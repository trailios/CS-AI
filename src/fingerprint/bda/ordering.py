

real_order = ['webgl_extensions', 'webgl_extensions_hash', 'webgl_renderer', 'webgl_vendor', 'webgl_version', 'webgl_shading_language_version', 'webgl_aliased_line_width_range', 'webgl_aliased_point_size_range', 'webgl_antialiasing', 'webgl_bits', 'webgl_max_params', 'webgl_max_viewport_dims', 'webgl_unmasked_vendor', 'webgl_unmasked_renderer', 'webgl_vsf_params', 'webgl_vsi_params', 'webgl_fsf_params', 'webgl_fsi_params', 'webgl_hash_webgl', 'user_agent_data_brands', 'user_agent_data_mobile', 'navigator_connection_downlink', 'navigator_connection_downlink_max', 'network_info_rtt', 'network_info_save_data', 'network_info_rtt_type', 'screen_pixel_depth', 'navigator_device_memory', 'navigator_pdf_viewer_enabled', 'navigator_languages', 'window_inner_width', 'window_inner_height', 'window_outer_width', 'window_outer_height', 'browser_detection_firefox', 'browser_detection_brave', 'browser_api_checks', 'browser_object_checks', '29s83ih9', 'audio_codecs', 'audio_codecs_extended_hash', 'video_codecs', 'video_codecs_extended_hash', 'media_query_dark_mode', 'f9bf2db', 'headless_browser_phantom', 'headless_browser_selenium', 'headless_browser_nightmare_js', 'headless_browser_generic', '1l2l5234ar2', 'document__referrer', 'window__ancestor_origins', 'window__tree_index', 'window__tree_structure', 'window__location_href', 'client_config__sitedata_location_href', 'client_config__language', 'client_config__surl', 'c8480e29a', 'client_config__triggered_inline', 'mobile_sdk__is_sdk', 'audio_fingerprint', 'navigator_battery_charging', 'media_device_kinds', 'media_devices_hash', '1f220c9', 'math_fingerprint', 'supported_math_functions', 'screen_orientation', 'rtc_peer_connection', '4b4b269e68', '6a62b2a558', 'is_keyless', 'c2d2015', '43f2d94', '20c15922', '4f59ca8', '3ea7194', '05d3d24', 'speech_default_voice', 'speech_voices_hash', '83eb055', '4ca87df3d1', '867e25e5d4', 'd4a306884c']

def reorder_bda(bda: dict) -> dict:
    # Step 1: Create a new dict in the exact order
    ordered_bda = {key: bda.get(key, None) for key in real_order}
    # If any key not present the missing one
    
    # Step 2: Include any extra keys from bda that aren't in real_order
    for key in bda:
        if key not in real_order:
            ordered_bda[key] = bda[key]

    return ordered_bda
