from typing     import List, Dict, Iterator
from os         import listdir, urandom
from random     import choice, randint
from json       import loads, dumps
from time       import time, sleep
from base64     import b64encode
from threading  import Thread
from uuid       import uuid4

from src                        import Proxy
from src.utils.utils            import Utils
from src.utils.presets          import Preset
from src.utils.ipIntelligence   import getIpInfo
from src.utils.crypto           import rsa_encrypt
from src.utils.vm               import transform_payload

fps = listdir("db/fingerprints")
badfps = []

class BDA:
    def __init__(self,
                 userbrowser: str,
                 fp_iter: Iterator = None
    ) -> None:
        self.userbrowser: str = userbrowser

        self.fp_iter = fp_iter
        self.fingerprint:          List = loads(open(f"db/fingerprints/{next(self.fp_iter)}", encoding="utf-8").read()) # this is still moving fingerpint to next one every call btw

        self._start()

    def _background_run(self):
        while True:
            sleep(randint(20,60))
            self.fingerprint: List = loads(open(f"db/fingerprints/{next(self.fp_iter)}", encoding="utf-8").read())

    def _start(self):
        Thread(target=self._background_run, daemon=True).start()

    def _preprocess(self, fingerprint: List[Dict]):
        fingerprintDict = {}
        enhancedFingerprint = {}

        for item in fingerprint:
            key: str = item.get("key")
            value: str = item.get("value")
            fingerprintDict[key] = value
        
        for item in fingerprintDict["enhanced_fp"]:
            key: str = item.get("key")
            value: str = item.get("value")
            enhancedFingerprint[key] = value

        return fingerprintDict, enhancedFingerprint

    def update_fingerprint(
            self,
            proxy: Proxy,
            action: str,
            accept_lang: str,
            encryption_key: str,
            cbid: str
        ) -> str:
        timestamp = time()

        fingerprint = self.fingerprint.copy()

        options: Dict
        info :   Dict

        options, info = Preset.get_options(action)
        fingerprintDict, enhancedFingerprint = self._preprocess(fingerprint)

        fingerprintDict["n"] = str(
            b64encode(
                str(int(timestamp)).encode()
            ).decode()
        )
        fingerprintDict["wh"] = f"{urandom(16).hex()}|79169737225f825ee428975a81c22b8f"
        enhancedFingerprint["1l2l5234ar2"] = str(int(timestamp * 1000)) + "\u2063"
        enhancedFingerprint["6a62b2a558"] = info["hash"]
        enhancedFingerprint["29s83ih9"] = "68934a3e9455fa72420237eb05902327\u2063"
        enhancedFingerprint["navigator_languages"] = accept_lang.split(";")[0]
        enhancedFingerprint["4b4b269e68"] = str(uuid4())

        enhancedFingerprint["d4a306884c"] = "Ow=="
        enhancedFingerprint["4ca87df3d1"] = "Ow=="
        enhancedFingerprint["867e25e5d4"] = "Ow=="

        timeOffset = getIpInfo(proxy)

        feDict = {
            item.split(":")[0]: item.split(":")[1]
            for item in fingerprintDict["fe"]
        }
        feDict["L"] = accept_lang.split("-")[0]
        feDict["TO"] = str(timeOffset)
        #feDict["JSF"] = ""
        feDict["H"] = choice([8,12,16,24,32])
        feList = [
            f"{key}:{value}"
            for key, value in feDict.items()
        ]

        fingerprintDict["fe"] = feList
        fingerprintDict["f"] = Utils.x64hash128(
            ";".join(
                ",".join(
                    map(
                        str, v
                    ) if isinstance(v, list) else str(v)
                    for v in feDict
                )
            )
        )
        fingerprintDict["ife_hash"] = Utils.x64hash128(
            ", ".join(feList),
            38
        )

        fingerprintDict["jsbd"] = dumps( # thats what he does, HE DOES THAT 
            {"HL":str(randint(3,4)),"NCE":True,"DT":"Log in to Roblox","NWD":False,"DMTO":1,"DOTO":1}, # i put nce as string cause that's what he does
            separators=(",", ":")
        ) # dc

        for key, value in options.items():
            enhancedFingerprint[key] = value

        enhancedFingerprint["window__location_href"] = "https://www.roblox.com/login"

        fingerprintDict["enhanced_fp"] = [
            {"key": key, "value": value}
            for key, value in enhancedFingerprint.items()
        ]
        fingerprint = [
            {"key": key, "value": value}
            for key, value in fingerprintDict.items()
        ]

        fingerprint = transform_payload(
            fingerprint,
            cbid
        )

        fingerprint = dumps(
            fingerprint,
            separators=(",", ":"),
            ensure_ascii=False
        )

        encryptedfingerprint = rsa_encrypt(
                fingerprint,
                encryption_key
        )

        return encryptedfingerprint
        
    def set_badBda(self):
        ...