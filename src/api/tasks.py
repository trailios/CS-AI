
from os             import getenv, listdir, makedirs, name as os_name
from typing         import Dict, Any
from logging        import getLogger
from celery         import Celery
from itertools      import cycle
from uuid           import uuid4
from multiprocessing import cpu_count
from threading      import local

from src                                import proxyHelper, key_service, logger
from src.utils.parser                   import get_vm_key, version_info
from src.helpers.ClassificationHelper   import XEvilClient
from src.arkose.challenge               import Challenge
from src.utils.presets                  import Preset
from src.utils.utils                    import Utils
from src.arkose.game                    import Game
from src.browser.fingerprint            import BDA
import time


# for logger_name in [
#     "celery",
#     "celery.task",
#     "kombu",
#     "amqp",
# ]:
#     getLogger(logger_name).disabled = True

BROKER_URL = getenv("CELERY_BROKER_URL", "redis://127.0.0.1:6379/0")
BACKEND_URL = getenv("CELERY_RESULT_BACKEND", BROKER_URL)

DEFAULT_POOL = getenv("CELERY_POOL", "threads" if os_name == "nt" else "prefork")


def _default_concurrency(pool: str) -> int:
    env_value = getenv("CELERY_WORKER_CONCURRENCY")
    if env_value is not None:
        try:
            return max(1, int(env_value))
        except ValueError:
            pass

    cores = cpu_count() or 1
    if pool == "threads":
        return max(4, min(64, cores * 4))
    return max(2, min(32, cores * 2))


CELERY_CONCURRENCY = _default_concurrency(DEFAULT_POOL)

celery_app = Celery(
    "src.api.tasks",
    broker=BROKER_URL,
    backend=BACKEND_URL,
)

_fingerprint_files = listdir("db/safari")
_thread_local = local()


def _get_bda_handler() -> BDA:
    handler = getattr(_thread_local, "bda_handler", None)
    if handler is None:
        handler = BDA(
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
            cycle(_fingerprint_files),
        )
        _thread_local.bda_handler = handler
    return handler

# static for now the ua
# nigger on your fp shit you still using the next() WHICH IS GOING TO SWITCH TO NEXT FP

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    worker_hijack_root_logger=False,
    worker_pool=DEFAULT_POOL,
    worker_concurrency=CELERY_CONCURRENCY,
    broker_connection_retry_on_startup=True,
)


@celery_app.task
def solve(type: str, **kwargs) -> str:
    try:
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
            accept_lang = "de-DE,de;q=0.7" #kwargs.get("accept_lang", "de-DE,de;q=0.7") 
            
            site_url = kwargs.get("site_url")
            action = kwargs.get("action")
            cookies = kwargs.get("cookies", None)
            try:
                proxy = proxyHelper.parse(kwargs.get("proxy", None))
            except Exception as e:
                return dict({"error": str(e), "solution": None})
                

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
            browser["cookies"] = cookies

            version = 142


            # headers = {
            #     "ark-build-id": "4e0e9770-e252-4758-8751-980278702a08", 
            #     'sec-ch-ua-platform': '"Windows"',
            #     'x-ark-esync-value': str(Utils.short_esync()),
            #     'user-agent': f'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36',
            #     'sec-ch-ua': f'"Chromium";v="142", "Google Chrome";v="142", "Not_A Brand";v="99"',
            #     'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
            #     'sec-ch-ua-mobile': '?0',
            #     'accept': '*/*',
            #     'origin': site_url, 
            #     'sec-fetch-site': 'same-site',
            #     'sec-fetch-mode': 'cors',
            #     'sec-fetch-dest': 'empty', 
            #     'referer': site_url + "/", 
            #     "accept-encoding": "gzip, deflate, br, zstd",
            #     'accept-language': accept_lang,
            #     'priority': 'u=1, i', 
            # }

            headers = {
                "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
                "x-ark-esync-value": str(int(time.time() / 21600) * 21600),# not sure if it changed or not, but many solver have it differnet..??
                "accept": "*/*",
                "sec-fetch-site": "same-site",
                "accept-language": "de-DE,de;q=0.9",
                "accept-encoding": "gzip, deflate, br",
                "sec-fetch-mode": "cors",
                "origin": "https://www.roblox.com",
                "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.6 Safari/605.1.15",
                "ark-build-id": "df48e82b-5d6a-43b9-b50a-738e595c6ec0",
                "referer": "https://www.roblox.com/",
                "sec-fetch-dest": "empty",
            }

            vm_key = get_vm_key(info["surl"], info["pkey"])

            if not vm_key:
                raise Exception("Could not fetch VM key.")

            bda, fp = _get_bda_handler().update_fingerprint(
                proxy,
                action,
                accept_lang,
                vm_key,
                version_info(info["surl"], info["pkey"])[2]
            )

            settings["bda"] = bda

            try:
                challenge: Challenge = Challenge(headers, proxy, settings, browser)
                challenge._pre_load()
                challenge.gt2()


                challenge.session.headers = {
                    'accept': '*/*',
                    'accept-encoding': "gzip, deflate, br, zstd",
                    'accept-language': accept_lang,
                    'cache-control': 'no-cache',
                    'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
                    'origin': settings["service_url"],
                    'pragma': 'no-cache',
                    'priority': 'u=1, i',
                    'referer': f'{settings["service_url"]}/v2/{challenge.version}/enforcement.{challenge.hash}.html',
                    'sec-ch-ua': f'"Not/A)Brand";v="8", "Google Chrome";v="{version}", "Chromium";v="{version}"',
                    'sec-ch-ua-mobile': '?0',
                    'sec-ch-ua-platform': '"Windows"',
                    'sec-fetch-dest': 'empty',
                    'sec-fetch-mode': 'cors',
                    'sec-fetch-site': 'same-origin',
                    'sec-gpc': '1',
                    'user-agent': f'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{version}.0.0.0 Safari/537.36',
                    'x-newrelic-timestamp': Utils.x_ark_esync(),
                    'x-requested-with': 'XMLHttpRequest',
                }

                if "sup" not in challenge.full_token:
                    game: Game = Game(challenge)
                    game._enforcement_callback()
                    game._init_load()
                    game.gfct()
                    game._user_callback()

                    print(f"waves: {game.waves} - vairant: {game.variant}")
                    makedirs(f"db/fps/{game.variant}/{game.waves}", exist_ok=True)

                    with open(f"db/fps/{game.variant}/{game.waves}/{uuid4()}.json", "w", encoding="utf-8") as f:
                        f.write(fp)

                    if game.waves >= 6:
                        return dict({"error": "Captcha was to difficult.", "solution": None})

                    game.get_images()
                    game.parse_images()

                    client = XEvilClient.with_defaults("MU8HyemZ70uQzjYNTubwxHRswOp9VhQn") 

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
                            
                            logger.success(f"Successfully solved: {challenge.session_token}")
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
                        logger.error(f"Failed to solved: {challenge.session_token}")
                        return dict({"error": "Failed to solve captcha.", "solution": None, "game_info": {"waves": game.waves, "variant": game.variant}})

                    return dict({"error": "Image solving not implemented", "solution": None})

                key_service.add_stat(
                    key,
                    action,
                    "success",
                    0.0006
                )
                key_service.add_solved_request(key)
                print(challenge.full_token.split("|")[0])
                with open(f"db/fps/sup/{uuid4()}.json", "w", encoding="utf-8") as f:
                    f.write(fp)
                return dict({"solution": challenge.full_token})
            
            except Exception as e:
                e = str(e)
                makedirs("db/fps/pow", exist_ok=True)
                if "POW" in e:
                    with open(f"db/fps/pow/{uuid4()}.json", "w", encoding="utf-8") as f:
                        f.write(fp)
                key_service.increment_failed(key)
                return dict({"error": str(e), "solution": None})
            
    except Exception as e:
        return dict({"error": str(e.with_traceback()), "solution": None})
    
