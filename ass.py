
import json

def transform_data(input_data):
    """
    Transforms a browser fingerprint JSON object into the specified format.

    Args:
        input_data (list): A list containing the source dictionary.

    Returns:
        list: The transformed list of key-value pair dictionaries.
    """
    if not input_data or not isinstance(input_data, list):
        return []

    source_object = input_data[0]

    webgl_dict = source_object.get('webgl', {})
    enhanced_fp_list = [{"key": k, "value": v} for k, v in webgl_dict.items()]

    fe_list = source_object.get('fe', [])
    wh = source_object.get('wh', "")

    output_list = [
        {
            "key": "api_type",
            "value": "js"
        },
        {
            "key": "f",
            "value": "73f4d8cf7827e53099b9a6539fecdc5c" 
        },
        {
            "key": "n",
            "value": "MTc1MDAxNTgwOA==" 
        },
        {
            "key": "wh",
            "value": wh
        },
        {
            "key": "enhanced_fp",
            "value": enhanced_fp_list 
        },
        {
            "key": "fb",
            "value": 1 
        },
        {
            "key": "fe",
            "value": fe_list
        },
        {
            "key": "ife_hash",
            "value": "d76be75820d272f1b763a4f44189efec" 
        },
        {
            "key": "jsbd",
            "value": "{\"HL\":4,\"NCE\":true,\"DT\":\"\",\"NWD\":\"false\",\"DMTO\":1,\"DOTO\":1}"
        }
    ]

    return output_list


fps = json.loads(open("webgl.json", "r", encoding="utf-8", errors="replace").read())

count = 0

for fp in fps:
    count += 1
    print(count, end="\r")
    input_data_dict = [fp]

    transformed_data = transform_data(input_data_dict)

    with open(f"db/fingerprints/{count}.json", "a", encoding="utf-8", errors="replace") as f:
        json.dump(transformed_data, f, indent=4)