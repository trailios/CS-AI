import sys
import os
import uuid
import time
import random
from typing import Dict, Any, List
import json


src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

if src_path not in sys.path:
    sys.path.insert(0, src_path)
from utils.hash import x64hash128
from utils.versionInfo import get_version_info
from utils.presets import get_method, get_options
from fingerprint.bda.ordering import reorder_bda
fingerprints: List[str] = os.listdir("fpData")


def convert_to_dict(data_list):
    result: Dict[str, Any] = {}
    for item in data_list:
        key = item["key"]
        value = item["value"]
        if isinstance(value, list) and all(
            isinstance(i, dict) and "key" in i and "value" in i for i in value
        ):

            result[key] = convert_to_dict(value)
        else:
            result[key] = value
    return result


def fetch_random_fingerprint():
    with open("fpData/" + random.choice(fingerprints), "r", encoding="utf-8") as f:
        realfingerprint = json.load(f)
        return realfingerprint


def fetch_random_enhanced_fingerprint(data):
    enhanced_fp_entry = next(
        (item for item in data if item["key"] == "enhanced_fp"), None
    )
    if enhanced_fp_entry:
        enhanced_fp_values = {
            item["key"]: item["value"] for item in enhanced_fp_entry["value"]
        }
        return enhanced_fp_values


def enhanced_fp(method) -> dict:
    info = get_options(method)
    other_info = get_method(method)
    capiInfo = get_version_info(other_info["service_url"], other_info["public_key"])
    nonFormatted = fetch_random_fingerprint()
    arkoseBda = convert_to_dict(nonFormatted)
    enhanced_fp_data = fetch_random_enhanced_fingerprint(nonFormatted)
    bda = {
        "webgl_extensions": enhanced_fp_data["webgl_extensions"],
        "webgl_extensions_hash": enhanced_fp_data["webgl_extensions_hash"],
        "webgl_renderer": enhanced_fp_data["webgl_renderer"],
        "webgl_vendor": enhanced_fp_data["webgl_vendor"],
        "webgl_version": enhanced_fp_data["webgl_version"],
        "webgl_shading_language_version": enhanced_fp_data[
            "webgl_shading_language_version"
        ],
        "webgl_aliased_line_width_range": enhanced_fp_data[
            "webgl_aliased_line_width_range"
        ],
        "webgl_aliased_point_size_range": enhanced_fp_data[
            "webgl_aliased_point_size_range"
        ],
        "webgl_antialiasing": enhanced_fp_data["webgl_antialiasing"],
        "webgl_bits": enhanced_fp_data["webgl_bits"],
        "webgl_max_params": enhanced_fp_data["webgl_max_params"],
        "webgl_max_viewport_dims": enhanced_fp_data["webgl_max_viewport_dims"],
        "webgl_unmasked_vendor": enhanced_fp_data["webgl_unmasked_vendor"],
        "webgl_unmasked_renderer": enhanced_fp_data["webgl_unmasked_renderer"],
        "webgl_vsf_params": enhanced_fp_data["webgl_vsf_params"],
        "webgl_vsi_params": enhanced_fp_data["webgl_vsi_params"],
        "1f220c9":"4265a56c672d7e6aa6193578832fbe69",
        "webgl_fsf_params": enhanced_fp_data["webgl_fsf_params"],
        "webgl_fsi_params": enhanced_fp_data["webgl_fsi_params"],
        "webgl_hash_webgl": enhanced_fp_data["webgl_hash_webgl"],
        "user_agent_data_brands": "Chromium,Google Chrome,Not.A/Brand",
        "user_agent_data_mobile": False,
        "navigator_connection_downlink": 1.45,
        "navigator_connection_downlink_max": None,
        "network_info_rtt": 300,
        "network_info_save_data": False,
        "network_info_rtt_type": None,
        "screen_pixel_depth": 24,
        "navigator_device_memory": 8,
        "navigator_pdf_viewer_enabled": True,
        "navigator_languages": "en-US,en",
        "window_inner_width": 0,
        "window_inner_height": 0,
        "window_outer_width": 1050,
        "window_outer_height": 700,
        "browser_detection_firefox": False,
        "browser_detection_brave": False,
        "browser_api_checks": [
            "permission_status: True",
            "eye_dropper: True",
            "audio_data: True",
            "writable_stream: True",
            "css_style_rule: True",
            "navigator_ua: True",
            "barcode_detector: False",
            "display_names: True",
            "contacts_manager: False",
            "svg_discard_element: False",
            "usb: defined",
            "media_device: defined",
            "playback_quality: True",
        ],
        
        "browser_object_checks": "554838a8451ac36cb977e719e9d6623c",
        "29s83ih9": "68934a3e9455fa72420237eb05902327⁣",
        "audio_codecs": enhanced_fp_data["audio_codecs"],
        "audio_codecs_extended_hash": enhanced_fp_data["audio_codecs_extended_hash"],
        "video_codecs": enhanced_fp_data["video_codecs"],
        "video_codecs_extended_hash": enhanced_fp_data["video_codecs_extended_hash"],
        "media_query_dark_mode": False,
        "f9bf2db": '{"pc":"no-preference","ah":"hover","ap":"fine","p":"fine","h":"hover","u":"fast","prm":"no-preference","prt":"no-preference","s":"enabled","fc":"none"}',
        "headless_browser_phantom": True,
        "headless_browser_selenium": False,
        "headless_browser_nightmare_js": False,
        "headless_browser_generic": 4,
        "1l2l5234ar2": str(int(time.time()) * 1000) + "⁣",
        "document__referrer": info["document__referrer"],
        "window__ancestor_origins": info["window__ancestor_origins"],
        "window__tree_index": info["window__tree_index"],
        "window__tree_structure": info["window__tree_structure"],
        "window__location_href": info["window__location_href"],
        "client_config__sitedata_location_href": info[
            "client_config__sitedata_location_href"
        ],
        "client_config__language": other_info["language"],
        "client_config__surl": other_info["service_url"],
        "c8480e29a": info["c8480e29a"],
        "client_config__triggered_inline": info["client_config__triggered_inline"],
        "mobile_sdk__is_sdk": False,
        "audio_fingerprint": enhanced_fp_data["audio_fingerprint"],
        "audio_fingerprint": enhanced_fp_data["audio_fingerprint"],
        "navigator_battery_charging": True,
        "media_device_kinds": ["audioinput", "videoinput", "audiooutput"],
        "media_devices_hash": "199eba60310b53c200cc783906883c67",
        #"navigator_permissions_hash": "67419471976a14a1430378465782c62d",
        "math_fingerprint": "0ce80c69b75667d69baedc0a70c82da7",
        "supported_math_functions": "67d1759d7e92844d98045708c0a91c2f",
        "screen_orientation": "landscape-primary",
        "rtc_peer_connection": 5,
        "4b4b269e68": str(uuid.uuid4()),
        "6a62b2a558": capiInfo[1],
        "is_keyless": False,
        "c2d2015": "29d13b1af8803cb86c2697345d7ea9eb",
        "43f2d94": "63a34c42b4221e3d98b70281ab5e6160",
        "20c15922": True,
        "4f59ca8": None,
        "3ea7194": {"supported": True, "formats": ["HDR10", "HLG"], "isHDR": False},
        "05d3d24": "7bd8fe2b950ecd77778f4bf4c2c1b213",
        "speech_default_voice": enhanced_fp_data.get("speech_default_voice", "Microsoft Hedda - German (Germany) || de-DE"),
        "speech_voices_hash": enhanced_fp_data.get("speech_default_voice", "f8224b0bd046a07df30c0549fd055803"),
        "speech_default_voice": enhanced_fp_data.get("speech_default_voice",None),
        "speech_voices_hash": enhanced_fp_data["speech_voices_hash"],
        "83eb055": "7fa7f3064b181569c87529f62d07c386",
        "4ca87df3d1": "Ow==",
        "867e25e5d4": "Ow==",
        "d4a306884c": "Ow==",
    }
   
    if "roblox" in method:
        bda["window__location_href"] = info["client_config__sitedata_location_href"]
    bda = reorder_bda(bda)
    nonFormat = []
    for k, v in bda.items():
        nonFormat.append({"key": k, "value": v})
    return {"formatted":nonFormat,"realBdaUsed":arkoseBda,"nonFormatted":bda}

