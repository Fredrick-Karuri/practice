import redis.asyncio as redis
import os 

redis_client = None
async def init_redis():
    global redis_client
    redis_client = await redis.from_url(
        os.getenv("REDIS_URL", "redis://localhost:6379"),
        encoding="utf-8",
        decode_responses=True
    )
    return redis_client

async def close_redis():
    global redis_client
    if redis_client:
        await redis_client.close()

async def get_redis():
    return redis_client

