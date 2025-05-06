import os
import uuid
from typing import List

from gradio_client import Client
from redis import StrictRedis

from ics_components.common import print_in_worker
from ics_components.common.models import TrainingResult
from ics.implementation import TaskInstructions
from ics_models import Response, Code

client = Client("https://llm1-compute.cms.hu-berlin.de/")
redis_host = os.getenv('REDIS_HOST') or 'localhost'
redis_store = StrictRedis(host=redis_host, port=6379, db=0, decode_responses=True)

def code(model_id: str, input_data: List[Response]) -> List[Response]:
    instructions = restore_instructions(model_id)
    for row in input_data:
        print_in_worker(row)
        result = client.predict(
            message = instructions.text.replace('$VALUE', row.value),
            api_name = "/chat"
        )
        print_in_worker(result)
        row.codes = [Code(id = int(result))]
        row.status = 'CODE_SELECTION_PENDING'
    return input_data

def train(task_label: str, instructions: TaskInstructions, input_data: List[Response]) -> TrainingResult:
    coder_id = str(uuid.uuid4())
    store_instructions(coder_id, instructions)
    return TrainingResult(coderId = coder_id, msg = "okay")

def store_instructions(coder_id: str, instructions: TaskInstructions):
    redis_store.set('instructions:' + coder_id, instructions.model_dump_json(by_alias = True))

def restore_instructions(coder_id: str) -> TaskInstructions:
    return TaskInstructions.model_validate_json(redis_store.get('instructions:' + coder_id))
