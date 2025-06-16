import json

realOrder = json.load(open("src/fingerprint/bda/realOrder.json", "r", encoding="utf-8"))
real_order = list(realOrder.keys())


def reorder_bda(bda: dict) -> dict:

    ordered_bda = {key: bda.get(key, realOrder[key]) for key in real_order}

    for key in bda:
        if key not in real_order:
            ordered_bda[key] = bda[key]

    return ordered_bda
