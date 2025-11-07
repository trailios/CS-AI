from typing            import Optional, Dict, Any
from hashlib           import md5

from src.utils.parser import version_info


class Preset:
    
    method_data: Dict[str, Dict[str, Any]] = {
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
                    "document__referrer": data["site_url"] + "/",
                    "window__ancestor_origins": [],
                    "window__tree_index": data["tree_index"],
                    "window__tree_structure": data["structure"],
                    "window__location_href": data["location"],
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