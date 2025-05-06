import os
from typing import Optional
from pydantic import BaseModel
from redis import StrictRedis

from ics_components.common import CoderRegistry as CoderRegistryInterface
from ics_models import Coder, Task as TaskBase, TaskUpdate as TaskUpdateBase

redis_host = os.getenv('REDIS_HOST') or 'localhost'
redis_store = StrictRedis(host=redis_host, port=6379, db=0, decode_responses=True)

class TaskInstructions(BaseModel):
    text: str = 'Antworte nur mit 0 oder 1 ob folgendes korrekt ist: "$VALUE"'
    @staticmethod
    def description() -> str:
        return "HU-LLM unterstützt außer dem Eingabetext keine Parameter. Gib den Anfragtext hier ein. $VALUE wird gegen den Wert ersetzt, der zu codieren ist. Das Ergebnis wird versucht in eine Zahl umzuwandeln."

class Task(TaskBase):
    instructions: Optional[TaskInstructions] = None

class TaskUpdate(TaskUpdateBase):
    instructions: Optional[TaskInstructions] = None

class CoderRegistry(CoderRegistryInterface):
    def list_coders(self) -> list[Coder]:
        coders : list[Coder] = []
        for key in redis_store.keys('instructions:*'):
            coders.append(
                Coder(
                    id = key.replace('instructions:', ''),
                    label = key # TODO
                )
            )
        return coders

    def delete_coder(self, coder_id: str) -> None:
        redis_store.delete('instructions:' + coder_id)
