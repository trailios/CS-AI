from curl_cffi import requests
from time import sleep

API_URL = "api.captchasolver.ai"

def get_token(roblox_session: requests.Session, blob, proxy):
    SOLVER_KEY = "LMAOADMIN-85FFD879E19840ABA927068599A48AF61748819857"
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
        print(response)
        task_id = response.get("task_id")

        if task_id is None:
            raise ValueError(f'Failed to get taskId, reason: {response["error"]}')

        counter = 0

        while counter < 60:
            sleep(1)

            solution = session.get(f"{API_URL}/getTaskResult/{task_id}").json()
            if solution["status"] == "success":
                return solution["result"]["solution"]

            elif solution["status"] == "failure":
                return None

            counter += 1

        return None
    except Exception as e:
        print(e)
        return None