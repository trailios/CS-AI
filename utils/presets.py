from versionInfo import get_version_info
from typing import Optional, Dict, Any
import hashlib

def hashing(data: Any) -> str:
    return hashlib.md5(data.encode() if isinstance(data, str) else data).hexdigest()

def get_options(method) -> None:
        if method == "outlook":
            
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
            capi_version = get_version_info(options['client_config__surl'],options['client_config__sitedata_location_href'].split('roblox.com/')[1].split('/')[0])
            options["window__location_href"] = f"{options['client_config__surl']}/v2/{capi_version[0]}/enforcement.{capi_version[1]}.html"
        elif method == "twitter":
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
            capi_version = get_version_info(options['client_config__surl'],options['client_config__sitedata_location_href'].split('roblox.com/')[1].split('/')[0])
            options["window__location_href"] = f"{options['client_config__surl']}/v2/{capi_version[0]}/enforcement.{capi_version[1]}.html"
            
        elif method == "twitter_unlock":
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
            capi_version = get_version_info(options['client_config__surl'],options['client_config__sitedata_location_href'].split('roblox.com/')[1].split('/')[0])
            options["window__location_href"] = f"{options['client_config__surl']}/v2/{capi_version[0]}/enforcement.{capi_version[1]}.html"
        elif method == "roblox_signup":
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
            capi_version = get_version_info(options['client_config__surl'],options['client_config__sitedata_location_href'].split('roblox.com/')[1].split('/')[0])
            options["window__location_href"] = f"{options['client_config__surl']}/v2/{capi_version[0]}/enforcement.{capi_version[1]}.html"
        elif method == "roblox_login":
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
            capi_version = get_version_info(options['client_config__surl'],options['client_config__sitedata_location_href'].split('roblox.com/')[1].split('/')[0])
            options["window__location_href"] = f"{options['client_config__surl']}/v2/{capi_version[0]}/enforcement.{capi_version[1]}.html"
        elif method == "roblox_join" or method == "roblox_follow":
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
            capi_version = get_version_info(options['client_config__surl'],options['client_config__sitedata_location_href'].split('roblox.com/')[1].split('/')[0])
            options["window__location_href"] = f"{options['client_config__surl']}/v2/{capi_version[0]}/enforcement.{capi_version[1]}.html"
        elif method == "ea":
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
            capi_version = get_version_info(options['client_config__surl'],options['client_config__sitedata_location_href'].split('roblox.com/')[1].split('/')[0])
            options["window__location_href"] = f"{options['client_config__surl']}/v2/{capi_version[0]}/enforcement.{capi_version[1]}.html"
        elif method == "github-signup":
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
            capi_version = get_version_info(options['client_config__surl'],options['client_config__sitedata_location_href'].split('roblox.com/')[1].split('/')[0])
            options["window__location_href"] = f"{options['client_config__surl']}/v2/{capi_version[0]}/enforcement.{capi_version[1]}.html"
        elif method == "asurion":
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
            capi_version = get_version_info(options['client_config__surl'],options['client_config__sitedata_location_href'].split('roblox.com/')[1].split('/')[0])
            options["window__location_href"] = f"{options['client_config__surl']}/v2/{capi_version[0]}/enforcement.{capi_version[1]}.html"
        elif method == "demo":
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
            capi_version = get_version_info(options['client_config__surl'],options['client_config__sitedata_location_href'].split('roblox.com/')[1].split('/')[0])
            options["window__location_href"] = f"{options['client_config__surl']}/v2/{capi_version[0]}/enforcement.{capi_version[1]}.html"
        elif method == "roblox_wall":
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
            capi_version = get_version_info(options['client_config__surl'],options['client_config__sitedata_location_href'].split('roblox.com/')[1].split('/')[0])
            options["window__location_href"] = f"{options['client_config__surl']}/v2/{capi_version[0]}/enforcement.{capi_version[1]}.html"
        elif method == "airbnb-register":
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
        elif method == "battle.net":
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
        else:
            raise Exception("Invalid method")