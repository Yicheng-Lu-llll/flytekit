import json
import pickle
import typing
from dataclasses import dataclass
from typing import Optional


import flytekit
from flytekit.extend.backend.base_agent import AgentBase, AgentRegistry, convert_to_flyte_state
from flytekit.models.literals import LiteralMap
from flytekit.models.task import TaskTemplate


@dataclass
class Metadata:
    run_id: str


class RayAgent(AgentBase):
    def __init__(self):
        super().__init__(task_type="spark")

    async def async_create(
        self,
        context: grpc.ServicerContext,
        output_prefix: str,
        task_template: TaskTemplate,
        inputs: Optional[LiteralMap] = None,
    ) -> CreateTaskResponse:

        return CreateTaskResponse()

    async def async_get(self, context: grpc.ServicerContext, resource_meta: bytes) -> GetTaskResponse:

        return GetTaskResponse()

    async def async_delete(self, context: grpc.ServicerContext, resource_meta: bytes) -> DeleteTaskResponse:

        return DeleteTaskResponse()



AgentRegistry.register(RayAgent())