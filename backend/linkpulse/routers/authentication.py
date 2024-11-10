from typing import Tuple, Optional

from fastapi import APIRouter
from linkpulse.models import User, Session

router = APIRouter()


def validate_session(
    token: str, user: bool = True
) -> Tuple[bool, bool, Optional[User]]:
    """
    Given a token, validate that the session exists and is not expired.

    This function has side effects:
        - This function updates last_used if `user` is True.
        - This function will invalidate the session if it is expired.
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
