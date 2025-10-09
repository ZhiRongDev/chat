import redis
from app.config import settings
from datetime import datetime, timezone

_snowflake_gen = None
# redis_client = redis.StrictRedis(
#     host=settings.REDIS_HOST,
#     port=settings.REDIS_PORT,
#     db=settings.REDIS_DB,
#     decode_responses=True,
# )

# session_prefix = "session:"

def set_snowflake_generator(snowflake_gen):
    global _snowflake_gen
    _snowflake_gen = snowflake_gen


def snowflake_generator() -> int:
    if _snowflake_gen is None:
        raise Exception("SnowflakeGenerator is not initialized")
    return int(next(_snowflake_gen))


def get_timestamp():
    return int(datetime.now(timezone.utc).timestamp())

# def set_redis_session(session_id: str, user_id: int, expires_in: int = 3600):
#     if (True):
#         redis_client.hset(session_prefix + session_id, mapping={"user_id": user_id})
#     else:
#         redis_client.expire(session_prefix + session_id, expires_in)
    
#     return session_prefix + session_id