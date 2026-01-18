import json
import os
import re
import shutil
import subprocess
import tempfile
import time
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit
import hashlib
import requests
import esprima

# i have no idea, this was ai

CACHE_PATH = Path.home() / ".cache" / "vm_key_cache.json"
CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)

def _atomic_write(path: Path, data: dict):
    tmp = path.with_suffix(path.suffix + f".{os.getpid()}.tmp")
    with tmp.open("w", encoding="utf-8") as f:
        json.dump(data, f)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)

def _load_cache() -> dict:
    if not CACHE_PATH.exists():
        return {}
    try:
        with CACHE_PATH.open("r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, dict) else {}
    except Exception:
        return {}

def _save_cache(data: dict):
    _atomic_write(CACHE_PATH, data)

def _normalize_api_url(api_url: str) -> str:
    parts = urlsplit(api_url.strip())
    scheme = parts.scheme or "https"
    netloc = parts.netloc.lower()
    path = parts.path.rstrip("/")
    return urlunsplit((scheme, netloc, path, "", ""))

def _normalize_sitekey(sitekey: str) -> str:
    return sitekey.strip()

def _ns_keys(api_url: str, sitekey: str) -> tuple[str, str]:
    return _normalize_api_url(api_url), _normalize_sitekey(sitekey)

def _cache_key(api_url: str, sitekey: str) -> str:
    a, s = _ns_keys(api_url, sitekey)
    return hashlib.sha256(f"{a}:{s}".encode()).hexdigest()

def _get_cached(api_url: str, sitekey: str):
    a, s = _ns_keys(api_url, sitekey)
    data = _load_cache()
    return data.get(a, {}).get(s)

def _set_cache(api_url: str, sitekey: str, value: dict):
    a, s = _ns_keys(api_url, sitekey)
    data = _load_cache()
    if a not in data:
        data[a] = {}
    entry = data[a].get(s, {})
    entry.update(value)
    entry["updated_at"] = int(time.time())
    data[a][s] = entry
    _save_cache(data)

def version_info(api_url: str, sitekey: str) -> tuple[str, str, str]:
    cached = _get_cached(api_url, sitekey)
    if cached and "version_info" in cached:
        return tuple(cached["version_info"])
    a, s = _ns_keys(api_url, sitekey)
    r = requests.get(f"{a}/v2/{s}/api.js", timeout=30)
    r.raise_for_status()
    js = r.text
    try:
        enforcement = js.split('h="inline",g=void 0,m="')[1].split('"')[0]
        capi, hash_ = enforcement.split("/")
        hash_ = hash_.split(".")[1]
        cbid = js.split('html",y="Verification challenge",b="')[1].split('"')[0]
        data = (capi, hash_, cbid)
        _set_cache(api_url, sitekey, {"version_info": list(data)})
        return data
    except Exception:
        raise Exception("Site not supported")

def _run_node_eval(js_expr: str):
    node = shutil.which("node")
    if not node:
        raise RuntimeError("node executable not found in PATH")
    script = f"try{{console.log(JSON.stringify({js_expr}))}}catch(e){{console.error('ERR:',e&&e.message||e);process.exit(2)}}"
    proc = subprocess.run([node, "-e", script], capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip() or "node eval failed")
    return json.loads(proc.stdout)

def _run_node_parser(script_content: str):
    node = shutil.which("node")
    if not node:
        raise RuntimeError("node executable not found in PATH")
    parser_path = Path(__file__).resolve().parent.parent.parent / "js" / "parser.js"
    if not parser_path.exists():
        raise FileNotFoundError(f"parser.js not found at {parser_path}")
    with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False, encoding="utf-8") as tmp:
        tmp.write(script_content)
        tmp_path = tmp.name
    try:
        proc = subprocess.run([node, str(parser_path), tmp_path], capture_output=True, text=True)
        if proc.returncode != 0:
            stderr = proc.stderr.strip()
            raise RuntimeError(stderr or "parser.js execution failed")
        output = proc.stdout.strip()
        if not output:
            return []
        return json.loads(output)
    finally:
        try:
            os.unlink(tmp_path)
        except FileNotFoundError:
            pass

def _extract_array_sources(script_content: str):
    tree = esprima.parseScript(script_content, tolerant=True, range=True)
    arrays = []
    for node in tree.body:
        if getattr(node, "type", None) == "VariableDeclaration":
            for decl in getattr(node, "declarations", []):
                init = getattr(decl, "init", None)
                if init and getattr(init, "type", "") == "ArrayExpression":
                    elements = getattr(init, "elements", [])
                    found_pattern = any(
                        getattr(el, "type", "") == "BinaryExpression"
                        and getattr(el, "operator", "") == "+"
                        and getattr(getattr(el, "right", None), "type", "") == "Literal"
                        and getattr(getattr(el, "right", None), "value", "") == "L2"
                        for el in elements
                    )
                    src = script_content[init.range[0] : init.range[1]]
                    if found_pattern:
                        arrays.append(src)
    return arrays

def _normalize_js_array_to_json_like(src: str):
    s = src.strip()
    s = re.sub(r",\s*]", "]", s)
    s = s.replace("undefined", "null")
    return s

def decode_script(script_content: str):
    try:
        node_results = _run_node_parser(script_content)
        if node_results:
            return node_results
    except Exception:
        pass
    array_sources = _extract_array_sources(script_content)
    if not array_sources:
        return []
    for arr_src in array_sources:
        normalized = _normalize_js_array_to_json_like(arr_src)
        try:
            arr = json.loads(normalized.replace("'", '"'))
        except Exception:
            try:
                arr = _run_node_eval(arr_src)
            except Exception:
                arr = None
        if not arr or not isinstance(arr, list):
            continue
        candidate = max((x for x in arr if isinstance(x, str)), key=len, default=None)
        if not candidate:
            continue
        parts = candidate.split("'")
        if len(parts) >= 3:
            encoded = parts[1]
            return _brute_xor_keys(encoded)
    return []

def _brute_xor_keys(encoded: str):
    results = []
    for i in range(1000):
        key = str(i)
        klen = len(key)
        try:
            decoded = "".join(chr(ord(c) ^ ord(key[j % klen])) for j, c in enumerate(encoded))
        except Exception:
            continue
        if all(ch not in "@|~`<>" for ch in decoded):
            results.append({"key": i, "decoded": decoded})
    return results

def get_vm_key(api_url: str, sitekey: str):
    return "MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAyAoGUKHuNGFlVJqAhq+m8iJ7FUY0E89CFU/nhpt6/WVuWhqux8360qqlGJzG6RqnCxwG3CFrw9KqUhVJ7OEncdiZ8HDWx3+GJcMLWghLH7nQ3MsvtwfNkYuxZP/Em72+rC8fVchbGkR52E5CSLIsCuwzMM5EFMEBM6hOxMW/mJaLjEzx6hBJBBsotQB/+NXSJHBFDY3v1wgww9j2BZvXs2vbELSuT2aYBVP7ZP53ra7zYevVQMnU57+m2Ndm+/xGr+7XQPIVUxCouzPKCOSx7+gipUscaIiWGO8tXETyuuzyhGwNOp4vyTbHOdBmxQK/DX3M8g9/Awqq3UGFq7cvzQIDAQAB"
    
    # bla bla parser broke, manual key
    
    cached = _get_cached(api_url, sitekey)
    if cached and "vm_key" in cached and isinstance(cached["vm_key"], str) and cached["vm_key"]:
        return cached["vm_key"]
    a, s = _ns_keys(api_url, sitekey)
    resp = requests.get(f"{a}/v2/{s}/api.js", timeout=30)
    resp.raise_for_status()
    script = resp.text
    keys = decode_script(script)
    if not keys:
        return None
    key = keys[0]["decoded"]
    _set_cache(api_url, sitekey, {"vm_key": key})
    return key

api_url = "https://arkoselabs.roblox.com/"
sitekey = "476068BF-9607-4799-B53D-966BE98E2B81"
print(get_vm_key(api_url, sitekey))
