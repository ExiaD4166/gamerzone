from redis.asyncio import Redis

from app.core.config import settings

# One shared client with an internal connection pool, created once at import time -
# same idea as the SQLAlchemy engine. decode_responses=True makes Redis hand back
# str instead of bytes, so we don't decode by hand everywhere.
redis_client: Redis = Redis.from_url(settings.redis_url, decode_responses=True)

# Namespacing keys by prefix keeps this data distinguishable from anything else we
# might store in Redis later (caching, rate limiting, Celery results...).
_BLACKLIST_PREFIX = "blacklist:jti:"


async def blacklist_token(jti: str, expires_in_seconds: int) -> None:
    """Mark one token as revoked until it would have expired anyway.

    `ex=` sets a time-to-live, so Redis deletes the key automatically once the token's
    own expiry has passed - after that the token is rejected by the expiry check
    regardless, so keeping the entry would be pointless. This is what stops the
    blacklist from growing without bound.
    """
    if expires_in_seconds <= 0:
        # Already expired: nothing to revoke, and a non-positive TTL is rejected.
        return
    await redis_client.set(f"{_BLACKLIST_PREFIX}{jti}", "revoked", ex=expires_in_seconds)


async def is_token_blacklisted(jti: str) -> bool:
    """Check whether this specific token has been revoked."""
    return await redis_client.exists(f"{_BLACKLIST_PREFIX}{jti}") == 1
