from utils.versionInfo import get_version_info
from typing import Optional, Dict, Any
import hashlib
def get_method(method):
        if method == "outlook":
            public_key = "B7D8911C-5CC8-A9A3-35B0-554ACEE604DA"
            service_url = "https://client-api.arkoselabs.com"
            site_url = "https://iframe.arkoselabs.com"
            capi_mode = "inline"
            language = "en"
        elif method == "twitter":
            public_key = "2CB16598-CB82-4CF7-B332-5990DB66F3AB"
            service_url = "https://client-api.arkoselabs.com"
            site_url = "https://iframe.arkoselabs.com"
            capi_mode = "inline"
            language = None
        elif method == "twitter_unlock":
            public_key = "0152B4EB-D2DC-460A-89A1-629838B529C9"
            service_url = "https://client-api.arkoselabs.com"
            site_url = "https://iframe.arkoselabs.com"
            capi_mode = "inline"
            language = None
        elif method == "roblox_signup":
            public_key = "A2A14B1D-1AF3-C791-9BBC-EE33CC7A0A6F"
            service_url = "https://arkoselabs.roblox.com"
            site_url = "https://www.roblox.com"
            capi_mode = "inline"
            language = None
        elif method == "roblox_login":
            public_key = "476068BF-9607-4799-B53D-966BE98E2B81"
            service_url = "https://arkoselabs.roblox.com"
            site_url = "https://www.roblox.com"
            capi_mode = "inline"
            language = None
        elif method == "roblox_join":
            public_key = "63E4117F-E727-42B4-6DAA-C8448E9B137F"
            service_url = "https://arkoselabs.roblox.com"
            site_url = "https://www.roblox.com"
            capi_mode = "inline"
            language = None
        elif method == "ea":
            public_key = "73BEC076-3E53-30F5-B1EB-84F494D43DBA"
            service_url = "https://ea-api.arkoselabs.com"
            site_url = "https://signin.ea.com"
            capi_mode = "lightbox"
            language = None
        elif method == "github-signup":
            public_key = "747B83EC-2CA3-43AD-A7DF-701F286FBABA"
            service_url = "https://github-api.arkoselabs.com"
            site_url = "https://octocaptcha.com"
            capi_mode = "inline"
            language = None
        elif method == "asurion":
            public_key = "8FC6BCF0-83CA-59A1-F97D-65E2322F5E70"
            service_url = "https://asurion-api.arkoselabs.com"
            site_url = "https://deviceprotection.phoneclaim.com"
            capi_mode = "lightbox"
            language = "en"
        elif method == "demo":
            public_key = "DF9C4D87-CB7B-4062-9FEB-BADB6ADA61E6"
            service_url = "https://client-api.arkoselabs.com"
            site_url = "https://demo.arkoselabs.com"
            capi_mode = "inline"
            language = "en"
        elif method == "roblox_wall":
            public_key = "63E4117F-E727-42B4-6DAA-C8448E9B137F"
            service_url = "https://arkoselabs.roblox.com"
            site_url = "https://www.roblox.com"
            capi_mode = "inline"
            language = None
        elif method == "airbnb-register":
            public_key = "2F0D6CB5-ACAC-4EA9-9B2A-A5F90A2DF15E"
            service_url = "https://airbnb-api.arkoselabs.com"
            site_url = "https://www.airbnb.com"
            capi_mode = "inline"
            language = "en"
        elif method == "battle.net":
            public_key = "CF5C61EE-F062-45DF-A32F-E9398E2B4E0D"
            service_url = "https://blizzard-api.arkoselabs.com"
            site_url = "https://eu.account.battle.net"
            capi_mode = "inline"
            language = None
        else:
            raise ValueError("Invalid method specified")
        return {
            "public_key": public_key,
            "service_url": service_url,
            "site_url": site_url,
            "capi_mode": capi_mode,
            "language": language,
        }
def hashing(data: Any) -> str:
    return hashlib.md5(data.encode() if isinstance(data, str) else data).hexdigest()

def get_options(method) -> None:
        if method == "outlook":
            siteKey = get_method(method)['public_key']
            options = {
                "document__referrer": "https://iframe.arkoselabs.com/",
                "window__ancestor_origins": [
                    "https://iframe.arkoselabs.com",
                    "https://signup.live.com",
                ],
                "window__tree_index": [1, 0],
                "window__tree_structure": "[[[]],[[]]]",
                #"window__location_href": f"https://client-api.arkoselabs.com/v2/{capi_version}/enforcement.{enforcement_hash}.html",
                "client_config__sitedata_location_href": f"https://iframe.arkoselabs.com/B7D8911C-5CC8-A9A3-35B0-554ACEE604DA/index.html",
                "client_config__language": "en",
                "client_config__surl": "https://client-api.arkoselabs.com",
                "c8480e29a": str(hashing("https://client-api.arkoselabs.com"))
                + "\u2062",
                "client_config__triggered_inline": False,
            }
            capi_version = get_version_info(options['client_config__surl'],siteKey)
            options["window__location_href"] = f"{options['client_config__surl']}/v2/{capi_version[0]}/enforcement.{capi_version[1]}.html"
        elif method == "twitter":
            siteKey = get_method(method)['public_key']
            options = {
                "document__referrer": "https://iframe.arkoselabs.com/",
                "window__ancestor_origins": [
                    "https://iframe.arkoselabs.com",
                    "https://twitter.com",
                ],
                "window__tree_index": [0, 0],
                "window__tree_structure": "[[[]]]",
                #"window__location_href": f"https://client-api.arkoselabs.com/v2/{capi_version}/enforcement.{enforcement_hash}.html",
                "client_config__sitedata_location_href": "https://iframe.arkoselabs.com/2CB16598-CB82-4CF7-B332-5990DB66F3AB/index.html",
                "client_config__language": None,
                "client_config__surl": "https://client-api.arkoselabs.com",
                "c8480e29a": str(hashing("https://client-api.arkoselabs.com"))
                + "\u2062",
                "client_config__triggered_inline": False,
            }
            capi_version = get_version_info(options['client_config__surl'],siteKey)
            options["window__location_href"] = f"{options['client_config__surl']}/v2/{capi_version[0]}/enforcement.{capi_version[1]}.html"
            
        elif method == "twitter_unlock":
            siteKey = get_method(method)['public_key']
            options = {
                "document__referrer": "https://iframe.arkoselabs.com/",
                "window__ancestor_origins": [
                    "https://iframe.arkoselabs.com",
                    "https://twitter.com",
                ],
                "window__tree_index": [0, 0],
                "window__tree_structure": "[[[]]]",
                #"window__location_href": f"https://client-api.arkoselabs.com/v2/{capi_version}/enforcement.{enforcement_hash}.html",
                "client_config__sitedata_location_href": "https://iframe.arkoselabs.com/0152B4EB-D2DC-460A-89A1-629838B529C9/index.html",
                "client_config__language": None,
                "client_config__surl": "https://client-api.arkoselabs.com",
                "c8480e29a": str(hashing("https://client-api.arkoselabs.com"))
                + "\u2062",
                "client_config__triggered_inline": False,
            }
            capi_version = get_version_info(options['client_config__surl'],siteKey)
            options["window__location_href"] = f"{options['client_config__surl']}/v2/{capi_version[0]}/enforcement.{capi_version[1]}.html"
        elif method == "roblox_signup":
            siteKey = get_method(method)['public_key']
            options = {
                "document__referrer": "https://www.roblox.com/",
                "window__ancestor_origins": [
                    "https://www.roblox.com",
                    "https://www.roblox.com",
                ],
                "window__tree_index": [1, 0],
                "window__tree_structure": "[[],[[]]]",
                #"window__location_href": f"https://arkoselabs.roblox.com/v2/{capi_version}/enforcement.{enforcement_hash}.html",
                "client_config__sitedata_location_href": f"https://www.roblox.com/de/arkose/iframe",
                "client_config__language": None,
                "client_config__surl": "https://arkoselabs.roblox.com",
                "c8480e29a": str(hashing("https://arkoselabs.roblox.com"))
                + "\u2062",
                "client_config__triggered_inline": False,
            }
            capi_version = get_version_info(options['client_config__surl'],siteKey)
            options["window__location_href"] = f"{options['client_config__surl']}/v2/{capi_version[0]}/enforcement.{capi_version[1]}.html"
        elif method == "roblox_login":
            siteKey = get_method(method)['public_key']
            options = {
                "document__referrer": "https://www.roblox.com/login",
                "window__ancestor_origins": [
                    "https://www.roblox.com",
                ],
                "window__tree_index": [1],
                "window__tree_structure":  "[[],[]]",
                #"window__location_href": f"https://arkoselabs.roblox.com/v2/{capi_version}/enforcement.{enforcement_hash}.html",
                "client_config__sitedata_location_href": "https://www.roblox.com/arkose/iframe",
                "client_config__language": None,
                "client_config__surl": "https://arkoselabs.roblox.com",
                "c8480e29a": str(hashing("https://arkoselabs.roblox.com"))
                + "\u2062",
                "client_config__triggered_inline": False,
            }
            capi_version = get_version_info(options['client_config__surl'],siteKey)
            options["window__location_href"] = f"{options['client_config__surl']}/v2/{capi_version[0]}/enforcement.{capi_version[1]}.html"
        elif method == "roblox_join" or method == "roblox_follow":
            siteKey = get_method(method)['public_key']
            options = {
                "document__referrer": "https://www.roblox.com/",
                "window__ancestor_origins": [
                    "https://www.roblox.com",
                    "https://www.roblox.com",
                ],
                "window__tree_index": [1, 0],
                "window__tree_structure": "[[],[[]]]",
                #"window__location_href": f"https://arkoselabs.roblox.com/v2/{capi_version}/enforcement.{enforcement_hash}.html",
                "client_config__sitedata_location_href": "https://www.roblox.com/de/arkose/iframe",
                "client_config__language": None,
                "client_config__surl": "https://arkoselabs.roblox.com",
                "c8480e29a": str(hashing("https://arkoselabs.roblox.com"))
                + "\u2062",
                "client_config__triggered_inline": False,
            }
            capi_version = get_version_info(options['client_config__surl'],siteKey)
            options["window__location_href"] = f"{options['client_config__surl']}/v2/{capi_version[0]}/enforcement.{capi_version[1]}.html"
        elif method == "ea":
            siteKey = get_method(method)['public_key']
            options = {
                "document__referrer": "https://signin.ea.com/",
                "window__ancestor_origins": [
                    "https://signin.ea.com",
                ],
                "window__tree_index": [0],
                "window__tree_structure": "[[]]",
                #"window__location_href": f"https://ea-api.arkoselabs.com/v2/{capi_version}/enforcement.{enforcement_hash}.html",
                "client_config__sitedata_location_href": "https://signin.ea.com/p/juno/create",
                "client_config__language": "en",
                "client_config__surl": "https://ea-api.arkoselabs.com",
                "c8480e29a": str(hashing("https://ea-api.arkoselabs.com"))
                + "\u2062",
                "client_config__triggered_inline": False,
            }
            capi_version = get_version_info(options['client_config__surl'],siteKey)
            options["window__location_href"] = f"{options['client_config__surl']}/v2/{capi_version[0]}/enforcement.{capi_version[1]}.html"
        elif method == "github-signup":
            siteKey = get_method(method)['public_key']
            options = {
                "document__referrer": "https://octocaptcha.com/",
                "window__ancestor_origins": [
                    "https://octocaptcha.com",
                    "https://github.com",
                ],
                "window__tree_index": [0, 0],
                "window__tree_structure": "[[[]],[]]",
                #"window__location_href": f"https://github-api.arkoselabs.com/v2/{capi_version}/enforcement.{enforcement_hash}.html",
                "client_config__sitedata_location_href": "https://octocaptcha.com/",
                "client_config__language": None,
                "client_config__surl": "https://github-api.arkoselabs.com",
                "c8480e29a": str(hashing("https://github-api.arkoselabs.com"))
                + "\u2062",
                "client_config__triggered_inline": False,
            }
            capi_version = get_version_info(options['client_config__surl'],siteKey)
            options["window__location_href"] = f"{options['client_config__surl']}/v2/{capi_version[0]}/enforcement.{capi_version[1]}.html"
        elif method == "asurion":
            siteKey = get_method(method)['public_key']
            options = {
                "document__referrer": "https://deviceprotection.phoneclaim.com/",
                "window__ancestor_origins": [
                    "https://deviceprotection.phoneclaim.com",
                ],
                "window__tree_index": [0],
                "window__tree_structure": "[[],[]]",
                #"window__location_href": f"https://asurion-api.arkoselabs.com/v2/{capi_version}/enforcement.{enforcement_hash}.html",
                "client_config__sitedata_location_href": "https://deviceprotection.phoneclaim.com/verizon/en-us/workflow/start#!",
                "client_config__language": "en",
                "client_config__surl": "https://asurion-api.arkoselabs.com",
                "c8480e29a": str(hashing("https://asurion-api.arkoselabs.com"))
                + "\u2062",
                "client_config__triggered_inline": False,
            }
            capi_version = get_version_info(options['client_config__surl'],siteKey)
            options["window__location_href"] = f"{options['client_config__surl']}/v2/{capi_version[0]}/enforcement.{capi_version[1]}.html"
        elif method == "demo":
            siteKey = get_method(method)['public_key']
            options = {
                "document__referrer": "https://login.microsoftonline.com/",
                "window__ancestor_origins": [
                    "https://demo.arkoselabs.com",
                ],
                "window__tree_index": [0],
                "window__tree_structure": "[[]]",
                #"window__location_href": f"https://cleint-api.arkoselabs.com/v2/{capi_version}/enforcement.{enforcement_hash}.html",
                "client_config__sitedata_location_href": "https://demo.arkoselabs.com/",
                "client_config__language": "en",
                "client_config__surl": "https://demo-api.arkoselabs.com",
                "c8480e29a": str(hashing("https://client-api.arkoselabs.com"))
                + "\u2062",
                "client_config__triggered_inline": False,
            }
            capi_version = get_version_info(options['client_config__surl'],siteKey)
            options["window__location_href"] = f"{options['client_config__surl']}/v2/{capi_version[0]}/enforcement.{capi_version[1]}.html"
        elif method == "roblox_wall":
            siteKey = get_method(method)['public_key']
            options = {
                "document__referrer": "https://www.roblox.com/",
                "window__ancestor_origins": [
                    "https://www.roblox.com",
                    "https://www.roblox.com",
                ],
                "window__tree_index": [1, 0],
                "window__tree_structure": "[[],[[]]]",
                #"window__location_href": f"https://arkoselabs.roblox.com/v2/{capi_version}/enforcement.{enforcement_hash}.html",
                "client_config__sitedata_location_href": "https://www.roblox.com/arkose/iframe",
                "client_config__language": None,
                "client_config__surl": "https://arkoselabs.roblox.com",
                "c8480e29a": str(hashing("https://arkoselabs.roblox.com"))
                + "\u2062",
                "client_config__triggered_inline": False,
            }
            capi_version = get_version_info(options['client_config__surl'],siteKey)
            options["window__location_href"] = f"{options['client_config__surl']}/v2/{capi_version[0]}/enforcement.{capi_version[1]}.html"
        elif method == "airbnb-register":
            siteKey = get_method(method)['public_key']
            options = {
                "document__referrer": "https://www.airbnb.com/",
                "window__ancestor_origins": [
                    "https://www.airbnb.com",
                ],
                "window__tree_index": [1],
                "window__tree_structure": "[[[]],[]]",
                #"window__location_href": f"https://airbnb-api.arkoselabs.com/v2/{capi_version}/enforcement.{enforcement_hash}.html",
                "client_config__sitedata_location_href": "https://www.airbnb.com/",
                "client_config__language": "en",
                "client_config__surl": "https://airbnb-api.arkoselabs.com",
                "c8480e29a": str(hashing("https://airbnb-api.arkoselabs.com"))
                + "\u2062",
                "client_config__triggered_inline": False,
            }
            capi_version = get_version_info(options['client_config__surl'],siteKey)
            options["window__location_href"] = f"{options['client_config__surl']}/v2/{capi_version[0]}/enforcement.{capi_version[1]}.html"
        elif method == "battle.net":
            siteKey = get_method(method)['public_key']
            options = {
                "document__referrer": "https://eu.account.battle.net/",
                "window__ancestor_origins": [
                    "https://eu.account.battle.net",
                ],
                "window__tree_index": [0],
                "window__tree_structure": "[[]]",
                #"window__location_href": f"https://blizzard-api.arkoselabs.com/v2/{capi_version}/enforcement.{enforcement_hash}.html",
                "client_config__sitedata_location_href": "https://www.battle.net/",
                "client_config__language": "en",
                "client_config__surl": "https://blizzard-api.arkoselabs.com",
                "c8480e29a": str(hashing("https://blizzard-api.arkoselabs.com"))
                + "\u2062",
                "client_config__triggered_inline": False,
            }
            capi_version = get_version_info(options['client_config__surl'],siteKey)
            options["window__location_href"] = f"{options['client_config__surl']}/v2/{capi_version[0]}/enforcement.{capi_version[1]}.html"
        else:
            raise Exception("Invalid method")
        return options

print(get_options('roblox_login'))  # This will print the options for the 'roblox_signup' method