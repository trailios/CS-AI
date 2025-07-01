from fastapi    import FastAPI
from pydantic   import BaseModel
from uuid       import UUID
from typing     import Union, Dict, Any

import json

from src.api.tasks import solve, celery_app

app = FastAPI()

class TaskOutput(BaseModel):
    task_id: Union[str, UUID]
    status: Union[str, None] = None
    result: Union[Dict[str, Any], str, None] = None

class TaskInformation(BaseModel):
    type: str
    extraData: Union[Dict[str, Any], None] = None 
    site_url: Union[str, None] = None
    action: str
    proxy: Union[str, None] = None

class Task(BaseModel):
    key: str
    task: TaskInformation

@app.post("/createTask")
def create_task(data: Task) -> TaskOutput:
    task = solve.delay(
        type=data.task.type,
        blob=data.task.extraData.get("data[blob]", None) if data.task.extraData else None,
        site_url=data.task.site_url,
        action=data.task.action,
        proxy=data.task.proxy,
        key=data.key
    )

    return TaskOutput(
        task_id=task.id,
        status="created",
        result=None
    )

@app.get("/getTaskResult/{task_id}")
def get_task_result(task_id: str) -> TaskOutput:
    result = celery_app.AsyncResult(task_id)

    status_map = {
        "PENDING": "pending",
        "SUCCESS": "success",
        "FAILURE": "failure",
    }

    status = status_map.get(result.state, result.state)
    output_result = None

    if result.state == "SUCCESS":
        output_result = str(result.result)
    elif result.state == "FAILURE":
        output_result = str(result.info) if hasattr(result.info, 'args') else str(result.info)

    return TaskOutput(
        task_id=result.id,
        status=status,
        result=output_result
    )