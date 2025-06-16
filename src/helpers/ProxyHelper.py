from dataclasses import dataclass
from urllib.parse import urlparse
from typing import Dict

def parse_proxy_url(url: str) -> dict:
    parsed = urlparse(url)

    return {
        "Protocol": parsed.scheme,
        "User": parsed.username or "",
        "Password": parsed.password or "",
        "Host": parsed.hostname,
        "Port": parsed.port
    }


@dataclass
class Proxy:
    Protocol: str

    User: str
    Password: str

    Host: str
    Port: int

    def Proxy_Url(self) -> str:
        return f"{self.Protocol}://{self.User}:{self.Password}@{self.Host}:{self.Port}"

    def Proxy_Dict(self) -> Dict[str, str]: #only work for curl_cffi
        Url: str = self.Proxy_Url()

        ProxyDict: Dict[str, str] = {
            "all": Url
        }

        return ProxyDict

if __name__ == "__main__":
    proxy_data = parse_proxy_url("socks://user123:pass456@127.0.0.1:8080")
    proxy = Proxy(**proxy_data)
    print(proxy)