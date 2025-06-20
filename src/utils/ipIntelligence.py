import requests

from src.helpers.ProxyHelper import Proxy

from typing import Dict, Optional


class TimeZoneOffsets:
    def __init__(self) -> None:
        self._timezones: Dict[str, int] = {
            "Europe/London": 0,
            "Europe/Berlin": 60,
            "Europe/Moscow": 180,
            "Africa/Lagos": 60,
            "Africa/Cairo": 120,
            "Africa/Nairobi": 180,
            "Asia/Dubai": 240,
            "Asia/Karachi": 300,
            "Asia/Kolkata": 330,
            "Asia/Dhaka": 360,
            "Asia/Bangkok": 420,
            "Asia/Shanghai": 480,
            "Asia/Tokyo": 540,
            "Australia/Sydney": 600,
            "Pacific/Auckland": 720,
            "Pacific/Honolulu": -600,
            "America/Anchorage": -540,
            "America/Los_Angeles": -480,
            "America/Denver": -420,
            "America/Chicago": -360,
            "America/New_York": -300,
            "America/Caracas": -240,
            "America/Sao_Paulo": -180,
            "Atlantic/Azores": -60,
        }

    def get_offset(self, timezone: str) -> Optional[int]:
        return self._timezones.get(timezone, -120)

    def list_timezones(self) -> list[str]:
        return list(self._timezones.keys())


def getIpInfo(proxy: Proxy) -> int:
    try:
        response = requests.get(
            "https://api.ipify.org/?format=json", proxies=proxy.dict(), timeout=10
        ).json()
        ip_address = response.get("ip", "")

        geo_data = requests.get(
            f"https://ipinfo.io/{ip_address}/json", proxies=proxy.dict(), timeout=10
        ).json()

        timezone_str = geo_data.get("timezone", "America/New_York")

        timetones = TimeZoneOffsets()
        utc_offset = timetones.get_offset(timezone_str) or -120  # <-- falllback

        return utc_offset
    except Exception:
        return 0
