import os
import structlog
from fastapi import HTTPException, Request, Response, status
from limits.aio.strategies import MovingWindowRateLimiter
from limits.aio.storage import MemoryStorage
from limits import parse

storage = MemoryStorage()
strategy = MovingWindowRateLimiter(storage)

logger = structlog.get_logger()
is_pytest = os.environ.get("PYTEST_VERSION") is not None


class RateLimiter:
    def __init__(self, limit: str):
        self.limit = parse(limit)
        self.retry_after = str(self.limit.get_expiry())

    async def __call__(self, request: Request, response: Response):
        key = request.headers.get("X-Real-IP")

        if key is None:
            if request.client is None:
                logger.warning("No client information available for request.")
                return False
            key = request.client.host

        if is_pytest:
            # This is somewhat hacky, I'm not sure if there's a way it can break during pytesting, but look here if odd rate limiting errors occur during tests
            # The reason for this is so tests don't compete with each other for rate limiting
            key += "." + os.environ["PYTEST_CURRENT_TEST"]

        if not await strategy.hit(self.limit, key):
            logger.warning("Rate limit exceeded", key=key)
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too Many Requests",
                headers={"Retry-After": self.retry_after},
            )
        return True
