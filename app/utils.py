from datetime import datetime, timezone

_snowflake_gen = None


def set_snowflake_generator(snowflake_gen):
    global _snowflake_gen
    _snowflake_gen = snowflake_gen


def snowflake_generator() -> int:
    if _snowflake_gen is None:
        raise Exception("SnowflakeGenerator is not initialized")
    return int(next(_snowflake_gen))


def get_timestamp():
    return int(datetime.now(timezone.utc).timestamp())
