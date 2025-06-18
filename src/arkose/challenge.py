from typing import Dict

from src.helpers.SessionHelper import Session, HttpVersion
from src.helpers.ProxyHelper import Proxy


class Challenge:
    def __init__(self, Headers: Dict[str, str], Proxy: Proxy) -> None:
        self.session = Session(impersonate="edge")

        self.session.headers = Headers
        self.session.proxies = Proxy.dict()
