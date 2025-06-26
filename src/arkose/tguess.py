import json
import string
from typing import Any, Dict, List

from javascript import require
from src.utils.crypto import encrypt_data

class DapibClient:
    def __init__(
        self,
        user_agent: Session,
        dapib_code: str,
        vm_storage_quota: int = 10_000_000,
    ) -> None:
        self.user_agent = user_agent
        self.dapib_code = dapib_code
        self.vm_storage_quota = vm_storage_quota
        self.jsdom = require("jsdom")
        self.vm_script = require("vm").Script

    @staticmethod
    def _ends_with_uppercase(value: str) -> bool:
        return bool(value) and value[-1] in string.ascii_uppercase

    @classmethod
    def is_flagged(cls, data: List[Dict[str, Any]]) -> bool:
        if not data or not isinstance(data, list):
            return False
        all_values = [val for record in data for val in record.values()]
        if not all_values:
            return False
        return all(cls._ends_with_uppercase(val) for val in all_values)

    def t_guess(
        self,
        user_agent: str,
        guesses: List[str],
        session_token: str,
    ) -> str:
        tok, en = session_token.split(".", 1)
        answers: List[Dict[str, Any]] = []
        for raw in guesses:
            guess_obj = json.loads(raw)
            if "index" in guess_obj:
                answers.append({"index": guess_obj["index"], tok: en})
            else:
                answers.append(
                    {
                        "px": guess_obj.get("px"),
                        "py": guess_obj.get("py"),
                        "x": guess_obj.get("x"),
                        "y": guess_obj.get("y"),
                        tok: en,
                    }
                )

        resource_loader = self.jsdom.ResourceLoader(
            {
                "userAgent": user_agent
                or (
                    self.user_agent or  "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36"
                )
            }
        )

        dom = self.jsdom.JSDOM(
            "",
            {
                "runScripts": "dangerously",
                "resources": resource_loader,
                "pretendToBeVisual": True,
                "storageQuota": self.vm_storage_quota,
            },
        )
        vm_context = dom.getInternalVMContext()

        inject_answers = """
            response=null;

            window.parent.ae={"answer":answers}

            window.parent.ae[("dapibRecei" + "ve")]=function(data) {
                response=JSON.stringify(data);
            }
        """.replace("answers", json.dumps(answers).replace('"index"', "index"))
        
        self.vm_script(inject_answers).runInContext(vm_context)
        self.vm_script(self.dapib_code).runInContext(vm_context)

        response_json = self.vm_script("response").runInContext(vm_context)
        result = json.loads(response_json)

        tanswer = result.get("tanswer", [])

        if self.is_flagged(tanswer):
            for record in tanswer:
                for key, val in record.items():
                    if val and val[-1] in string.ascii_uppercase:
                        record[key] = val[:-1]

        compact = json.dumps(tanswer, separators=(",", ":"))
        return encrypt_data(compact, session_token)
