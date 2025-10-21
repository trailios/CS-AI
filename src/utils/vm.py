from random import choice

def transform_payload(payload: list, cbid: str) -> list:
    try:

        target: list = payload[4]["value"]
        val25 = target[25]
        val26 = target[26]
        val1 = target[1]
        val18 = target[18]

        if not val25 or not val26 or not val1 or not val18:
            return None

        target[25] = {
            "key": val25["key"],
            "value": val1["value"][:3] + val18["value"][:3],
        }

        target[26] = {"key": val26["key"], "value": val26["value"] * 3}

        target.append({"key": "vsadsa", "value": choice([3,4,7])})
        target.append({"key": "basfas", "value": [0,4294705152]})
        target.append({"key": "lfasdgs", "value": cbid})



        return payload

    except Exception as e:

        return None
