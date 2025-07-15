from curl_cffi import requests
from time import sleep

API_URL = "https://api.captchasolver.ai/api/solve"

def get_token(roblox_session: requests.Session, blob, proxy):
    SOLVER_KEY = "bd1fe828b24d54596dcc7b73a25c7900648d8cbb3aa587f81d551f309de3537b"
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

        response = session.post(f"https://{API_URL}/createTask", json=payload, timeout=120).json()
        task_id = response.get("task_id")

        if task_id is None:
            raise ValueError(f'Failed to get taskId, reason: {response["error"]}')

        counter = 0

        while counter < 60:
            sleep(1)

            solution = session.get(f"https://{API_URL}/getTaskResult/{task_id}").json()
            if solution["status"] == "success":
                return solution["result"]["solution"]

            elif solution["status"] == "failure":
                return None

            counter += 1

        return None
    except Exception as e:
        print(e)
        return None