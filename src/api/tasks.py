
from typing     import Dict, Any
from celery     import Celery


from src                                import proxyHelper, key_service
from src.fingerprint.bda.fingerprint    import returnBDA
from src.arkose.challenge               import Challenge
from src.utils.presets                  import Preset


celery_app = Celery(
    "src.api.tasks",
    broker="redis://144.76.218.98:6379/0",
    backend="redis://144.76.218.98:6379/0"
)

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    worker_prefetch_multiplier=1,
    task_acks_late=True,
)


@celery_app.task
def solve(type: str, **kwargs) -> str:
    key: str = kwargs.get("key", None)

    if key == None:
        return {
            "error": "Key is missing."
        }
    
    if not key_service.key_exists(key):
        return {
            "error": "Key does not exists on our database"
        }
    
    keydata = key_service.key_manager.get_key_data(key)
    if (keydata.bought - keydata.solved) < 1:
        return {
            "error": "Key does not have any balance, refill at None"
        }
        

    if type == "FunCaptcha":
        blob = kwargs.get("blob", None)
        site_url = kwargs.get("site_url")
        action = kwargs.get("action")
        proxy = proxyHelper.parse(kwargs.get("proxy", None))

        options, info = Preset.get_options(action)
        settings: Dict[str, Any] = {}
        browser:  Dict[str, Any] = {}


        settings["blob"] = blob
        settings["site"] = site_url
        settings["proxy"] = proxy
        settings["service_url"] = info["surl"]
        settings["cmode"] = info["cmode"]
        settings["public_key"] = info["pkey"]

        browser["bda"] = returnBDA(settings["proxy"], action, 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36')
        
        headers = {
    'accept': '*/*',
    'accept-language': 'en,de-DE;q=0.9,de;q=0.8,en-US;q=0.7',
    'cache-control': 'no-cache',
    'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'origin': 'https://www.roblox.com',
    'pragma': 'no-cache',
    'priority': 'u=1, i',
    'referer': 'https://www.roblox.com/',
    'sec-ch-ua': '"Not)A;Brand";v="8", "Chromium";v="138", "Brave";v="138"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-site',
    'sec-gpc': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36',
    'x-ark-esync-value': '1752602400',
}

        try:
            challenge: Challenge = Challenge(headers, proxy, settings, browser)
            challenge.gt2()

            print(challenge.full_token)

            return {"solution": challenge.full_token}
        except Exception as e:
            print(e)
            return {"error": str(e)}