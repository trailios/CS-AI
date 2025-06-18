from src.helpers.SessionHelper import Session, CurlHttpVersion
from typing import Dict

from src.helpers.ProxyHelper import Proxy


class Challenge:
    def __init__(self, Headers: Dict[str, str], Proxy: Proxy) -> None:
        self.session = Session()

        self.session.impersonate = "edge"
        self.session.headers = Headers
        self.session.proxies = Proxy.dict()
