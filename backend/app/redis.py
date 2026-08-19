import os

import redis
from dotenv import load_dotenv


load_dotenv()


REDIS_URL = os.getenv("REDIS_URL")

if not REDIS_URL:
    raise RuntimeError(
        "REDIS_URL is not set in environment variables."
    )


redis_client = redis.Redis.from_url(
    REDIS_URL,
    decode_responses=True
)


def get_redis():
    return redis_client