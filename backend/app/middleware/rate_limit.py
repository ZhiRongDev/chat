"""
Rate limiting middleware using Redis
Implements a sliding window rate limiter for chat endpoints
"""

import redis
import time
import logging
from typing import Optional
from fastapi import HTTPException, status
from app.config import settings

logger = logging.getLogger(__name__)


class RateLimiter:
    """Redis-based rate limiter using sliding window algorithm"""

    def __init__(self):
        """Initialize Redis connection"""
        self.enabled = settings.RATE_LIMIT_ENABLED
        self.redis_client: Optional[redis.Redis] = None

        if self.enabled:
            try:
                self.redis_client = redis.Redis(
                    host=settings.REDIS_HOST,
                    port=settings.REDIS_PORT,
                    password=settings.REDIS_PASSWORD,
                    db=settings.REDIS_DB,
                    decode_responses=True,
                    socket_connect_timeout=5,
                )
                # Test connection
                self.redis_client.ping()
                logger.info(
                    f"✓ Rate limiter initialized: {settings.RATE_LIMIT_MESSAGES} messages per {settings.RATE_LIMIT_WINDOW_SECONDS}s (Redis: {settings.REDIS_HOST}:{settings.REDIS_PORT})"
                )
            except Exception as e:
                logger.error(
                    f"Failed to connect to Redis at {settings.REDIS_HOST}:{settings.REDIS_PORT}: {e}"
                )
                logger.warning("Rate limiting disabled due to Redis connection failure")
                self.enabled = False
                self.redis_client = None
        else:
            logger.warning("Rate limiting is disabled (RATE_LIMIT_ENABLED=False)")

    def check_rate_limit(self, user_id: int) -> tuple[bool, Optional[int]]:
        """
        Check if user has exceeded rate limit

        Args:
            user_id: User ID to check

        Returns:
            Tuple of (allowed: bool, retry_after: Optional[int])
            - allowed: True if request is allowed, False if rate limited
            - retry_after: Seconds until rate limit resets (only if not allowed)
        """
        if not self.enabled or not self.redis_client:
            return True, None

        try:
            key = f"rate_limit:chat:{user_id}"
            now = int(time.time())
            window_start = now - settings.RATE_LIMIT_WINDOW_SECONDS

            logger.debug(
                f"Rate limit check: key={key}, now={now}, window_start={window_start}"
            )

            # Use Redis pipeline for atomic operations
            pipe = self.redis_client.pipeline()

            # Remove old entries outside the window
            pipe.zremrangebyscore(key, 0, window_start)

            # Count requests in current window
            pipe.zcard(key)

            # Execute pipeline
            results = pipe.execute()
            current_count = results[1]

            logger.debug(
                f"Current count for user {user_id}: {current_count}/{settings.RATE_LIMIT_MESSAGES}"
            )

            if current_count >= settings.RATE_LIMIT_MESSAGES:
                # Rate limit exceeded
                logger.info(
                    f"Rate limit EXCEEDED for user {user_id}: {current_count}/{settings.RATE_LIMIT_MESSAGES}"
                )
                # Get oldest timestamp to calculate retry_after
                oldest_timestamps = self.redis_client.zrange(key, 0, 0, withscores=True)
                if oldest_timestamps:
                    oldest_time = int(oldest_timestamps[0][1])
                    retry_after = oldest_time + settings.RATE_LIMIT_WINDOW_SECONDS - now
                    return False, max(1, retry_after)
                return False, settings.RATE_LIMIT_WINDOW_SECONDS

            # Add current request timestamp
            self.redis_client.zadd(key, {str(now): now})
            logger.info(
                f"Rate limit OK for user {user_id}: {current_count + 1}/{settings.RATE_LIMIT_MESSAGES}"
            )

            # Set expiry on key (cleanup)
            self.redis_client.expire(key, settings.RATE_LIMIT_WINDOW_SECONDS)

            return True, None

        except Exception as e:
            logger.error(f"Rate limit check failed: {e}")
            # On error, allow request (fail open)
            return True, None

    def reset_rate_limit(self, user_id: int) -> bool:
        """
        Reset rate limit for a user (admin function)

        Args:
            user_id: User ID to reset

        Returns:
            True if reset successful
        """
        if not self.enabled or not self.redis_client:
            return False

        try:
            key = f"rate_limit:chat:{user_id}"
            self.redis_client.delete(key)
            logger.info(f"Rate limit reset for user {user_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to reset rate limit: {e}")
            return False

    def get_user_stats(self, user_id: int) -> dict:
        """
        Get current rate limit stats for a user

        Args:
            user_id: User ID

        Returns:
            Dict with rate limit stats
        """
        if not self.enabled or not self.redis_client:
            return {
                "enabled": False,
                "current_count": 0,
                "limit": settings.RATE_LIMIT_MESSAGES,
                "window_seconds": settings.RATE_LIMIT_WINDOW_SECONDS,
                "remaining": settings.RATE_LIMIT_MESSAGES,
            }

        try:
            key = f"rate_limit:chat:{user_id}"
            now = int(time.time())
            window_start = now - settings.RATE_LIMIT_WINDOW_SECONDS

            # Remove old entries and count
            pipe = self.redis_client.pipeline()
            pipe.zremrangebyscore(key, 0, window_start)
            pipe.zcard(key)
            results = pipe.execute()
            current_count = results[1]

            return {
                "enabled": True,
                "current_count": current_count,
                "limit": settings.RATE_LIMIT_MESSAGES,
                "window_seconds": settings.RATE_LIMIT_WINDOW_SECONDS,
                "remaining": max(0, settings.RATE_LIMIT_MESSAGES - current_count),
            }
        except Exception as e:
            logger.error(f"Failed to get rate limit stats: {e}")
            return {
                "enabled": False,
                "current_count": 0,
                "limit": settings.RATE_LIMIT_MESSAGES,
                "window_seconds": settings.RATE_LIMIT_WINDOW_SECONDS,
                "remaining": settings.RATE_LIMIT_MESSAGES,
            }


# Global rate limiter instance
rate_limiter = RateLimiter()


def check_chat_rate_limit(user_id: int) -> None:
    """
    Dependency function to check rate limit for chat endpoints

    Args:
        user_id: User ID to check

    Raises:
        HTTPException: If rate limit exceeded
    """
    logger.info(f"Checking rate limit for user {user_id}")
    allowed, retry_after = rate_limiter.check_rate_limit(user_id)
    logger.info(
        f"Rate limit check for user {user_id}: allowed={allowed}, retry_after={retry_after}"
    )

    if not allowed:
        logger.warning(
            f"Rate limit exceeded for user {user_id}, retry after {retry_after}s"
        )
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Rate limit exceeded. You can send {settings.RATE_LIMIT_MESSAGES} messages per {settings.RATE_LIMIT_WINDOW_SECONDS // 60} minutes. "
            f"Please try again in {retry_after} seconds.",
            headers={"Retry-After": str(retry_after)} if retry_after else {},
        )
