from typing import Tuple, Optional

from pwdlib import PasswordHash
from pwdlib.hashers.argon2 import Argon2Hasher
from fastapi import APIRouter, Depends
from pydantic import BaseModel, EmailStr, Field
from linkpulse.dependencies import RateLimiter
from linkpulse.models import User, Session

router = APIRouter()

hasher = PasswordHash([Argon2Hasher()])
dummy_hash = "$argon2id$v=19$m=65536,t=3,p=4$Ii3hm5/NqcJddQDFK24Wtw$I99xV/qkaLROo0VZcvaZrYMAD9RTcWzxY5/RbMoRLQ4"


def validate_session(
    token: str, user: bool = True
) -> Tuple[bool, bool, Optional[User]]:
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
    email: EmailStr
    password: str = Field(min_length=1)
    remember_me: bool = False


class LoginError(BaseModel):
    error: str


@router.post("/api/login", dependencies=[Depends(RateLimiter("6/minute"))])
async def login(body: LoginBody):
    # Acquire user by email
    user = User.get_or_none(User.email == body.email)

    if user is None:
        # Hash regardless of user existence to prevent timing attacks
        hasher.verify(body.password, dummy_hash)
        return LoginError(error="Invalid email or password")

    # valid, updated_hash = hasher.verify_and_update(body.password, existing_hash)

    # Check if user exists, return 401 if not
    # Check if password matches, return 401 if not
    # Create session
    # Set Cookie of session token
    # Return 200 with mild user information
    pass


@router.post("/api/logout")
async def logout():
    # TODO: Force logout parameter, logout ALL sessions for User
    # Get session token from Cookie
    # Delete session
    # Return 200
    pass


@router.post("/api/register")
async def register():
    # Validate parameters
    # Hash password
    # Create User
    # Create Session
    # Set Cookie of session token
    # Return 200 with mild user information
    pass


@router.get("/api/sessions")
async def sessions():
    pass


# GET /api/user/{id}/sessions
# GET /api/user/{id}/sessions/{token}
# DELETE /api/user/{id}/sessions
# POST /api/user/{id}/logout (delete all sessions)
