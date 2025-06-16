from curl_cffi import requests as internal_session
def get_version_info(apiurl, sitekey):
    captchadata = internal_session.get(
        f"{apiurl}/v2/{sitekey}/api.js"
    ).text.split("/enforcement.")

    capi_version = captchadata[0].split('"')[-1]
    enforcement_hash = captchadata[1].split(".html")[0]
    return [capi_version, enforcement_hash]
