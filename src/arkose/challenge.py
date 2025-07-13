from typing                     import Dict, Optional, Any
from random                     import random
from urllib                     import parse
from time                       import time


from src.helpers.SessionHelper  import (
    HTTPError, 
    ProxyError, 
    Session, 
    HttpVersion
)
from src.utils.versionInfo      import get_version_info
from src.helpers.ProxyHelper    import Proxy


class ProxyConnectionFailed(Exception):
    PREFIX = "CS-AI-ERR:"

    def __init__(self, message: str = "Proxy connection failed"):
        full_message = f"{self.PREFIX} {message}"
        super().__init__(full_message)


class Http3NotSupported(Exception):
    PREFIX = "CS-AI-ERR:"

    def __init__(self, message: str = "Http3 is not supported by proxy provider"):
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
    ) -> None:
        self.session: Session = Session(impersonate="edge")
        self.session.http_version = HTTPVersion

        self.session.headers = Headers
        self.session.proxies = Proxy.dict()

        self.cookies:   Dict[str, str] = {}
        self.settings:  Dict[str, str] = Settings
        self.browser:   Dict[str, Any] = BrowserData

        self.base_url:  str = Settings["service_url"]
        self.version, self.hash = get_version_info(
            Settings["service_url"], Settings["public_key"]
        )

        self.session_token: str = ""
        self.full_token:    str = ""
        self.game_url:      str = ""
        self.game_version:  str = ""

    def _pre_load(self) -> None:
        try:
            r = self.session.get(
                f"{self.base_url}/v2/{self.version}/api.js"
            )
            self.session.cookies.update(r.cookies)
            self.cookies.update(r.cookies.get_dict())

            self.session.get(f"{self.base_url}/v2/{self.version}/settings")

        except ProxyError as e:
            raise ProxyConnectionFailed(str(e))

        except HTTPError as e:
            raise Http3NotSupported(str(e))

        except Exception as e:
            raise Exception("CS-AI-ERR: Failed to pre-load challenge because " + str(e))

    def _callback_sup(self) -> None:
        params = {
            "callback": "__jsonp_" + str(int(time() * 1000)),
            "category": "loaded",
            "action": "game loaded",
            "session_token": self.session_token,
            "data[public_key]": self.settings["public_key"],
            "data[site]": parse.quote(self.settings["site_url"]),
        }

        try:
            self.session.get(f"{self.base_url}/fc/a/", params=params)

        except ProxyError as e:
            raise ProxyConnectionFailed(str(e))

        except HTTPError as e:
            raise Http3NotSupported(str(e))

        except Exception as e:
            raise Exception("CS-AI-ERR: Failed to callback because " + str(e))

    def gt2(self) -> None:

        payload = {
            "public_key": self.settings["public_key"],
            "capi_version": self.version,
            "style_theme": "default",
            "rnd": str(random()),
            "bda": self.browser["bda"],
            "site": self.settings["site"],
            "userbrowser": self.session.headers["user-agent"],
        }

        if self.settings["blob"]:
            payload["data[blob]"] = self.settings["blob"]

        try:
            gt2r = self.session.post(f"https://{self.base_url}/fc/gt2/public_key/{self.settings["public_key"]}", data=str(parse.urlencode(payload)))

            if "denied" in gt2r.text.lower() or gt2r.status_code == 400:
                raise Exception("Blob has been refused by provider.")

            if gt2r.ok:
                rjson = gt2r.json()

                self.full_token = rjson["token"]
                self.game_url = rjson["challenge_url_cdn"]

                start = self.game_url.index("bootstrap/") + len("bootstrap/")
                end = self.game_url.index("/", start)
                self.game_version = self.game_url[start:end]

                self.session_token = self.full_token.split("|")[0]

                if "sup" in self.full_token:
                    self._callback_sup()

                    return self.full_token
            
        except ProxyError as e:
            raise ProxyConnectionFailed(str(e))

        except HTTPError as e:
            raise Http3NotSupported(str(e))

        except Exception as e:
            raise Exception("CS-AI-ERR: Failed to get token because " + str(e))
