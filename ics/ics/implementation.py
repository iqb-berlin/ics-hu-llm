import os
from typing import Optional
from pydantic import BaseModel, Field
from redis import StrictRedis

from ics_components.common import CoderRegistry as CoderRegistryInterface
from ics_models import Coder, Task as TaskBase, TaskUpdate as TaskUpdateBase

redis_host = os.getenv('REDIS_HOST') or 'localhost'
redis_store = StrictRedis(host=redis_host, port=6379, db=0, decode_responses=True)

class TaskInstructions(BaseModel):
    text: str = Field(default = 'Antworte nur mit 0 oder 1 ob folgendes korrekt ist: "$VALUE"', description = "Promttext")
    @staticmethod
    def description() -> str:
        return ("<a href='https://llm1-compute.cms.hu-berlin.de/' target='_blank'>HU-LLM</a> wird nur mit einem Promt bedient.<br>"
                "Promt zur Auswertung hier eingeben (Der Ausdruck <i>$VALUE</i> wird gegen den Wert ersetzt, der zu codieren ist.<br>"
                "Das Promt sollte eine Aufforderung enthalten, nur mit 0 oder 1 zu antworten, denn die Antwort wird immer als Zahl"
                " ( = Code)interpretiert.</a>")

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
