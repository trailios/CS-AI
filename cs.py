from curl_cffi import requests
from time import sleep
from src.utils.logger import logger

API_URL = "https://api.captchasolver.ai"

def get_token(roblox_session: requests.Session, blob, proxy):
    SOLVER_KEY = ""
    try:
        if "http://" not in proxy:
            proxy = "http://" + proxy
        session = requests.Session()


        payload = {
            "key": SOLVER_KEY,
            "task": {
                "type": "FunCaptcha",
                "extraData": {
                    "blob": blob
                },
                "site_url": "https://www.roblox.com",
                "action": "roblox_login",
                "proxy": proxy
            }
        }

        response = session.post(f"{API_URL}/createTask", json=payload, timeout=120).json()
        logger.info(f"Response from createTask: {response}")
        task_id = response.get("task_id")

        if task_id is None:
            raise ValueError(f'Failed to get taskId, reason: {response["error"]}')

        counter = 0

        while counter < 60:
            sleep(1)

            solution = session.get(f"{API_URL}/getTaskResult/{task_id}").json()
            if solution["status"] == "success":
                logger.info(f"Solution found: {solution["result"]["solution"]}")
                return solution["result"]["solution"]

            elif solution["status"] == "failure":
                logger.error(f"Task failed: {solution["info"]}")
                return None

            counter += 1

        logger.warning("Task timed out.")
        return None
    except Exception as e:
        logger.error(f"Error in get_token: {e}")
        return None