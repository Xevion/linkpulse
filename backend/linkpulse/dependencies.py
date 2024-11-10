import os
from dataclasses import dataclass

import structlog
from fastapi import HTTPException, Request, Response, status
from limits import parse
from limits.aio.storage import MemoryStorage
from limits.aio.strategies import MovingWindowRateLimiter
from linkpulse.models import Session

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


@dataclass
class SessionModel:
    user_id: str
    session_id: str
    expires_at: int


class SessionDependency:
    def __init__(self, required: bool = False):
        self.required = required

    async def __call__(self, request: Request, response: Response):
        session_token = request.cookies.get("session")

        # If not present, raise 401 if required
        if session_token is None:
            logger.debug("No session cookie found", required=self.required)
            if self.required:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
            return None

        # Get session from database
        session = Session.get_or_none(Session.token == session_token)

        # This doesn't differentiate between expired or completely invalid sessions
        if session is None or session.is_expired(revoke=True):
            if self.required:
                logger.debug("Session Cookie Revoked", token=session_token)
                response.delete_cookie("session")
                headers = {"set-cookie": response.headers["set-cookie"]}
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized", headers=headers
                )
            return None

        return session
