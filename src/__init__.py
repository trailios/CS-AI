from src.helpers.KeyHelper      import KeyService
from src.helpers.SessionHelper  import Session
from src.helpers.ProxyHelper    import Proxy
from src.utils.logger           import *
from src.utils.utils            import Utils


key_service = KeyService()
proxyHelper = Proxy

internal_session: Session = Session(impersonate="chrome")
internal_session.headers = {
    "accept": "*/*",
    "accept-language": "en-US,en;q=0.9",
    "cache-control": "no-cache",
    "pragma": "no-cache",
    "referer": "https://www.roblox.com/",
    "sec-ch-ua": '"Chromium";v="138", "Google Chrome";v="136", "Not.A/Brand";v="99"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "script",
    "sec-fetch-mode": "no-cors",
    "sec-fetch-site": "same-site",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
}

log = ... # new logger aint impleented yet
tools: Utils = Utils

