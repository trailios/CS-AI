from curl_cffi import requests

headers = {
    'accept': '*/*',
    'accept-language': 'en-US,en;q=0.9',
    'cache-control': 'no-cache',
    'pragma': 'no-cache',
    'referer': 'https://www.roblox.com/',
    'sec-ch-ua': '"Chromium";v="136", "Google Chrome";v="136", "Not.A/Brand";v="99"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'script',
    'sec-fetch-mode': 'no-cors',
    'sec-fetch-site': 'same-site',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36',
    # 'cookie': 'RBXEventTrackerV2=CreateDate=05/25/2025 08:01:11&rbxid=&browserid=1748178071985001; GuestData=UserID=-2088128126; RBXSource=rbx_acquisition_time=05/25/2025 13:01:17&rbx_acquisition_referrer=https://www.roblox.com/login&rbx_medium=Social&rbx_source=www.roblox.com&rbx_campaign=&rbx_adgroup=&rbx_keyword=&rbx_matchtype=&rbx_send_info=0; _cfuvid=2Tcy_EqLJ0qhYnviOGCTm_1P9sZBMu9.hAx5FSqz2z4-1717104076479-0.0.1.1-604800000; rbx-ip2=1',
}
def get_version_info(apiurl,sitekey):
        captchadata=requests.get(f"{apiurl}/v2/{sitekey}/api.js",headers=headers
        ).text.split('/enforcement.')

        capi_version=captchadata[0].split('"')[-1]
        enforcement_hash=captchadata[1].split('.html')[0]
        return [capi_version, enforcement_hash]
        