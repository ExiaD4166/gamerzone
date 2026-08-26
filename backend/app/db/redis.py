from redis.asyncio import Redis

from app.core.config import settings

redis_client: Redis = Redis.from_url(settings.redis_url, decode_responses=True)

_BLACKLIST_PREFIX = "blacklist:jti:"


async def blacklist_token(jti: str, expires_in_seconds: int) -> None:
    """Revoke one token until the moment it would have expired anyway.

    The TTL means Redis drops the entry once the token's own expiry has passed, so the
    blacklist cannot grow without bound.
    """
    if expires_in_seconds <= 0:
        return
    await redis_client.set(f"{_BLACKLIST_PREFIX}{jti}", "revoked", ex=expires_in_seconds)


async def is_token_blacklisted(jti: str) -> bool:
    return await redis_client.exists(f"{_BLACKLIST_PREFIX}{jti}") == 1
