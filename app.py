from typing         import Any, Dict, Optional

from fastapi        import FastAPI, Header, HTTPException
from pydantic       import BaseModel
from json           import dumps
from datetime       import datetime, timezone
from time           import sleep
from threading      import Thread
from redis          import Redis

from src.api.tasks      import celery_app, solve
from src                import key_service
from src.utils.logger   import logger

app = FastAPI()

STAFF_TOKEN: str =       "cai/admin/staff#7e1bcd88-6304-4f9f-9df9-52d642399d97"
SB_TOKEN: str =          "sb/reseller/tool#370ef922-5124-42dc-83c8-6e574f8fa403"
UFC_TOKEN: str =         "ufc/reseller/solver#440c888c-dc32-43a0-9b56-7c8813af3bc4"
STATS_TOKEN: str =       "data/key/stats#0e3eae2a-ec61-4fe0-87f2-4476d159d197"
RESELLER_KEY: str =      "UFCR-461C8A462B8C4726A20EDFE367BFA8C81747616826"
COIN_MULTIPLIER: int =   1666.7


class TaskOutput(BaseModel):
    task_id:    str
    status:     str
    result:     Optional[Dict[str, Any]]

class ExtraTaskData(BaseModel):
    blob:               Optional[str]
    accept_language:    Optional[str]
    cookies:            Optional[Dict[str, str]]

class TaskInformation(BaseModel):
    type:       str
    extraData:  Optional[ExtraTaskData]
    site_url:   str
    action:     str
    proxy:      str

class TaskInput(BaseModel):
    key:    str
    task:   TaskInformation


class NewKey(BaseModel):
    bought: float

class TopUp(BaseModel):
    bought: float
    key:    str

class KeyAuth(BaseModel):
    key: str


def role_from_user_agent(user_agent: Optional[str]) -> Optional[str]:
    if not user_agent:
        return None
    if user_agent == STAFF_TOKEN:
        return "staff"
    if user_agent == SB_TOKEN:
        return "sb"
    if user_agent == UFC_TOKEN:
        return "ufc"
    if user_agent == STATS_TOKEN:
        return "stats"
    return "unknown"


def task_exists(task_id: str) -> bool:
    # fuck you bitch
    result = celery_app.AsyncResult(task_id)
    if result.state and result.state != "PENDING":
        return True
    backend = getattr(celery_app, "backend", None)
    try:
        if backend is not None and hasattr(backend, "get_task_meta"):
            meta = backend.get_task_meta(task_id)
            if meta and (
                meta.get("status")
                or meta.get("state")
                or meta.get("result") is not None
                or meta.get("traceback") is not None
            ):
                return True
    except Exception:
        pass
    # kill myself while at it
    try:
        insp = celery_app.control.inspect()
        if insp is None:
            return False
        for fn in (insp.active, insp.reserved, insp.scheduled):
            listing = fn() or {}
            for tasks in listing.values():
                for t in tasks:
                    tid = (
                        t.get("id")
                        or t.get("task_id")
                        or (t.get("request") or {}).get("id")
                        or (t.get("headers") or {}).get("id")
                    )
                    if tid == task_id:
                        return True
    except Exception:
        pass
    return False


@app.post("/createTask", response_model=TaskOutput)
def create_task(data: TaskInput) -> TaskOutput:
    extra = data.task.extraData or {}
    task = solve.delay(
        accept_lang=    extra.accept_language   or None,
        cookies=        extra.cookies           or None,
        blob=           extra.blob              or None,
        site_url=       data.task.site_url,
        action=         data.task.action,
        proxy=          data.task.proxy,
        type=           data.task.type,
        key=            data.key,
    )
    logger.info(f"<{task.id}> Created successfully.")
    return TaskOutput(task_id=task.id, status="created", result=None)


@app.get("/getTaskResult/{task_id}", response_model=TaskOutput)
def get_task_result(task_id: str) -> TaskOutput:
    if not task_exists(task_id):
        raise HTTPException(status_code=404, detail="task not found")
    
    result = celery_app.AsyncResult(task_id)
    status_map = {"PENDING": "pending", "SUCCESS": "success", "FAILURE": "failure"}
    status = status_map.get(result.state, result.state)
    output_result: Optional[Dict[str, Any]] = None

    if result.state == "SUCCESS":
        output_result = result.result if isinstance(result.result, dict) else {"result": result.result}

    elif result.state == "FAILURE":
        info = getattr(result, "info", None)
        output_result = info if isinstance(info, dict) else {"error": str(info)}

    return TaskOutput(task_id=result.id, status=status, result=output_result)


@app.post("/admin/generate")
def generate_key(data: NewKey, user_agent: Optional[str] = Header(None)):
    role = role_from_user_agent(user_agent)
    if role is None:
        return "?"
    
    if role == "staff":
        try:
            bought = data.bought * COIN_MULTIPLIER
            key = key_service.generate_new_key(bought, prefix="CS")
            return {"key": key, "bought": bought, "error": None}
        except Exception as e:
            return {"key": None, "bought": None, "error": str(e)}
        
    if role == "sb":
        return {"error": "NOT IMPLEMENTED"}
    
    if role == "ufc":
        try:
            bought = data.bought * COIN_MULTIPLIER
            if bought > key_service.get_balance(RESELLER_KEY):
                return {"key": None, "bought": None, "error": "You don't have enough balance, ask traili for refill."}
            
            key = key_service.generate_new_key(bought, "STRIKE")
            key_service.add_solved_request(RESELLER_KEY, bought)
            return {"key": key, "bought": bought, "error": None}
        
        except Exception as e:
            return {"key": None, "bought": None, "error": str(e)}
        
    return "?"


@app.post("/admin/key/stats")
def key_stats(data: KeyAuth, user_agent: Optional[str] = Header(None)):
    role = role_from_user_agent(user_agent)
    if role is None:
        return None
    if role != "stats":
        return "?"
    key = data.key
    if key is None:
        return {"error": "Invalid key"}
    keydata = key_service.key_manager.get_key_data(key)
    return dumps(keydata.stats)


@app.post("/getBalance")
def balance(data: KeyAuth):
    try:
        key = data.key
        keydata = key_service.key_manager.get_key_data(key)
        return {"balance": int(keydata.bought - keydata.solved)}
    except Exception as e:
        return {"error": str(e)}


@app.post("/admin/topup")
def admin_topup(data: TopUp, user_agent: Optional[str] = Header(None)):
    role = role_from_user_agent(user_agent)
    if role != "stats":
        return {"error": "?"}
    try:
        bought = data.bought * COIN_MULTIPLIER
        key_service.add_balance(data.key, bought)
        keydata = key_service.key_manager.get_key_data(data.key)
        return {"key": data.key, "balance": int(keydata.bought - keydata.solved), "error": None}
    except Exception as e:
        return {"key": None, "bought": None, "error": str(e)}


logger.info("API running on 'api.captchasolver.ai' port 80/443")
