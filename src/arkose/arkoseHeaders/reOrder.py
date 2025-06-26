import os
import json
from collections import OrderedDict

target_folder = "src/arkose/arkoseHeaders/headerStorage"
cache_folder = "headerCache"

def lowercase_keys(obj):
    if isinstance(obj, dict):
        return OrderedDict((k.lower(), lowercase_keys(v)) for k, v in obj.items())
    elif isinstance(obj, list):
        return [lowercase_keys(item) for item in obj]
    else:
        return obj

def compare_dicts(original, updated, path=""):
    changes = []
    orig_keys = list(original.keys())
    updated_keys = list(updated.keys())

    if orig_keys != updated_keys:
        changes.append(f"  [!] Key order changed at {path or '/'}")

    for key in original:
        if key not in updated:
            changes.append(f"  [-] Removed key: {path + '.' + key if path else key}")
        elif original[key] != updated[key]:
            changes.append(f"  [~] Value changed: {path + '.' + key if path else key} — '{original[key]}' → '{updated[key]}'")

    for key in updated:
        if key not in original:
            changes.append(f"  [+] New key added: {path + '.' + key if path else key}")

    return changes

def process_json_files(folder_path):
    for root, _, files in os.walk(folder_path):
        for file_name in files:
            if file_name.endswith(".json"):
                rel_path = os.path.relpath(os.path.join(root, file_name), folder_path)
                original_path = os.path.join(root, file_name)
                cache_path = os.path.join(cache_folder, rel_path)

                os.makedirs(os.path.dirname(cache_path), exist_ok=True)

                try:
                    with open(original_path, "r", encoding="utf-8") as f:
                        original_data = json.load(f, object_pairs_hook=OrderedDict)

                    with open(cache_path, "w", encoding="utf-8") as f:
                        json.dump(original_data, f, indent=2)

                    lowered_data = lowercase_keys(original_data)

                    with open(original_path, "w", encoding="utf-8") as f:
                        json.dump(lowered_data, f, indent=2)

                    changes = compare_dicts(original_data, lowered_data)
                    if changes:
                        print(f"\n[•] Changes in {original_path}:")
                        for change in changes:
                            print(change)

                except Exception as e:
                    print(f"[✗] Error processing {original_path}: {e}")

process_json_files(target_folder)

