from dataclasses    import dataclass
from urllib.parse   import urlparse
from typing         import Dict


@dataclass
class Proxy:
    Protocol:   str
    User:       str
    Password:   str
    Host:       str
    Port:       int
    UnEdited:   str

    @classmethod
    def parse(cls, url: str) -> "Proxy":
        parsed = urlparse(url)
        return cls(
            Protocol=parsed.scheme,
            User=parsed.username or "",
            Password=parsed.password or "",
            Host=parsed.hostname,
            Port=parsed.port,
            UnEdited=url
        )

    def __str__(self) -> str:
        return self.UnEdited

    def __str__UnEdited(self) -> str:
        return self.UnEdited

    def dict(self) -> Dict[str, str]:
        return {"all": self.__str__()}

