from flytekit.extend.backend.base_agent import AgentBase, AgentRegistry
from dataclasses import dataclass
import requests

@dataclass
class Metadata:
    # you can add any metadata you want, propeller will pass the metadata to the agent to get the job status.
    # For example, you can add the job_id to the metadata, and the agent will use the job_id to get the job status.
    # You could also add the s3 file path, and the agent can check if the file exists.
    job_id: str

class RayAgent(AgentBase):
    def __init__(self, task_type: str):
        # Each agent should have a unique task type. Agent service will use the task type to find the corresponding agent.
        super().__init__(task_type="ray")
        print("RayAgent")

    async def async_create(
        self,
        context: grpc.ServicerContext,
        output_prefix: str,
        task_template: TaskTemplate,
        inputs: typing.Optional[LiteralMap] = None,
    ) -> TaskCreateResponse:
        print(__name__)

        return CreateTaskResponse(resource_meta=json.dumps(asdict(Metadata(job_id=1))).encode("utf-8"))

    async def async_get(self, context: grpc.ServicerContext, resource_meta: bytes) -> TaskGetResponse:

        return GetTaskResponse(resource=Resource(state="SUCCEEDED"))

    async def async_delete(self, context: grpc.ServicerContext, resource_meta: bytes) -> TaskDeleteResponse:
        return DeleteTaskResponse()

# To register the custom agent
print("register!!!!!!!!!!!!!")
AgentRegistry.register(RayAgent())