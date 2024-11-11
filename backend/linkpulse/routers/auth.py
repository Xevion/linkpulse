from datetime import datetime, timedelta
from typing import Annotated, Optional, Tuple

import structlog
from fastapi import APIRouter, Depends, Response, status
from linkpulse.dependencies import RateLimiter, SessionDependency
from linkpulse.models import Session, User
from linkpulse.utilities import utc_now, is_development
from pwdlib import PasswordHash
from pwdlib.hashers.argon2 import Argon2Hasher
from pydantic import BaseModel, EmailStr, Field

logger = structlog.get_logger()

router = APIRouter()

hasher = PasswordHash([Argon2Hasher()])
# cspell: disable
dummy_hash = (
    "$argon2id$v=19$m=65536,t=3,p=4$Ii3hm5/NqcJddQDFK24Wtw$I99xV/qkaLROo0VZcvaZrYMAD9RTcWzxY5/RbMoRLQ4"
)

# Session expiry times
default_session_expiry = timedelta(hours=12)
remember_me_session_expiry = timedelta(days=14)


def validate_session(token: str, user: bool = True) -> Tuple[bool, bool, Optional[User]]:
    """Given a token, validate that the session exists and is not expired.

    This function has side effects:
        - This function updates last_used if `user` is True.
        - This function will invalidate the session if it is expired.

    :param token: The session token to validate.
    :type token: str
    :param user: Whether to update the last_used timestamp of the session.
    :type user: bool
    :return: A tuple containing:
        - A boolean indicating if the session exists.
        - A boolean indicating if the session is valid.
        - The User object if the session is valid, otherwise None.
    :rtype: Tuple[bool, bool, Optional[User]]
    """
    # Check if session exists
    session = Session.get_or_none(Session.token == token)
    if session is None:
        return False, False, None

    # Check if session is expired
    if session.is_expired(revoke=True):
        return True, False, None

    if user:
        session.use()
    return True, True, session.user


class LoginBody(BaseModel):
    email: EmailStr  # May be a heavy check; profiling could determine if this is necessary
    password: str = Field(min_length=1)  # Basic check, registration will have more stringent requirements
    remember_me: bool = False


class LoginError(BaseModel):
    error: str


class LoginSuccess(BaseModel):
    email: EmailStr
    expiry: datetime


@router.post(
    "/api/login",
    responses={200: {"model": LoginSuccess}, 401: {"model": LoginError}},
    dependencies=[Depends(RateLimiter("6/minute"))],
)
async def login(body: LoginBody, response: Response):
    # Acquire user by email
    user = User.get_or_none(User.email == body.email)

    if user is None:
        # Hash regardless of user existence to prevent timing attacks
        hasher.verify(body.password, dummy_hash)
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return LoginError(error="Invalid email or password")

    logger.warning("Hash", hash=user.password_hash)
    valid, updated_hash = hasher.verify_and_update(body.password, user.password_hash)

    # Check if password matches, return 401 if not
    if not valid:
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return LoginError(error="Invalid email or password")

    # Update password hash if necessary
    if updated_hash:
        user.password_hash = updated_hash
        user.save()

    # Create session
    token = Session.generate_token()
    session_duration = remember_me_session_expiry if body.remember_me else default_session_expiry
    session = Session.create(
        token=token,
        user=user,
        expiry=utc_now() + session_duration,
    )

    # Set Cookie of session token
    max_age = int(session_duration.total_seconds())
    response.set_cookie("session", token, max_age=max_age, secure=not is_development, httponly=True)
    return {"email": user.email, "expiry": session.expiry}


@router.post("/api/logout", status_code=status.HTTP_200_OK)
async def logout(
    response: Response,
    session: Annotated[Session, Depends(SessionDependency(required=True))],
    all: bool = False,
):
    # We can assume the session is valid via the dependency
    if not all:
        session.delete_instance()
        logger.debug("Session deleted", user=session.user.email, token=session.token)
    else:
        count = Session.delete().where(Session.user == session.user).execute()
        logger.debug("All sessions deleted", user=session.user.email, count=count, source_token=session.token)

    response.delete_cookie("session")


@router.post("/api/register")
async def register():
    # Validate parameters
    # Hash password
    # Create User
    # Create Session
    # Set Cookie of session token
    # Return 200 with mild user information
    pass


@router.get("/api/session")
async def session(session: Annotated[Session, Depends(SessionDependency(required=True))]):
    # Returns the session information for the current session
    return {
        "user": {
            "email": session.user.email,
        }
    }


@router.get("/api/sessions")
async def sessions(session: Annotated[Session, Depends(SessionDependency(required=True))]):
    # Returns a list of all active sessions for this user
    return {}


# GET /api/user/{id}/sessions
# GET /api/user/{id}/sessions/{token}
# DELETE /api/user/{id}/sessions
# POST /api/user/{id}/logout (delete all sessions)
