from random     import choice, randint
from json       import loads, dumps
from typing     import List, Dict
from base64     import b64encode
from os         import listdir
from uuid       import uuid4
from time       import time

from src                        import Proxy
from src.utils.utils            import Utils
from src.utils.presets          import Preset
from src.utils.ipIntelligence   import getIpInfo
from src.utils.crypto           import AES_Crypto

fps = listdir("db/fingerprints")

class BDA:
    def __init__(self, 
                 proxy: Proxy, 
                 action: str, 
                 userbrowser: str, 
                 accept_language: str = "en-US,de-DE"
    ) -> None:
        self.proxy: Proxy     = proxy
        self.action: str      = action
        self.userbrowser: str = userbrowser
        self.accept_lang      = accept_language

        self.options: Dict[str, str]
        self.info:    Dict[str, str]

        self.options, self.info = Preset.get_options(self.action)
        
        self.fingerprint:          List = loads(open(f"db/fingerprints/{choice(fps)}", encoding="utf-8").read())
        self.fingerprintDict:      Dict = {}
        self.enhancedFingerprint:  Dict = {}
        self.encryptedfingerprint: str = ""

        self._preprocess()

    def _preprocess(self):
        for item in self.fingerprint:
            key: str = item.get("key")
            value: str = item.get("value")
            self.fingerprintDict[key] = value
        
        for item in self.fingerprintDict["enhanced_fp"]:
            key: str = item.get("key")
            value: str = item.get("value")
            self.enhancedFingerprint[key] = value

    def update_fingerprint(self):
        timestamp = time()

        self.fingerprintDict["n"] = str(
            b64encode(
                str(int(timestamp)).encode()
            ).decode()
        )
        self.enhancedFingerprint["1l2l5234ar2"] = str(int(timestamp * 1000)) + "\u2063"
        self.enhancedFingerprint["6a62b2a558"] = self.info["hash"]
        self.enhancedFingerprint["29s83ih9"] = "68934a3e9455fa72420237eb05902327\u2063"
        self.enhancedFingerprint["navigator_languages"] = self.accept_lang.split(",")[0]
        self.enhancedFingerprint["4b4b269e68"] = str(uuid4())
        self.enhancedFingerprint["43f2d94"] = [
            "MetaMask",
            "Tron Web (likely TronLink)"
        ]

        if choice([True, False]):
            self.enhancedFingerprint["43f2d94"].append("Phantom")

        self.enhancedFingerprint["d4a306884c"] = "Ow=="
        self.enhancedFingerprint["4ca87df3d1"] = "Ow=="
        self.enhancedFingerprint["867e25e5d4"] = "Ow=="

        timeOffset = getIpInfo(self.proxy)

        feDict = {
            item.split(":")[0]: item.split(":")[1]
            for item in self.fingerprintDict["fe"]
        }
        feDict["L"] = self.accept_lang.split("-")[0]
        feDict["TO"] = str(timeOffset)
        feDict["JSF"] = None # not sure if its the same still for brolxo
        feDict["H"] = choice([2,4,8,6,16,12,32,24])
        feList = [
            f"{key}:{value}"
            for key, value in feDict.items()
        ]

        self.fingerprintDict["fe"] = feList
        self.fingerprintDict["f"] = Utils.x64hash128(
            ";".join(
                ",".join(
                    map(
                        str, v
                    ) if isinstance(v, list) else str(v)
                    for v in feDict
                )
            )
        )
        self.fingerprintDict["ife_hash"] = Utils.x64hash128(
            ", ".join(feList),
            38
        )

        self.fingerprintDict["jsbd"] = dumps(
            {"HL":int(randint(3,17)),"NCE":True,"DT":"","NWD":"false","DMTO":1,"DOTO":1}
        )

        for key, value in self.options.items():
            self.enhancedFingerprint[key] = value


        self.fingerprintDict["enhanced_fp"] = [
            {"key": key, "value": value}
            for key, value in self.enhancedFingerprint.items()
        ]
        self.fingerprint = [
            {"key": key, "value": value}
            for key, value in self.fingerprintDict.items()
        ]
        
        # slowly going insane after 3 hours debugging in all files...

        self.fingerprint = dumps(
            self.fingerprint,
        )

        if choice([0,0,0,1]):
            pos = randint(0, len(self.fingerprint) - 1)
            self.fingerprint = self.fingerprint[:pos] + '"' + self.fingerprint[pos:]

        self.encryptedfingerprint = b64encode(
            AES_Crypto.encrypt_data(
                self.fingerprint,
                self.userbrowser + str(int(t := timestamp) - int(t) % 21600)
            ).encode("utf-8")
        ).decode("utf-8")