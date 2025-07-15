import time
import json

from base64 import b64encode
from json   import dumps

from src.fingerprint.bda.enhancedfp import enhanced_fp
from src.utils.crypto               import AES_Crypto
from src.utils.ipIntelligence       import getIpInfo
from src.utils.utils                import Utils
from src.helpers.ProxyHelper        import Proxy


def getCFP(bda):
    return list(bda["fe"])[14].split(":")[1]


def prepare_fingerprint_data(fingerprint: dict) -> str:
    formatted_data = []
    for key, value in fingerprint.items():
        if isinstance(value, list):
            formatted_data.append(",".join(map(str, value)))
        else:
            formatted_data.append(str(value))
    return ";".join(formatted_data)


def returnBDA(proxy: Proxy, method: str, userbrowser: str ):
    enhancedfp = enhanced_fp(method)
    CFP = getCFP(enhancedfp["realBdaUsed"])
    TO = getIpInfo(proxy)
    fe = [
        "DNT:unknown",
        "L:en-US",
        "D:24",
        "PR:1",
        "S:1920,1080",
        "AS:1920,1080", # what the fuck !?!?!? :fire:
        f"TO:{TO}",
        "SS:true",
        "LS:true",
        "IDB:true",
        "B:false",
        "ODB:false",
        "CPUC:unknown",
        "PK:Win32",
        f"CFP:{CFP}",
        "FR:false",
        "FOS:false",
        "FB:false",
        "JSF:",
        "P:Chrome PDF Viewer,Chromium PDF Viewer,Microsoft Edge PDF Viewer,PDF Viewer,WebKit built-in PDF",
        "T:0,false,false",
        "H:8",
        "SWF:false",
    ]
    data_dict = {item.split(":")[0]: item.split(":")[1] for item in fe}
    data_entries = prepare_fingerprint_data(data_dict)
    BDA = {
        "api_type": "js",
        "f": Utils.x64hash128(prepare_fingerprint_data(data_dict), 0),
        "n": b64encode(str(int(time.time())).encode("utf-8")).decode("utf-8"),
        "wh": "6e783395340e2dddfb86bc8a7f040a3c|cc7fecdd5c8bec57541ae802c7648eed",# proto|browserbasedproto
        "enhanced_fp": enhancedfp["formatted"],
        "fe": fe,
        "ife_hash": Utils.x64hash128(", ".join(data_entries), 38),
        "jsbd": '{"HL":2,"NCE":true,"DT":"","NWD":"false","DMTO":1,"DOTO":1}',
    }
    bdaList = [{"key": k, "value": v} for k, v in BDA.items()]
    timestamp = time.time()
    timeframe = int(timestamp - (timestamp % 21600))


    return b64encode(json.dumps(
        AES_Crypto.encrypt_data(dumps(bdaList), userbrowser + str(timeframe)), separators=(",", ": ")
    ).encode()).decode()
