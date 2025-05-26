import requests
import pytz
from datetime import datetime


def getIpInfo(proxy: str) -> int:
    try:
        proxy_dict = {"http": f"http://{proxy}", "https": f"http://{proxy}"}

        response = requests.get(
            "https://api.ipify.org/?format=json", proxies=proxy_dict, timeout=10
        ).json()
        ip_address = response.get("ip", "")

        geo_data = requests.get(
            f"https://ipinfo.io/{ip_address}/json", proxies=proxy_dict, timeout=10
        ).json()

        timezone_str = geo_data.get("timezone", "America/New_York")

        tz = pytz.timezone(timezone_str)
        current_time = datetime.now(tz)
        utc_offset = int(current_time.utcoffset().total_seconds() / 60)

        return utc_offset
    except Exception:
        return 0
