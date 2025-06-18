from dataclasses import dataclass
from urllib.parse import urlparse
from typing import Dict


@dataclass
class Proxy:
    Protocol: str
    User: str
    Password: str
    Host: str
    Port: int

    @classmethod
    def parse(cls, url: str) -> "Proxy":
        parsed = urlparse(url)
        return cls(
            Protocol=parsed.scheme,
            User=parsed.username or "",
            Password=parsed.password or "",
            Host=parsed.hostname,
            Port=parsed.port,
        )

    def __str__(self) -> str:
        return f"{self.Protocol}://{self.User}:{self.Password}@{self.Host}:{self.Port}"

    def dict(self) -> Dict[str, str]:  # only works for curl_cffi
        return {"all": self.__str__()}


if __name__ == "__main__":
    proxy = Proxy.parse("socks://user123:pass456@127.0.0.1:8080")
    print(proxy)
    print(proxy.__str__())
    print(proxy.dict())
