import os
import uuid
from typing import List, Callable

from gradio_client import Client
from redis import StrictRedis

from ics_components.common.models import TrainingResult
from ics.implementation import TaskInstructions, CoderRegistry
from ics_models import Response, Code

redis_host = os.getenv('REDIS_HOST') or 'localhost'
redis_store = StrictRedis(host=redis_host, port=6379, db=0, decode_responses=True)

def connect() -> Client | None:
    try:
        return Client("https://llm1-compute.cms.hu-berlin.de/")
    except Exception as e:
        print(e)
        raise Exception('Could not connect to HU LLM (too many requests?).')

def get_code_from_answer(answer: str) -> List[Code] | str:
    try:
        probab = float(answer)
        predicted_code = int(round(probab))
    except ValueError as error:
        return getattr(error, 'message', repr(error))
    if predicted_code == 0 or predicted_code == 1:
        if predicted_code == 1:
            not_predicted = 0
            not_probab = 1 - probab
        else:
            not_predicted = 1
            not_probab = probab
            probab = 1 - not_probab
        return [
            Code(id = predicted_code, parameter = str(probab)),
            Code(id = not_predicted, parameter = str(not_probab))
        ]
    return [Code(id = predicted_code)]

def code(model_id: str, input_data: List[Response], reporter: Callable[[str, bool], None]) -> List[Response]:
    client = connect()
    instructions = restore_instructions(model_id)
    items = len(input_data)
    item_nr = 0
    for row in input_data:
        result = client.predict(
            instructions.text.replace('$VALUE', row.value),
            api_name = "/chat"
        )
        codes = get_code_from_answer(result)
        if type(codes) == 'string':
            row.status = 'CODING_ERROR'
            reporter(f'Result is not usable: {codes}', True)
        else :
            row.codes = codes
            row.status = 'CODE_SELECTION_PENDING'
        item_nr += 1
        if item_nr % 5 == 0:
            reporter(f'{item_nr}/{items}', False)
    return input_data

def train(
    task_label: str,
    instructions: TaskInstructions,
    input_data: List[Response],
    reporter: Callable[[str, bool], None]
) -> TrainingResult:
    coder_id = str(uuid.uuid4())
    store_instructions(coder_id, instructions)
    return TrainingResult(coderId = coder_id, msg = "okay")

def store_instructions(coder_id: str, instructions: TaskInstructions):
    redis_store.set('instructions:' + coder_id, instructions.model_dump_json(by_alias = True))

def restore_instructions(coder_id: str) -> TaskInstructions:
    return TaskInstructions.model_validate_json(redis_store.get('instructions:' + coder_id))

def coder_exists(coder_id: str) -> bool:
    return redis_store.exists('instructions:' + coder_id)
