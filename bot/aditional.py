import os

USE_REDIS = os.getenv("USE_REDIS", "false").lower() == "true"

if USE_REDIS:
    import redis.asyncio as redis
    redis_client = redis.Redis(decode_responses=True)

    async def cache_get(key: str):
        return await redis_client.exists(key)

    async def cache_set(key: str):
        await redis_client.set(key, 1, ex=86400)

else:
    _local_cache = set()

    async def cache_get(key: str):
        return key in _local_cache

    async def cache_set(key: str):
        _local_cache.add(key)
