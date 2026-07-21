import json

import httpx

from app.core.config import settings
from app.core.redis_client import redis_client

THREAT_INTEL_CACHE_PREFIX = "threatintel:"
THREAT_INTEL_CACHE_TTL_SECONDS = 60 * 60 * 6


def check_ip_reputation(ip: str) -> dict | None:
    """
    Nice-to-have: checks a source IP against AbuseIPDB's free tier.
    Returns None gracefully (rather than raising) if no API key is
    configured, so this feature is fully optional and never blocks
    the core ingestion/detection pipeline.
    """
    if not settings.ABUSEIPDB_API_KEY:
        return None

    cache_key = f"{THREAT_INTEL_CACHE_PREFIX}{ip}"
    cached = redis_client.get(cache_key)
    if cached:
        return json.loads(cached)

    try:
        resp = httpx.get(
            "https://api.abuseipdb.com/api/v2/check",
            params={"ipAddress": ip, "maxAgeInDays": 90},
            headers={"Key": settings.ABUSEIPDB_API_KEY, "Accept": "application/json"},
            timeout=5.0,
        )
        data = resp.json().get("data", {})
        result = {
            "abuse_confidence_score": data.get("abuseConfidenceScore"),
            "total_reports": data.get("totalReports"),
            "is_known_malicious": (data.get("abuseConfidenceScore") or 0) >= 50,
            "country_code": data.get("countryCode"),
        }
        redis_client.setex(cache_key, THREAT_INTEL_CACHE_TTL_SECONDS, json.dumps(result))
        return result
    except (httpx.HTTPError, ValueError, KeyError):
        return None
