import json
realBDA = "bdaSandbox_WIP/realBDA.json"
realBDA = json.load(open(realBDA, "r", encoding="utf-8"))

def convert_to_dict(data_list):
    result = {}
    for item in data_list:
        key = item["key"]
        value = item["value"]
        if isinstance(value, list) and all(isinstance(i, dict) and "key" in i and "value" in i for i in value):
           
            result[key] = convert_to_dict(value)
        else:
            result[key] = value
    return json.dumps(result, indent=4)
print(convert_to_dict(realBDA))
