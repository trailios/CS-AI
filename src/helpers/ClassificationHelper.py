from __future__     import annotations
from dataclasses    import dataclass, field
from typing         import ClassVar, Iterable, Optional

from src    import internal_session

import time
import random
import requests

@dataclass
class XEvilClient:
    api_key: str
    hosts: Iterable[str]
    timeout: float = 30.0
    poll_interval: float = 0.5

    DEFAULT_HOSTS: ClassVar[Iterable[str]] = ("157.180.15.203:80", "149.50.108.43:2020",)


    @classmethod
    def with_defaults(
        cls,
        api_key: str,
        hosts: Optional[Iterable[str]] = None,
        timeout: float = 30.0,
        poll_interval: float = 0.5,
    ) -> XEvilClient:
        return cls(
            api_key=api_key,
            hosts=hosts or cls.DEFAULT_HOSTS,
            timeout=timeout,
            poll_interval=poll_interval,
        )


    def _pick_host(self) -> str:
        return random.choice(tuple(self.hosts))


    def _submit_task(self, image_base64: str, instructions: str, host: str) -> str:
        url = f"http://{host}/in.php"
        payload = {
            "method": "base64",
            "key": self.api_key,
            "imginstructions": instructions,
            "body": image_base64,
        }

        response = internal_session.post(url, data=payload)
        parts = response.text.split("|")

        return parts[1]


    def _fetch_result(self, task_id: str, host: str) -> Optional[int]:
        url = f"http://{host}/res.php"
        params = {"action": "get", "key": self.api_key, "id": task_id}
        end_time = time.time() + self.timeout

        while time.time() < end_time:
            response = internal_session.get(url, params=params)
            text = response.text
            if text.startswith("OK|"):
                return int(text.split("|", 1)[1]) - 1
                
            if any(code in text for code in ("FAILED", "ERROR")):
                return None

            time.sleep(self.poll_interval)

        return None

    def solve_image(self, image_base64: str, instructions: str, x: int) -> int:
        host = self._pick_host()
        try:
            task_id = self._submit_task(image_base64, instructions, host)
            result = self._fetch_result(task_id, host)
            return result if result is not None else random.randint(0, x)
            
        except requests.RequestException:
            return random.randint(0, x)
