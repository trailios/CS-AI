from typing     import Dict
from requests   import get

from src.helpers.ProxyHelper import Proxy



class TimeZoneOffsets:
    _timezones: Dict[str, int] = {
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

    @classmethod
    def get_offset(cls, timezone: str) -> int:
        return cls._timezones.get(timezone, -120)

    @classmethod
    def list_timezones(cls) -> list[str]:
        return list(cls._timezones.keys())


def getIpInfo(proxy: Proxy) -> int:
    try:
        response = get(
            "https://pro.ip-api.com/json/?key=5mRuJtQYJhXOX8a", proxies=proxy.dict(), timeout=10
        ).json()

        timezone_str = response.get("timezone", "America/New_York")

        utc_offset = TimeZoneOffsets.get_offset(timezone_str)

        return utc_offset
    except Exception:
        return 0
