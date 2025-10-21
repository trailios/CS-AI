import requests
from json import loads
import subprocess
import tempfile
import os
import hashlib
import time

_cache = {}
_CACHE_TTL = 300

def _cache_key(api_url: str, sitekey: str) -> str:
    return hashlib.sha256(f"{api_url}:{sitekey}".encode()).hexdigest()

def _get_cached(api_url: str, sitekey: str):
    key = _cache_key(api_url, sitekey)
    if key in _cache:
        entry = _cache[key]
        if time.time() - entry["time"] < _CACHE_TTL:
            return entry["value"]
        del _cache[key]
    return None

def _set_cache(api_url: str, sitekey: str, value):
    _cache[_cache_key(api_url, sitekey)] = {"value": value, "time": time.time()}

def version_info(api_url: str, sitekey: str) -> tuple[str, str, str]:
    cached = _get_cached(api_url, sitekey)
    if cached and "version_info" in cached:
        return cached["version_info"]

    r = requests.get(f"{api_url}/v2/{sitekey}/api.js")
    js = r.text
    try:
        enforcement = js.split('h="inline",g=void 0,m="')[1].split('"')[0]
        capi, hash_ = enforcement.split("/")
        hash_ = hash_.split(".")[1]
        cbid = js.split('html",y="Verification challenge",b="')[1].split('"')[0]
        data = (capi, hash_, cbid)
        _set_cache(api_url, sitekey, {"version_info": data})
        return data
    except:
        raise Exception("Site not supported")

def get_vm_key(api_url: str, sitekey: str):
    cached = _get_cached(api_url, sitekey)
    if cached and "vm_key" in cached:
        return cached["vm_key"]

    response = requests.get(f"{api_url}/v2/{sitekey}/api.js")
    script_content = response.text

    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt', encoding='utf-8') as temp_file:
        temp_file.write(script_content)
        temp_file_path = temp_file.name

    try:
        result = subprocess.run(
            ['node', r'.\js\parser.js', temp_file_path],
            capture_output=True,
            text=True,
            encoding='utf-8',
            check=True
        )
        key_dict = loads(result.stdout)
        key = key_dict[0]["decoded"]
        if key:
            _set_cache(api_url, sitekey, {"vm_key": key})
            return key
    finally:
        os.unlink(temp_file_path)
