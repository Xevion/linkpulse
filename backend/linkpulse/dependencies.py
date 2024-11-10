import structlog
from fastapi import HTTPException, Request, Response, status
from limits.strategies import MovingWindowRateLimiter
from limits.storage import MemoryStorage
from limits import parse

storage = MemoryStorage()
strategy = MovingWindowRateLimiter(storage)

logger = structlog.get_logger()


class RateLimiter:
    def __init__(self, limit: str):
        self.limit = parse(limit)
        self.retry_after = str(self.limit.get_expiry())

    async def __call__(self, request: Request, response: Response):
        logger.debug("Rate limiting request", path=request.url.path)

        key = request.headers.get("X-Real-IP")
        if key is None:
            if request.client is None:
                logger.warning("No client information available for request.")
                return False
            key = request.client.host

        if not strategy.hit(self.limit, key):
            logger.warning("Rate limit exceeded", key=key)
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too Many Requests",
                headers={"Retry-After": self.retry_after},
            )
        return True
