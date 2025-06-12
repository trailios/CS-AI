from curl_cffi.requests import ThreadType, RequestParams
from curl_cffi import Curl, requests
from typing import Optional, Unpack


class Session(requests.Session):
    def __init__(
        self,
        curl: Optional[Curl] = None,
        thread: Optional[ThreadType] = None,
        use_thread_local_curl: bool = True,
        impersonate: Optional[str] = None,
        **kwargs,
    ):
        super().__init__(
            curl=curl,
            thread=thread,
            use_thread_local_curl=use_thread_local_curl,
            impersonate=impersonate,
            **kwargs,
        )

    def post(self, url: str, **kwargs: Unpack[RequestParams]):
        return super().post(url, **kwargs)

    def get(self, url: str, **kwargs: Unpack[RequestParams]):
        return super().get(url, **kwargs)

    def options(self, url: str, **kwargs: Unpack[RequestParams]):
        return super().options(url, **kwargs)

    def patch(self, url: str, **kwargs: Unpack[RequestParams]):
        return super().patch(url, **kwargs)

    def head(self, url: str, **kwargs: Unpack[RequestParams]):
        return super().head(url, **kwargs)


if __name__ == "__main__":
    session: Session = Session(impersonate="chrome")

    print(session.impersonate)

    try:
        r = session.get("https://example.com/")
        print(r.text)

    except Exception as e:
        print(f"Error occurred: {e}")
