import json


realOrder: dict = json.load(open(f"src/fingerprint/bda/realOrder.json", "r", encoding="utf-8")) 

def reorder_bda(preset: str, bda: dict) -> dict:
    real_order = list(realOrder.keys())

    ordered_bda = {key: bda.get(key, realOrder[key]) for key in real_order}

    for key in bda:
        if key not in real_order:
            ordered_bda[key] = bda[key]

    return ordered_bda
