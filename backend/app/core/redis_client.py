import logging

import redis

from app.core.config import settings

logger = logging.getLogger("sentinelview.redis")

if settings.REDIS_URL:
    # Preferred path for managed providers: one URL already encodes host,
    # port, password, and whether TLS is required (rediss:// vs redis://).
    redis_client = redis.Redis.from_url(
        settings.REDIS_URL,
        decode_responses=True,
        socket_connect_timeout=3,
        socket_timeout=3,
    )
else:
    # Fallback for local docker-compose, where mysql/redis have no
    # password and no TLS, so separate plain fields are simpler.
    redis_client = redis.Redis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        db=settings.REDIS_DB,
        password=settings.REDIS_PASSWORD or None,
        ssl=settings.REDIS_SSL,
        decode_responses=True,
        socket_connect_timeout=3,
        socket_timeout=3,
    )


def redis_safe_get(key: str) -> str | None:
    """Wraps redis GET so a Redis outage degrades a feature (dedup/cache)
    instead of crashing the whole request."""
    try:
        return redis_client.get(key)
    except redis.exceptions.RedisError as exc:
        logger.warning("Redis GET failed for key=%s: %s", key, exc)
        return None


def redis_safe_setex(key: str, ttl_seconds: int, value) -> bool:
    try:
        redis_client.setex(key, ttl_seconds, value)
        return True
    except redis.exceptions.RedisError as exc:
        logger.warning("Redis SETEX failed for key=%s: %s", key, exc)
        return False


def redis_safe_expire(key: str, ttl_seconds: int) -> bool:
    try:
        redis_client.expire(key, ttl_seconds)
        return True
    except redis.exceptions.RedisError as exc:
        logger.warning("Redis EXPIRE failed for key=%s: %s", key, exc)
        return False