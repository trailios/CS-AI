from fastapi    import FastAPI
from pydantic   import BaseModel
from uuid       import UUID

from src.api.tasks import solve, celery_app

app = FastAPI()

class TaskInput(BaseModel):
    task_data: str

@app.post("/createTask")
def create_task(data: TaskInput):
    task = solve.delay(data.task_data)
    return {"task_id": task.id}

@app.get("/getTaskResult/{task_id}")
def get_task_result(task_id: str):
    result = celery_app.AsyncResult(task_id)
    if result.state == "PENDING":
        return {"status": "pending", "result": None}
    
    elif result.state == "SUCCESS":
        return {"status": "completed", "result": result.result}
    
    elif result.state == "FAILURE":
        return {"status": "failed", "result": str(result.result)}
    
    else:
        return {"status": result.state.lower(), "result": None}