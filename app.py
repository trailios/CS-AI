from typing         import Union, Dict, Any, Optional
from fastapi        import FastAPI, Header
from json           import loads, dumps
from pydantic       import BaseModel

from src.api.tasks  import solve, celery_app
from src            import key_service
from src.utils.logger import logger

app = FastAPI()

class TaskOutput(BaseModel):
    task_id: str
    status:  str
    result:  Optional[Any]
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
        blob=data.task.extraData.get("blob", None) if data.task.extraData else None,
        accept_lang=data.task.extraData.get("accept_language") if data.task.extraData else None,
        site_url=data.task.site_url,
        action=data.task.action,
        proxy=data.task.proxy,
        key=data.key
    )

    logger.info(
        f"<{task.id}> Created successfully."
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
    output_result = {}

    if result.state == "SUCCESS":
        output_result = result.result

    elif result.state == "FAILURE":
        output_result = result.info

    return TaskOutput(
        task_id=result.id,
        status=status,
        result=output_result
    )


class CustomAPI1(BaseModel):
    bought: float

class CustomAPI2(BaseModel):
    bought: float
    key: str

class KeyAuth(BaseModel):
    key: str

@app.post("/admin/generate")
def generate_key(data: CustomAPI1, user_agent: str = Header(None)):
    print(user_agent)
    if not user_agent:
        return "?"
    
    elif user_agent == "cai/admin/staff#7e1bcd88-6304-4f9f-9df9-52d642399d97":
        try:
            bought = data.bought * 1666.7

            key = key_service.generate_new_key(bought, prefix="CS")

            return {
                "key": key,
                "bought": bought,
                "error": None
            }
        
        except Exception as e:
            return {
                "key": None,
                "bought": None,
                "error": str(e)
            }

    elif user_agent == "sb/reseller/tool#370ef922-5124-42dc-83c8-6e574f8fa403":
        return {"error": "NOT IMPLEMENTED"}
    
    elif user_agent == "ufc/reseller/solver#440c888c-dc32-43a0-9b56-7c8813af3bc4":
        try:
            bought = data.get("bought",0) * 1666.7

            if bought > key_service.get_balance("UFCR-461C8A462B8C4726A20EDFE367BFA8C81747616826"):
                return {
                    "key": None,
                    "bought": None,
                    "error": "You don't have enough balance, ask traili for refill."
                }
            

            key = key_service.generate_new_key(bought, "STRIKE")
            key_service.add_solved_request("UFCR-461C8A462B8C4726A20EDFE367BFA8C81747616826", bought)

            return {
                "key": key,
                "bought": bought,
                "error": None
            }

        except Exception as e:
            return {
                "key": None,
                "bought": None,
                "error": str(e)
            }


    return "?"

    ## add more if needed

@app.post("/admin/key/stats")
def key_stats(data: KeyAuth, user_agent: str = Header(None)):
    if user_agent == None:
        return None
    
    elif user_agent == "data/key/stats#0e3eae2a-ec61-4fe0-87f2-4476d159d197":
        key = data.key

        if key == None:
            return {
                "error": "Invalid key"
            }

        keydata = key_service.key_manager.get_key_data(key)

        return dumps(keydata.stats)


    return "?"


@app.post("/getBalance")
def balance(data: KeyAuth):
    try:
        key = data.key
        keydata = key_service.key_manager.get_key_data(key)

        return {
            "balance": int(keydata.bought - keydata.solved)
        }

    except Exception as e:
        return {
            "error": str(e)
        }
    
@app.post("/admin/topup")
def admin_topup(data: CustomAPI2, user_agent: str = Header(None)):
    if user_agent != "data/key/stats#0e3eae2a-ec61-4fe0-87f2-4476d159d197":
        return {"error": "?"}
    
    try:
        bought = data.bought * 1666.7
        key_service.add_balance(data.key, bought)
        keydata = key_service.key_manager.get_key_data(data.key)
    
        return {
            "key": data.key,
            "balance": int(keydata.bought - keydata.solved),
            "error": None
        }
    
    except Exception as e:
        return {
            "key": None,
            "bought": None,
            "error": str(e)
        }
    
logger.info("API running on 'api.captchasolver.ai' port 80/443")