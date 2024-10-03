import aioredis
import os

redis_host = os.getenv("REDIS_HOST", "redis")
redis = None

def get_redis_client():
    global redis
    if redis is None:
        redis = aioredis.from_url(f"redis://{redis_host}")
    return redis
