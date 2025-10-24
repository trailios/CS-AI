from typing            import Optional, Dict, Any
from hashlib           import md5

from src.utils.parser import version_info


class Preset:
    
    method_data: Dict[str, Dict[str, Any]] = {
        "outlook": {
            "public_key": "B7D8911C-5CC8-A9A3-35B0-554ACEE604DA",
            "service_url": "https://client-api.arkoselabs.com",
            "site_url": "https://iframe.arkoselabs.com",
            "capi_mode": "inline",
            "language": "en",
            "origin": "https://signup.live.com",
            "location": "https://iframe.arkoselabs.com/B7D8911C-5CC8-A9A3-35B0-554ACEE604DA/index.html",
            "tree_index": [1, 0],
            "structure": "[[[]],[[]]]"
        },
        "twitter": {
            "public_key": "2CB16598-CB82-4CF7-B332-5990DB66F3AB",
            "service_url": "https://client-api.arkoselabs.com",
            "site_url": "https://iframe.arkoselabs.com",
            "capi_mode": "inline",
            "language": None,
            "origin": "https://twitter.com",
            "location": "https://iframe.arkoselabs.com/2CB16598-CB82-4CF7-B332-5990DB66F3AB/index.html",
            "tree_index": [0, 0],
            "structure": "[[[]]]"
        },
        "twitter_unlock": {
            "public_key": "0152B4EB-D2DC-460A-89A1-629838B529C9",
            "service_url": "https://client-api.arkoselabs.com",
            "site_url": "https://iframe.arkoselabs.com",
            "capi_mode": "inline",
            "language": None,
            "origin": "https://twitter.com",
            "location": "https://iframe.arkoselabs.com/0152B4EB-D2DC-460A-89A1-629838B529C9/index.html",
            "tree_index": [0, 0],
            "structure": "[[[]]]"
        },
        "roblox_signup": {
            "public_key": "A2A14B1D-1AF3-C791-9BBC-EE33CC7A0A6F",
            "service_url": "https://arkoselabs.roblox.com",
            "site_url": "https://www.roblox.com",
            "capi_mode": "lightbox",
            "language": None,
            "origin": "https://www.roblox.com/",
            "location": "https://www.roblox.com",
            "tree_index": [],
            "structure": "[]"
        },
        "roblox_login": {
            "public_key": "476068BF-9607-4799-B53D-966BE98E2B81",
            "service_url": "https://arkoselabs.roblox.com",
            "site_url": "https://www.roblox.com",
            "capi_mode": "lightbox",
            "language": None,
            "origin": "https://www.roblox.com/login",
            "location": "https://www.roblox.com/login",
            "tree_index": [],
            "structure": "[[],[[]]]"
        },
        "roblox_join": {
            "public_key": "63E4117F-E727-42B4-6DAA-C8448E9B137F",
            "service_url": "https://arkoselabs.roblox.com",
            "site_url": "https://www.roblox.com",
            "capi_mode": "inline",
            "language": None,
            "origin": "https://www.roblox.com",
            "location": "https://www.roblox.com/arkose/iframe",
            "tree_index": [1, 0],
            "structure": "[[],[[]]]"
        },
        "roblox_support": {
            "public_key": "63E4117F-E727-42B4-6DAA-C8448E9B137F",
            "service_url": "https://arkoselabs.roblox.com",
            "site_url": "https://www.roblox.com",
            "capi_mode": "inline",
            "language": None,
            "origin": "https://www.roblox.com",
            "location": "https://www.roblox.com/arkose/iframe",
            "tree_index": [1, 0],
            "structure": "[[],[]]"
        },
        "ea": {
            "public_key": "73BEC076-3E53-30F5-B1EB-84F494D43DBA",
            "service_url": "https://ea-api.arkoselabs.com",
            "site_url": "https://signin.ea.com",
            "capi_mode": "lightbox",
            "language": None,
            "location": "https://signin.ea.com/p/juno/create",
            "tree_index": [0],
            "structure": "[[]]",
        },
        "github-signup": {
            "public_key": "747B83EC-2CA3-43AD-A7DF-701F286FBABA",
            "service_url": "https://github-api.arkoselabs.com",
            "site_url": "https://octocaptcha.com",
            "capi_mode": "inline",
            "language": None,
            "origin": "https://github.com",
            "location": "https://octocaptcha.com/",
            "tree_index": [0, 0],
            "structure": "[[[]],[]]"
        },
        "asurion": {
            "public_key": "8FC6BCF0-83CA-59A1-F97D-65E2322F5E70",
            "service_url": "https://asurion-api.arkoselabs.com",
            "site_url": "https://deviceprotection.phoneclaim.com",
            "capi_mode": "lightbox",
            "language": "en",
            "location": "https://deviceprotection.phoneclaim.com/verizon/en-us/workflow/start#!",
            "tree_index": [0],
            "structure": "[[],[]]",
        },
        "demo": {
            "public_key": "DF9C4D87-CB7B-4062-9FEB-BADB6ADA61E6",
            "service_url": "https://client-api.arkoselabs.com",
            "site_url": "https://demo.arkoselabs.com",
            "capi_mode": "inline",
            "language": "en",
            "location": "https://demo.arkoselabs.com/",
            "tree_index": [0],
            "structure": "[[]]",
        },
        "roblox_wall": {
            "public_key": "63E4117F-E727-42B4-6DAA-C8448E9B137F",
            "service_url": "https://arkoselabs.roblox.com",
            "site_url": "https://www.roblox.com",
            "capi_mode": "inline",
            "language": None,
            "origin": "https://www.roblox.com/login",
            "location": "https://www.roblox.com/login",
            "tree_index": [],
            "structure": "[]"
        },
        "airbnb-register": {
            "public_key": "2F0D6CB5-ACAC-4EA9-9B2A-A5F90A2DF15E",
            "service_url": "https://airbnb-api.arkoselabs.com",
            "site_url": "https://www.airbnb.com",
            "capi_mode": "inline",
            "language": "en",
            "location": "https://www.airbnb.com",
            "tree_index": [1],
            "structure": "[[[]],[]]"
        },
        "battle.net": {
            "public_key": "CF5C61EE-F062-45DF-A32F-E9398E2B4E0D",
            "service_url": "https://blizzard-api.arkoselabs.com",
            "site_url": "https://eu.account.battle.net",
            "capi_mode": "inline",
            "language": None,
            "location": "https://www.battle.net",
            "tree_index": [0],
            "structure": "[[]]",
        },
        "match.com": {
            "public_key": "85800716-F435-4981-864C-8B90602D10F7",
            "service_url": "https://client-api.arkoselabs.com",
            "site_url": "https://us.match.com",
            "capi_mode": "lightbox",
            "language": None,
            "location": "https://us.match.com/login",
            "tree_index": [1],
            "structure": "[[],[],[[]],[]]"
        }
    }
    
    @staticmethod
    def hash(data: Any) -> str:
        
        return md5(
            data.encode() if isinstance(data, str) else data
            ).hexdigest()

    @staticmethod
    def get_options(method: str) -> Optional[Dict[str, Any]]:
        
        for key, data in Preset.method_data.items():
            if key == method:
                capi_version, enforcement_hash, cbid = version_info(data["service_url"], data["public_key"])
                
                options: dict = {
                    "document__referrer": data["site_url"] + "/home" if not method == "roblox_support" else data["site_url"] + "/support",
                    "window__ancestor_origins": [],
                    "window__tree_index": data["tree_index"],
                    "window__tree_structure": data["structure"],
                    "window__location_href": f"{data["service_url"]}/v2/{capi_version}/enforcement.{enforcement_hash}.html",
                    "client_config__sitedata_location_href": data["location"],
                    "client_config__language": data["language"],
                    "client_config__surl": data["service_url"],
                    "c8480e29a": str(Preset.hash(data["service_url"])) + "\u2062",
                    "client_config__triggered_inline": False,
                }

                info: dict = {
                    "pkey": data["public_key"],
                    "surl": data["service_url"],
                    "url": data["site_url"],
                    "cmode": data["capi_mode"],
                    "lang": data["language"],
                    "ver": capi_version,
                    "hash": enforcement_hash
                }


                    
        if options:
            return options, info
        
        else:
            raise ValueError(f"{method} is not a valid method.")