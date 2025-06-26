import json



methodsList = ['enforcementJS','enforcementHTML','iframe','gt2','a','api']

def transform_key(key: str) -> str:

    return key.lower()

def deep_transform_keys(obj):
    if isinstance(obj, dict):
        new_dict = {}
        for key, value in obj.items():
            new_key = transform_key(key)
            new_value = deep_transform_keys(value)

            if isinstance(new_value, dict):
                new_value = {transform_key(k): deep_transform_keys(v) for k, v in new_value.items()}
            new_dict[new_key] = new_value
        return new_dict
    elif isinstance(obj, list):
        return [deep_transform_keys(item) for item in obj]
    else:
        return obj


def parseHeader(method,headers):
    if method not in methodsList:
        raise ValueError(f"Method '{method}' is not supported. Supported methods are: {methodsList}")
    headers = deep_transform_keys(headers)
