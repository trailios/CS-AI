import json



def reorder_bda(preset,bda: dict) -> dict:
    realOrder = json.load(open(f"src/fingerprint/bda/{preset}realOrder.json", "r", encoding="utf-8"))
    real_order = list(realOrder.keys())

    ordered_bda = {key: bda.get(key, realOrder[key]) for key in real_order}

    for key in bda:
        if key not in real_order:
            ordered_bda[key] = bda[key]

    return ordered_bda
