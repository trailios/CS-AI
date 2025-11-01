import os, time
import tempfile
import subprocess
import requests
from json import loads

_cache = {}


def _get_cached(api_url: str, sitekey: str):
    return _cache.get((api_url, sitekey))


def _set_cache(api_url: str, sitekey: str, data: dict):
    _cache[(api_url, sitekey)] = data


def get_vm_key(api_url: str, sitekey: str):
    start = time.time()
    cached = _get_cached(api_url, sitekey)
    if cached and "vm_key" in cached:
        return cached["vm_key"]

    response = requests.get(f"{api_url}/v2/{sitekey}/api.js")
    response.raise_for_status()
    script_content = response.text

    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt", encoding="utf-8") as temp_file:
        temp_file.write(script_content)
        temp_file_path = temp_file.name

    try:
        result = subprocess.run(
            ["node", r".\js\parser.js", temp_file_path],
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=True,
        )
        key_dict = loads(result.stdout)
        key = key_dict[0]["decoded"]
        if key:
            _set_cache(api_url, sitekey, {"vm_key": key})
            end = time.time()
            print(end-start)
            return key
    finally:
        os.unlink(temp_file_path)


if __name__ == "__main__":
    api_url = "https://arkoselabs.roblox.com"
    sitekey = "476068BF-9607-4799-B53D-966BE98E2B81"
    print(get_vm_key(api_url, sitekey))
