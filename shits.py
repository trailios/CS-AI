import requests
from src.utils.logger import logger

r = requests.post(
    "http://127.0.0.1/admin/generate",
    headers={
        "user-agent": "cai/admin/staff#7e1bcd88-6304-4f9f-9df9-52d642399d97"
    },
    json={
        "bought": 1000
    }
)
print(r.text)
rjson = r.json()
logger.info(f'{rjson["key"]} {rjson["bought"]}')

r = requests.post(
    "http://localhost/admin/generate",
    headers={
        "user-agent": "cai/admin/staff#7e1bcd88-6304-4f9f-9df9-52d642399d97"
    },
    json={
        "bought": 999999
    }
)

rjson = r.text
logger.info(
    rjson
)
logger.info(f'{rjson["key"]} {rjson["bought"]}')

r2 = requests.post(
    "https://api.captchasolver.ai/admin/key/stats",
    headers={
        "user-agent": "data/key/stats#0e3eae2a-ec61-4fe0-87f2-4476d159d197"
    },
    json={
        "key": rjson["key"]
    }
)

logger.info(r2.json())