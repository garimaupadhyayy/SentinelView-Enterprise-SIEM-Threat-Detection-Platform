import ipaddress
import json
import math

import httpx

from app.core.config import settings
from app.core.redis_client import redis_client

GEOIP_CACHE_PREFIX = "geoip:"
GEOIP_CACHE_TTL_SECONDS = 60 * 60 * 24  # 24h, IP geolocation doesn't need to be fresh


def is_private_ip(ip: str) -> bool:
    try:
        return ipaddress.ip_address(ip).is_private
    except ValueError:
        return True


def lookup_ip(ip: str) -> dict | None:
    """
    Resolve an IP to {lat, lon, country, city} using the free ip-api.com
    endpoint, with a Redis cache so we don't hammer the free tier and so
    the dashboard's geo-map loads fast on repeat renders.
    """
    if is_private_ip(ip):
        return None

    cache_key = f"{GEOIP_CACHE_PREFIX}{ip}"
    cached = redis_client.get(cache_key)
    if cached:
        return json.loads(cached)

    try:
        url = settings.GEOIP_LOOKUP_URL.format(ip=ip)
        resp = httpx.get(url, timeout=3.0)
        data = resp.json()
        if data.get("status") == "success":
            result = {
                "lat": data.get("lat"),
                "lon": data.get("lon"),
                "country": data.get("country"),
                "city": data.get("city"),
                "isp": data.get("isp"),
            }
            redis_client.setex(cache_key, GEOIP_CACHE_TTL_SECONDS, json.dumps(result))
            return result
    except (httpx.HTTPError, ValueError, KeyError):
        pass
    return None


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    r = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))
