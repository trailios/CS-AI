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

fps = listdir("db/safari")
badfps = []

class BDA:
    def __init__(self,
                 userbrowser: str,
                 fp_iter: Iterator = None
    ) -> None:
        self.userbrowser: str = userbrowser

        self.fp_iter = fp_iter
        self.fingerprint:          List = loads(open(f"db/safari/{next(self.fp_iter)}", encoding="utf-8").read()) # this is still moving fingerpint to next one every call btw

        self._start()

    def _background_run(self):
        pass
        # while True:
        #     sleep(randint(0.01,2))
        #     self.fingerprint: List = loads(open(f"db/fingerprints/{next(self.fp_iter)}", encoding="utf-8").read())

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
        self.fingerprint: List = loads(open(f"db/safari/{next(self.fp_iter)}", encoding="utf-8").read())
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
        #fingerprintDict["wh"] = f"{urandom(16).hex()}|1d99c2530fa1a96e676f9b1a1a9bcb58" #why do u do ts
        enhancedFingerprint["1l2l5234ar2"] = str(int(timestamp * 1000)) + "\u2063"
        enhancedFingerprint["6a62b2a558"] = info["hash"]
        enhancedFingerprint["29s83ih9"] = "68934a3e9455fa72420237eb05902327" + "\u2063"  # md5 of action
        # enhancedFingerprint["navigator_languages"] = "de-DE"
        # enhancedFingerprint["4b4b269e68"] = str(uuid4())
        # enhancedFingerprint["speech_voices_hash"] = "a0c90ca98043f0489c1e731e233b937e"
        # enhancedFingerprint["speech_default_voice"] = "Google Deutsch || de-DE"
        # enhancedFingerprint["4ca87df3d1"] = "Ow=="
        # enhancedFingerprint["7541c2s"] = None
        # enhancedFingerprint["05d3d24"] = "40e14a53f514b3d6792e2d8072aa5c37"

        try:
            fingerprintDict.pop("fb")
        except KeyError:
            pass

        # timeOffset = getIpInfo(proxy)

        feDict = {
            item.split(":")[0]: item.split(":")[1]
            for item in fingerprintDict["fe"]
        }
        #1s
        # feDict["L"] = "de-DE" #accept_lang.split(";")[0]
        # feDict["TO"] = "-60" 
        # #feDict["JSF"] = ""
        # feList = [
        #     f"{key}:{value}"
        #     for key, value in feDict.items()
        # ]

        # fingerprintDict["fe"] = feList
        # fingerprintDict["f"] = Utils.x64hash128(
        #     ";".join(
        #         ",".join(
        #             map(
        #                 str, v
        #             ) if isinstance(v, list) else str(v)
        #             for v in feDict
        #         )
        #     )
        # )
        # fingerprintDict["ife_hash"] = Utils.x64hash128(
        #     ", ".join(feList),
        #     38
        # )

        fingerprintDict["jsbd"] = dumps( # thats what he does, HE DOES THAT 
            {"HL":3,"NCE":True,"DT":"Log in to Roblox","NWD":"false","DMTO":1,"DOTO":1}, # i put nwd as string cause that's what he does
            separators=(",", ":")
        ) # dc

        for key, value in options.items():
            enhancedFingerprint[key] = value

        enhancedFingerprint["window__location_href"] = "https://www.roblox.com/Login"
        enhancedFingerprint["client_config__sitedata_location_href"] = "https://www.roblox.com/Login"

        fingerprintDict["enhanced_fp"] = [
            {"key": key, "value": value}
            for key, value in enhancedFingerprint.items()
        ]
        fingerprint = [
            {"key": key, "value": value}
            for key, value in fingerprintDict.items()
        ]

        # fingerprint = transform_payload(
        #     fingerprint,
        #     cbid
        # )

        fingerprint = dumps(
            fingerprint,
            separators=(",", ":"),
            ensure_ascii=False
        )

        encryptedfingerprint = rsa_encrypt(
                fingerprint,
                encryption_key
        )

        return encryptedfingerprint, fingerprint
        
    def set_badBda(self):
        ...