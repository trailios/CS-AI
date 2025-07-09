from typing import Union, Dict, Any, Optional
from pydantic import BaseModel
from fastapi import FastAPI
from uuid import UUID
from src.api.tasks import solve, celery_app
from collections import deque
from datetime import datetime, timedelta
from threading import Thread
import time
import logging

app = FastAPI()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("task-stats")

# History of timestamps
task_creation_times = deque()
task_resolution_times = deque()

# Models
class TaskOutput(BaseModel):
    task_id: str
    status: str
    result: Union[str, Dict[str, Any], None]

class TaskInformation(BaseModel):
    type: str
    extraData: Optional[Dict[str, Any]]
    site_url: str
    action: str
    proxy: str

class TaskInput(BaseModel):
    key: str
    task: TaskInformation

@app.post("/createTask")
def create_task(data: TaskInput) -> TaskOutput:
    task = solve.delay(
        type=data.task.type,
        blob=data.task.extraData.get("data[blob]", None) if data.task.extraData else None,
        site_url=data.task.site_url,
        action=data.task.action,
        proxy=data.task.proxy,
        key=data.key
    )

    task_creation_times.append(datetime.utcnow())
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
        task_resolution_times.append(datetime.utcnow())

    elif result.state == "FAILURE":
        output_result = str(result.info)
        task_resolution_times.append(datetime.utcnow())

    return TaskOutput(
        task_id=result.id,
        status=status,
        result=output_result
    )

def log_task_rates():
    interval = 1

    while True:
        now = datetime.utcnow()
        one_minute_ago = now - timedelta(minutes=1)

        created_last_minute = [t for t in task_creation_times if t > one_minute_ago]
        resolved_last_minute = [t for t in task_resolution_times if t > one_minute_ago]

        created_rate = len(created_last_minute) / 60
        resolved_rate = len(resolved_last_minute) / 60

        logger.info(f"Task creation rate: {created_rate:.2f}/s | Resolved rate: {resolved_rate:.2f}/s\r")

        while task_creation_times and task_creation_times[0] <= one_minute_ago:
            task_creation_times.popleft()
        while task_resolution_times and task_resolution_times[0] <= one_minute_ago:
            task_resolution_times.popleft()

        time.sleep(interval)

Thread(target=log_task_rates, daemon=True).start()
