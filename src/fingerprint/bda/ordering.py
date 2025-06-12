
import json
realOrder = json.load(open("src/fingerprint/bda/realOrder.json", "r", encoding="utf-8"))
real_order = list(realOrder.keys())


def reorder_bda(bda: dict) -> dict:
    # Step 1: Create a new dict in the exact order
    ordered_bda = {key: bda.get(key,realOrder[key] ) for key in real_order}
    # If any key not present the missing one
    
    # Step 2: Include any extra keys from bda that aren't in real_order
    for key in bda:
        if key not in real_order:
            ordered_bda[key] = bda[key]

    return ordered_bda
