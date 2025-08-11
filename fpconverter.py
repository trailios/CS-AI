import os
import json

OLD_DIR = "db/OLD_fingerprints"
NEW_DIR = "db/OLD_fingerprints" 

files = [f for f in os.listdir(OLD_DIR) if f.endswith(".fp") or f.endswith(".json")]

for filename in files:
    old_path = os.path.join(OLD_DIR, filename)
    new_path = "newfp.json"

    if not os.path.exists(new_path):
        print(f"Skipping {filename}: no matching file in NEW directory")
        continue

    oldfp = json.load(open(old_path, encoding="utf-8"))
    newfp = json.load(open(new_path, encoding="utf-8"))

    newfpProcessed = {fpdict["key"]: fpdict["value"] for fpdict in newfp}
    oldfpProcessed = {fpdict["key"]: fpdict["value"] for fpdict in oldfp}

    newenhancedfp = newfpProcessed["enhanced_fp"]
    oldenhancedfp = oldfpProcessed["enhanced_fp"]

    newenhancedfpProcessed = {efp["key"]: efp["value"] for efp in newenhancedfp}
    oldenhancedfpProcessed = {efp["key"]: efp["value"] for efp in oldenhancedfp}

    missing_keys = set(newenhancedfpProcessed.keys()) - set(oldenhancedfpProcessed.keys())
    removed_keys = set(oldenhancedfpProcessed.keys()) - set(newenhancedfpProcessed.keys())

    print(f"=== {filename} ===")
    print("missing in old enhanced_fp:", missing_keys)
    print("removed from new enhanced_fp:", removed_keys)

    replacements = {
        "5dd48ca0": "rtc_peer_connection",
        "3f76dd27": "screen_orientation",
        "7541c2s": "media_devices_hash",
        "862f2c1": "headless_browser_generic",
    }
    for new_key, old_key in replacements.items():
        if old_key in oldenhancedfpProcessed:
            oldenhancedfpProcessed[new_key] = oldenhancedfpProcessed[old_key]

    oldenhancedfpProcessed.pop("media_device_kinds", None)

    newfporder = list(newenhancedfpProcessed.keys())
    oldenhancedfpProcessed_ordered = {
        key: oldenhancedfpProcessed[key]
        for key in newfporder
        if key in oldenhancedfpProcessed
    }

    enhancedfplist = []
    fplist = []

    for key, value in oldenhancedfpProcessed_ordered.items():
        fpdict = {
            "key": key,
            "value": value
        }

        enhancedfplist.append(fpdict)

    oldfpProcessed["enhanced_fp"] = enhancedfplist

    for key, value in oldfpProcessed.items():
        fppdict = {
            "key": key,
            "value": value
        }

        fplist.append(fppdict)

    with open(f"db/fingerprints/{filename}", "w") as f:
        json.dump(fplist, f, indent=4)