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
<<<<<<< HEAD
    UnEdited:   str
=======
>>>>>>> bc866b9515201de4fa468acf7551815a35983e33

    @classmethod
    def parse(cls, url: str) -> "Proxy":
        parsed = urlparse(url)
        return cls(
            Protocol=parsed.scheme,
            User=parsed.username or "",
            Password=parsed.password or "",
            Host=parsed.hostname,
            Port=parsed.port,
<<<<<<< HEAD
            UnEdited=url
        )

    def __str__(self) -> str:
        return self.UnEdited

    def __str__UnEdited(self) -> str:
        return self.UnEdited
=======
        )

    def __str__(self) -> str:
        return f"{self.Protocol}://{self.User}:{self.Password}@{self.Host}:{self.Port}"
>>>>>>> bc866b9515201de4fa468acf7551815a35983e33

    def dict(self) -> Dict[str, str]:
        return {"all": self.__str__()}

