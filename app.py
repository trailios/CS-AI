from typing         import Union, Dict, Any, Optional
from fastapi        import FastAPI, Header
from pydantic       import BaseModel

from src.api.tasks  import solve, celery_app
from src            import key_service

app = FastAPI()

class TaskOutput(BaseModel):
    task_id: str
    status:  str
    result:  Optional[Dict[str, Any]]

class TaskInformation(BaseModel):
    type:       str
    extraData:  Optional[Dict[str, Any]]
    site_url:   str
    action:     str
    proxy:      str

class TaskInput(BaseModel):
    key:    str
    task:   TaskInformation

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
        output_result = {"error": str(result.info)}

    return TaskOutput(
        task_id=result.id,
        status=status,
        result=output_result
    )

@app.post("/admin/generate")
def generate_key(data: dict, user_agent: str = Header(None)):
    if user_agent == None:
        return None
    
    elif user_agent == "cai/admin/staff#7e1bcd88-6304-4f9f-9df9-52d642399d97":
        bought = data.get("bought", 0.1) * 1000

        key = key_service.generate_new_key(bought, prefix="CS")

        return {
            "key": key,
            "bought": bought
        }

    elif user_agent == "sb/reseller/tool#370ef922-5124-42dc-83c8-6e574f8fa403":
        ... #EXTRACT FROM THEIR OWN KEY
    
    elif user_agent == "ufc/reseller/solver#440c888c-dc32-43a0-9b56-7c8813af3bc4":
        bought = data.get("bought", 0.05) * 1000



    return None

    ## add more if needed