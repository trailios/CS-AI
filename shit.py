import json
import os
import re
import shutil
import subprocess
import tempfile
import time
from pathlib import Path

import requests
import esprima


CACHE_PATH = Path.home() / ".cache" / "vm_key_cache.json"
CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)


def _get_cached(api_url: str, sitekey: str):
    if not CACHE_PATH.exists():
        return None
    try:
        with CACHE_PATH.open("r", encoding="utf-8") as fh:
            data = json.load(fh)
    except Exception:
        return None
    return data.get(api_url, {}).get(sitekey)


def _set_cache(api_url: str, sitekey: str, value: dict):
    data = {}
    if CACHE_PATH.exists():
        try:
            with CACHE_PATH.open("r", encoding="utf-8") as fh:
                data = json.load(fh)
        except Exception:
            data = {}
    data.setdefault(api_url, {})[sitekey] = value
    with CACHE_PATH.open("w", encoding="utf-8") as fh:
        json.dump(data, fh)


def _run_node_eval(js_expr: str):
    node = shutil.which("node")
    if not node:
        raise RuntimeError("node executable not found in PATH")
    script = f"try{{console.log(JSON.stringify({js_expr}))}}catch(e){{console.error('ERR:',e && e.message||e);process.exit(2)}}"
    proc = subprocess.run([node, "-e", script], capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip() or "node eval failed")
    return json.loads(proc.stdout)


def _run_node_parser(script_content: str):
    node = shutil.which("node")
    if not node:
        raise RuntimeError("node executable not found in PATH")
    parser_path = Path(__file__).resolve().parent / "js" / "parser.js"
    if not parser_path.exists():
        raise FileNotFoundError(f"parser.js not found at {parser_path}")
    with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False, encoding="utf-8") as tmp:
        tmp.write(script_content)
        tmp_path = tmp.name
    try:
        proc = subprocess.run(
            [node, str(parser_path), tmp_path],
            capture_output=True,
            text=True,
        )
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
                    found_pattern = False
                    for el in elements:
                        if getattr(el, "type", "") == "BinaryExpression" and getattr(el, "operator", "") == "+":
                            right = getattr(el, "right", None)
                            if getattr(right, "type", "") == "Literal" and getattr(right, "value", "") == "L2":
                                found_pattern = True
                                break
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
        if not arr:
            continue
        if not isinstance(arr, list) or not arr:
            continue
        candidate = max(arr, key=lambda x: len(x) if isinstance(x, str) else 0)
        if not isinstance(candidate, str):
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
    start = time.time()
    cached = _get_cached(api_url, sitekey)
    if cached and "vm_key" in cached:
        return cached["vm_key"]
    resp = requests.get(f"{api_url}/v2/{sitekey}/api.js", timeout=30)
    resp.raise_for_status()
    script = resp.text
    keys = decode_script(script)
    if not keys:
        return None
    key = keys[0]["decoded"]
    _set_cache(api_url, sitekey, {"vm_key": key})
    print(time.time() - start)
    return key


if __name__ == "__main__":
    api_url = "https://arkoselabs.roblox.com"
    sitekey = "476068BF-9607-4799-B53D-966BE98E2B81"
    print(get_vm_key(api_url, sitekey))
