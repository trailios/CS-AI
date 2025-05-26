from curl_cffi import requests

def get_version_info(apiurl,sitekey):
        captchadata=requests.get(f"{apiurl}/v2/{sitekey}/api.js",headers={'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7','accept-language': f'en-US,en;q=0.9,{locale};q=0.8,{locale.split("-")[0]};q=0.7','cache-control': 'max-age=0','device-memory': '8','priority': 'u=0, i','sec-ch-dpr': '1','sec-ch-ua': '"Google Chrome";v="129", "Not=A?Brand";v="8", "Chromium";v="129"','sec-ch-ua-arch': '"x86"','sec-ch-ua-bitness': '"64"','sec-ch-ua-form-factors': '"Desktop"','sec-ch-ua-full-version-list': '"Google Chrome";v="129.0.6668.60", "Not=A?Brand";v="8.0.0.0", "Chromium";v="129.0.6668.60"','sec-ch-ua-mobile': '?0','sec-ch-ua-model': '""','sec-ch-ua-platform': '"Windows"','sec-ch-ua-platform-version': '"10.0.0"','sec-ch-viewport-width': '1133','sec-fetch-dest': 'document','sec-fetch-mode': 'navigate','sec-fetch-site': 'none','sec-fetch-user': '?1','upgrade-insecure-requests': '1','user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36',}
        ).text.split("/enforcement.")

        capi_version=captchadata[0].split('"')[-1]
        enforcement_hash=captchadata[1].split('.html')[0]
        return [capi_version, enforcement_hash]
