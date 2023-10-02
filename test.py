import ray
from flytekit import task, workflow
from flytekitplugins.ray import RayJobConfig, HeadNodeConfig, WorkerNodeConfig

@ray.remote
def f(x):
    return x * x

@task(
    task_config=RayJobConfig(
    address="0.0.0.0:8265",
    head_node_config=HeadNodeConfig(ray_start_params={"log-color": "True"}),
    worker_node_config=[WorkerNodeConfig(group_name="ray-group", replicas=1)],
    )
)
def ray_task() -> int:
    return 9 * 9

@workflow
def ray_workflow() -> int:
    return ray_task()

# pyflyte run /home/ubuntu/flyte/flytekit/test.py ray_workflow --version 10