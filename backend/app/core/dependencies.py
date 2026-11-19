
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt.exceptions import InvalidTokenError
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import decode_access_token
from app.models.user import User

# Extract Bearer tokens from HTTP Authorization headers.
bearer_scheme = HTTPBearer(auto_error=False)


# Reusable dependency types.
DbSession = Annotated[Session, Depends(get_db)]

BearerCredentials = Annotated[
    HTTPAuthorizationCredentials | None,
    Depends(bearer_scheme),
]


def get_current_user(
    credentials: BearerCredentials,
    db: DbSession,
) -> User:
    """
    Identify the authenticated DEVLOOP user.

    Validates the JWT, retrieves the user from PostgreSQL,
    and rejects missing, invalid, expired or inactive accounts.
    """

    unauthorized_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # Check whether a Bearer token was supplied.
    if credentials is None:
        raise unauthorized_error

    # Verify the JWT signature and expiration.
    try:
        payload = decode_access_token(credentials.credentials)
    except InvalidTokenError as exc:
        raise unauthorized_error from exc

    # Extract the database user ID from the JWT subject.
    subject = payload.get("sub")

    if (
        not isinstance(subject, str)
        or not subject.isascii()
        or not subject.isdigit()
    ):
        raise unauthorized_error

    user_id = int(subject)

    if user_id <= 0:
        raise unauthorized_error

    # Retrieve the authenticated account.
    user = db.get(User, user_id)

    if user is None or not user.is_active:
        raise unauthorized_error

    return user


# Reusable dependency for protected endpoints.
CurrentUser = Annotated[User, Depends(get_current_user)]
