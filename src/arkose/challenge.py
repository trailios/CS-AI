from typing import Dict, Optional, Any, Awaitable, Callable
from urllib import parse
from json import loads
from time import time
from random import random
from sys import platform
from threading import Thread, Event

import rnet
import asyncio

from src.helpers.SessionHelper import (
    HTTPError,
    ProxyError,
    HttpVersion,
    Session,
)
from src.utils.parser import version_info, get_vm_key
from src import internal_session
from src.helpers.ProxyHelper import Proxy

class V8Random:
    def __init__(self, seed=0xdeadbeefcafebabe):
        self.s = [seed, 0x7f3f7f3f7f3f7f3f, 0x6c33f7c36c33f7c3, 0x123456789abcdeff]

    def _rotl(self, x, k):
        return ((x << k) | (x >> (64 - k))) & 0xFFFFFFFFFFFFFFFF

    def next(self):
        s = self.s
        result = (self._rotl(s[0] + s[3], 23) + s[0]) & 0xFFFFFFFFFFFFFFFF
        t = (s[1] << 17) & 0xFFFFFFFFFFFFFFFF

        s[2] ^= s[0]
        s[3] ^= s[1]
        s[1] ^= s[2]
        s[0] ^= s[3]

        s[2] ^= t
        s[3] = self._rotl(s[3], 45)

        return result

    def random(self):
        u53 = self.next() >> 11
        return u53 * (1.0 / 9007199254740992.0)

randomness = V8Random()

def encode(input_str: str) -> str:
    safe_chars = set(
        b"!'()*-.0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ_abcdefghijklmnopqrstuvwxyz~"
    )

    hex_table = [f"%{i:02X}" for i in range(256)]

    result = []
    for ch in input_str:
        b = ord(ch)
        if b in safe_chars:
            result.append(chr(b))
        else:
            result.append(hex_table[b])

    return "".join(result)


class ProxyConnectionFailed(Exception):
    PREFIX = "CS-AI-ERR:"

    def __init__(self, message: str = "Proxy connection failed") -> None:
        full_message = f"{self.PREFIX} {message}"
        super().__init__(full_message)


class Http3NotSupported(Exception):
    PREFIX = "CS-AI-ERR:"

    def __init__(
        self,
        message: str = "Http3 is not supported by proxy provider",
    ) -> None:
        full_message = f"{self.PREFIX} {message}"
        super().__init__(full_message)


class Challenge:
    def __init__(
        self,
        Headers: Dict[str, str],
        Proxy: Proxy,
        Settings: Dict[str, str],
        BrowserData: Dict[str, str],
        HTTPVersion: Optional[int] = HttpVersion.V2_0,
        Impersonate: Optional[str] = "chrome136",
    ) -> None:
        if platform.startswith("win"):
            try:
                asyncio.set_event_loop_policy(
                    asyncio.WindowsSelectorEventLoopPolicy()
                )
            except Exception:
                pass

        self.loop: asyncio.AbstractEventLoop = asyncio.new_event_loop()
        self.loop_thread: Optional[Thread] = None
        self.loop_ready: Event = Event()
        self._start_background_loop()

        self.cookies: Dict[str, str] = {}
        self.settings: Dict[str, str] = Settings
        self.browser: Dict[str, Any] = BrowserData
        self.proxy: Any = Proxy

        self.session: Session = Session(
            proxy=self.proxy.__str__(),
            impersonate="safari260",
        )
        self.proxies = self._run_async(
            lambda: self._init_proxies(self.proxy)
        )
        self.rnet_client: rnet.Client = self._run_async(
            lambda: self._init_rnet_client(Headers, self.proxies)
        )
        self.session.headers = Headers

        self.base_url: str = Settings["service_url"]
        self.version, self.hash, self.cbid = version_info(
            Settings["service_url"],
            Settings["public_key"],
        )

        self.session_token: str = ""
        self.full_token: str = ""
        self.game_url: str = ""
        self.game_version: str = ""

    def _start_background_loop(self) -> None:
        if self.loop_thread and self.loop_thread.is_alive():
            return

        def _runner() -> None:
            if platform.startswith("win"):
                try:
                    asyncio.set_event_loop_policy(
                        asyncio.WindowsSelectorEventLoopPolicy()
                    )
                except Exception:
                    pass
            asyncio.set_event_loop(self.loop)
            self.loop_ready.set()
            self.loop.run_forever()

        self.loop_thread = Thread(target=_runner, daemon=True)
        self.loop_thread.start()
        self.loop_ready.wait(timeout=1)

    async def _init_proxies(self, proxy: Proxy) -> Any:
        return rnet.Proxy.all(proxy.__str__())

    async def _init_rnet_client(
        self,
        headers: Dict[str, str],
        proxies: Any,
    ) -> rnet.Client:
        return rnet.Client(
            emulation=rnet.Emulation.OkHttp4_9,
            proxies=[proxies],
            headers=headers,
            http2_only=True,
        )

    def _run_async(
        self,
        coro_or_factory: Callable[[], Awaitable[Any]] | Awaitable[Any],
    ) -> Any:
        async def runner() -> Any:
            if callable(coro_or_factory):
                coro = coro_or_factory()
            else:
                coro = coro_or_factory
            return await coro

        if (
            self.loop.is_closed()
            or not (self.loop_thread and self.loop_thread.is_alive())
            or not self.loop.is_running()
        ):
            self.loop = asyncio.new_event_loop()
            self.loop_ready = Event()
            self._start_background_loop()
        try:
            future = asyncio.run_coroutine_threadsafe(
                runner(),
                self.loop,
            )
            return future.result()
        except RuntimeError as exc:
            msg = str(exc).lower()
            if (
                "no running event loop" in msg
                or "no current event loop" in msg
                or "event loop is closed" in msg
            ):
                self._reset_loop()
                future = asyncio.run_coroutine_threadsafe(
                    runner(),
                    self.loop,
                )
                return future.result()
            raise

    def _reset_loop(self) -> None:
        try:
            if self.loop and not self.loop.is_closed():
                self.loop.call_soon_threadsafe(self.loop.stop)
        except Exception:
            pass

        if self.loop_thread and self.loop_thread.is_alive():
            self.loop_thread.join(timeout=1)

        self.loop = asyncio.new_event_loop()
        self.loop_thread = None
        self.loop_ready = Event()
        self._start_background_loop()

        self.proxies = self._run_async(
            lambda: self._init_proxies(self.proxy)
        )
        self.rnet_client = self._run_async(
            lambda: self._init_rnet_client(self.session.headers, self.proxies)
        )

    def _sync_rnet_cookies(self, *responses: Any) -> None:
        for response in responses:
            if not response:
                continue

            cookies = getattr(response, "cookies", None) or []
            for cookie in cookies:
                name = getattr(cookie, "name", None)
                value = getattr(cookie, "value", None)

                if not name:
                    continue

                cookie_kwargs = {}
                if getattr(cookie, "domain", None):
                    cookie_kwargs["domain"] = cookie.domain
                if getattr(cookie, "path", None):
                    cookie_kwargs["path"] = cookie.path

                self.session.cookies.set(name, value, **cookie_kwargs)
                self.cookies[name] = value

    def _pre_load(self) -> None:
        try:
            api_js_response = self._run_async(
                lambda: self.rnet_client.get(
                    f"{self.base_url}/v2/{self.version}/api.js"
                )
            )
            settings_response = self._run_async(
                lambda: self.rnet_client.get(
                    f"{self.base_url}/v2/{self.settings['public_key']}/settings"
                )
            )

            for resp in (api_js_response, settings_response):
                if resp:
                    resp.raise_for_status()

            self._sync_rnet_cookies(api_js_response, settings_response)

        except ProxyError as e:
            raise ProxyConnectionFailed(str(e)) from e

        except HTTPError:
            raise Http3NotSupported()

        except (rnet.ConnectionError, rnet.TimeoutError) as e:
            raise ProxyConnectionFailed(str(e)) from e

        except rnet.StatusError:
            raise Http3NotSupported()

        except Exception as e:
            raise Exception(
                "CS-AI-ERR: Failed to pre-load challenge because " + str(e)
            ) from e

    def _callback_sup(self) -> None:
        params = {
            "callback": "__jsonp_" + str(int(time() * 1000)),
            "category": "loaded",
            "action": "game loaded",
            "session_token": self.session_token,
            "data[public_key]": self.settings["public_key"],
            "data[site]": parse.quote(self.settings["site"]),
        }

        try:
            self.session.get(f"{self.base_url}/fc/a/", params=params)

        except ProxyError as e:
            raise ProxyConnectionFailed(str(e)) from e

        except HTTPError:
            raise Http3NotSupported()

        except Exception as e:
            raise Exception(
                "CS-AI-ERR: Failed to callback because " + str(e)
            ) from e

    def gt2(self) -> None:
        self._pre_load()
        payload = {
            "c": self.settings["bda"],
            "public_key": self.settings["public_key"],
            "site": self.settings["site"],
            "userbrowser": self.session.headers["user-agent"],
            "capi_version": "4.0.12",
            "capi_mode": "lightbox",
            "style_theme": "modal",
            "rnd": str(randomness.random()),
        }

        cookiestring = ""

        if self.settings["blob"]:
            payload["data[blob]"] = self.settings["blob"]

        if self.browser["cookies"]:
            for key, value in self.browser["cookies"].items():
                cookiestring += key + "=" + value + "; "
            cookiestring = cookiestring[:-2]
        else:
            cookiestring = None

        data_encoded = []

        for k, v in payload.items():
            value = encode(v)

            data_encoded.append(f"{k}={value}")

        datastring = "&".join(data_encoded)

        try:
            gt2r = self._run_async(
                lambda: self.rnet_client.post(
                    f"{self.base_url}/fc/gt2/public_key/{self.settings['public_key']}",
                    body=datastring,
                )
            )

            if gt2r:
                rjson = self._run_async(lambda: gt2r.json())
                #print(rjson)

                self.full_token = rjson["token"]
                self.game_url = rjson["challenge_url_cdn"]

                start = self.game_url.index("bootstrap/") + len("bootstrap/")
                end = self.game_url.index("/", start)
                self.game_version = self.game_url[start:end]

                self.session_token = self.full_token.split("|")[0]

                if "sup" in self.full_token:
                    self._callback_sup()
                    return self.full_token

                if rjson["pow"]:
                    raise Exception("POW is currently not supported.")

        except ProxyError as e:
            raise ProxyConnectionFailed(str(e)) from e

        except HTTPError:
            raise Http3NotSupported()

        except Exception as e:
            raise Exception(
                "CS-AI-ERR: Failed to get token because " + str(e)
            ) from e
