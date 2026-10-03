import json
import logging
from typing import Any, Optional
import redis.asyncio as redis
from app.core.config import settings

logger = logging.getLogger(__name__)

redis_client: Optional[redis.Redis] = None


async def get_redis_client() -> Optional[redis.Redis]:
    global redis_client
    if not settings.REDIS_ENABLED:
        return None
    if redis_client is None:
        try:
            redis_client = redis.from_url(
                settings.ASYNC_REDIS_URL,
                decode_responses=True,
                socket_connect_timeout=2.0
            )
            await redis_client.ping()
            logger.info("Connected to Redis server.")
        except Exception as e:
            logger.warning(f"Redis not available ({e}). Running with cache bypass.")
            redis_client = None
    return redis_client


async def close_redis_client() -> None:
    global redis_client
    if redis_client is not None:
        try:
            await redis_client.close()
            logger.info("Closed Redis connection.")
        except Exception as e:
            logger.error(f"Error closing Redis: {e}")
        finally:
            redis_client = None


async def cache_get(key: str) -> Optional[Any]:
    client = await get_redis_client()
    if client is None:
        return None
    try:
        data = await client.get(key)
        if data:
            return json.loads(data)
    except Exception as e:
        logger.debug(f"Cache get error for key '{key}': {e}")
    return None


async def cache_set(key: str, value: Any, ttl_seconds: int = 300) -> bool:
    client = await get_redis_client()
    if client is None:
        return False
    try:
        serialized = json.dumps(value, default=str)
        await client.set(key, serialized, ex=ttl_seconds)
        return True
    except Exception as e:
        logger.debug(f"Cache set error for key '{key}': {e}")
        return False


async def cache_delete(key: str) -> bool:
    client = await get_redis_client()
    if client is None:
        return False
    try:
        await client.delete(key)
        return True
    except Exception as e:
        logger.debug(f"Cache delete error for key '{key}': {e}")
        return False


async def cache_delete_pattern(pattern: str) -> int:
    client = await get_redis_client()
    if client is None:
        return 0
    try:
        count = 0
        async for key in client.scan_iter(match=pattern):
            await client.delete(key)
            count += 1
        return count
    except Exception as e:
        logger.debug(f"Cache delete pattern error '{pattern}': {e}")
        return 0
