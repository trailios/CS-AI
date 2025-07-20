
from typing     import Dict, Any
from celery     import Celery
from logging    import getLogger

from src                                import proxyHelper, key_service
from src.helpers.ClassificationHelper   import XEvilClient
from src.browser.fingerprint            import BDA
from src.arkose.challenge               import Challenge
from src.utils.utils                    import Utils
from src.utils.presets                  import Preset
from src.arkose.game                    import Game

import random

for logger_name in [
    "celery",
    "celery.task",
    "kombu",
    "amqp",
]:
    getLogger(logger_name).disabled = True

celery_app = Celery(
    "src.api.tasks",
    broker="redis://149.50.108.43:6379/0",
    backend="redis://149.50.108.43:6379/0",
)


celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    worker_hijack_root_logger=False,
)


@celery_app.task
def solve(type: str, **kwargs) -> str:
    try:
        key: str = kwargs.get("key", None)

        if key == None:
            return {
                "error": "Key is missing."
            }
        
        if not key_service.key_exists(key):
            return {
                "error": "Key does not exists"
            }
        
        keydata = key_service.key_manager.get_key_data(key)

        if (keydata.bought - keydata.solved) < 1:
            return {
                "error": "Key does not have any balance, refill at None"
            }
        
    except Exception as e:
        return {
            "error": "Couldnt process the key. (To many global threads?)",
            "solution": None
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

        browser["language"] = info["lang"]

        version = 139

        headers = {
    'accept': '*/*',
    'accept-language': 'en,de-DE;q=0.9,de;q=0.8,en-US;q=0.7',
    'cache-control': 'no-cache',
    'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'origin': 'https://www.roblox.com',
    'pragma': 'no-cache',
    'priority': 'u=1, i',
    'referer': 'https://www.roblox.com/',
    'sec-ch-ua': f'"Not/A)Brand";v="99", "Google Chrome";v="{version}", "Chromium";v="{version}"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-site',
    'sec-gpc': '1',
    'user-agent': f'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{version}.0.0.0 Safari/537.36',
    'x-ark-esync-value': Utils.short_esync(),
}

        bda = BDA(proxy, action, headers['user-agent'], headers['accept-language'])
        bda.update_fingerprint()

        settings["bda"] = bda.encryptedfingerprint

        try:
            challenge: Challenge = Challenge(headers, proxy, settings, browser)
            challenge._pre_load()
            challenge.gt2()


            challenge.session.headers_update({
                'accept': '*/*',
                'accept-encoding': "gzip, deflate, br, zstd",
                'accept-language': 'en,de-DE;q=0.9,de;q=0.8,en-US;q=0.7',
                'cache-control': 'no-cache',
                'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
                'origin': settings["service_url"],
                'pragma': 'no-cache',
                'priority': 'u=1, i',
                'referer': f'{settings["service_url"]}/v2/3.5.0/enforcement.df45d93b7883fed1e47dedac58c1d924.html',
                'sec-ch-ua': f'"Not/A)Brand";v="99", "Google Chrome";v="{version}", "Chromium";v="{version}"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Windows"',
                'sec-fetch-dest': 'empty',
                'sec-fetch-mode': 'cors',
                'sec-fetch-site': 'same-origin',
                'sec-gpc': '1',
                'user-agent': f'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{version}.0.0.0 Safari/537.36',
                'x-newrelic-timestamp': Utils.x_ark_esync(),
                'x-requested-with': 'XMLHttpRequest',
            })

            if "sup" not in challenge.full_token:
                game: Game = Game(challenge)
                game._enforcement_callback()
                game._init_load()
                game.gfct()
                game._user_callback()

                # what if i was actually gay?

                game.get_images()
                game.parse_images()

                client = XEvilClient.with_defaults("glcOgEAPEkT8JxakGyfneCeT9BsYUav8") 

                solved = False

                guess = []

                for img in game._imgs:
                    answer = client.solve_image(img, game.variant, game.diff)

                    guess.append(
                        {
                            "index": answer
                        }
                    )

                    solved = game.put_answer(guess)

                    if solved:
                        key_service.add_solved_request(key)
                        key_service.add_stat(
                            key,
                            action,
                            "success",
                            0.0006
                        )
                        return dict({"solution": challenge.full_token, "game_info": {"waves": game.waves, "variant": game.variant}})

                if solved == False:
                    key_service.increment_failed(key)
                    key_service.add_total_request(key)
                    key_service.add_stat(
                        key,
                        action,
                        "failed",
                        0.0
                    )
                    return dict({"error": "Failed to solve captcha.", "solution": None, "game_info": {"waves": game.waves, "variant": game.variant}})

                return dict({"error": "Image solving not implemented", "solution": None})

            key_service.add_stat(
                key,
                action,
                "success",
                0.0006
            )
            key_service.add_solved_request(key)
            return dict({"solution": challenge.full_token})
        except Exception as e:
            return dict({"error": str(e), "solution": None})
