from curl_cffi.requests.exceptions import *
from curl_cffi.requests import ThreadType, RequestParams
from curl_cffi import Curl, requests, Response
from typing import Optional, Unpack, Literal
from enum import IntEnum

BrowserLiteral = Literal[
    "edge99",
    "edge101",
    "chrome99",
    "chrome100",
    "chrome101",
    "chrome104",
    "chrome107",
    "chrome110",
    "chrome116",
    "chrome119",
    "chrome120",
    "chrome123",
    "chrome124",
    "chrome131",
    "chrome133a",
    "chrome136",
    "chrome99_android",
    "chrome131_android",
    "safari153",
    "safari155",
    "safari170",
    "safari172_ios",
    "safari180",
    "safari180_ios",
    "safari184",
    "safari184_ios",
    "firefox133",
    "firefox135",
    "tor145",
    "chrome",
    "edge",
    "safari",
    "safari_ios",
    "chrome_android",
    "firefox",
]


class HttpVersion(IntEnum):
    NONE = 0
    V1_0 = 1  # HTTP 1.0
    V1_1 = 2  # HTTP 1.1
    V2_0 = 3  # HTTP 2
    V2TLS = 4  # HTTP(s) 1.1
    V2_PRIOR_KNOWLEDGE = 5  # HTTP 1.1 (no idea.)
    V3 = 30  # HTTP 3 - FALLBACK -> HTTP 2
    V3ONLY = 31  # HTTP3 - No Fallback


class Session(requests.Session):
    def __init__(
        self,
        curl: Optional[Curl] = None,
        thread: Optional[ThreadType] = None,
        use_thread_local_curl: bool = True,
        impersonate: Optional[BrowserLiteral] = None,
        **kwargs,
    ):
        super().__init__(
            curl=curl,
            thread=thread,
            use_thread_local_curl=use_thread_local_curl,
            impersonate=impersonate,
            **kwargs,
        )

    def post(self, url: str, **kwargs: Unpack[RequestParams]) -> Response:
        return super().post(url, **kwargs)

    def get(self, url: str, **kwargs: Unpack[RequestParams]) -> Response:
        return super().get(url, **kwargs)

    def options(self, url: str, **kwargs: Unpack[RequestParams]) -> Response:
        return super().options(url, **kwargs)

    def patch(self, url: str, **kwargs: Unpack[RequestParams]) -> Response:
        return super().patch(url, **kwargs)

    def head(self, url: str, **kwargs: Unpack[RequestParams]) -> Response:
        return super().head(url, **kwargs)


if __name__ == "__main__":
    session: Session = Session(impersonate="chrome136")

    print(session.impersonate)

    try:
        r = session.get("https://example.com/")
        print(r.text)

    except Exception as e:
        print(f"Error occurred: {e}")
