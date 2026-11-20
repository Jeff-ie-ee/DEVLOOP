
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt.exceptions import InvalidTokenError
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import decode_access_token
from app.models.user import User
from app.repositories.user_repository import user_has_role
from app.services.session_service import has_active_refresh_session

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
    Identify and validate the authenticated DEVLOOP user.

    Validates JWT signature, expiration, user status and
    active refresh-token session family.
    """

    unauthorized_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if credentials is None:
        raise unauthorized_error

    # Validate the JWT.
    try:
        payload = decode_access_token(
            credentials.credentials
        )

    except InvalidTokenError as exc:
        raise unauthorized_error from exc

    # Extract the JWT subject.
    subject = payload.get("sub")
    session_id = payload.get("sid")

    if (
        not isinstance(subject, str)
        or not subject.isascii()
        or not subject.isdigit()
    ):
        raise unauthorized_error

    if not isinstance(session_id, str) or not session_id:
        raise unauthorized_error

    user_id = int(subject)

    if user_id <= 0:
        raise unauthorized_error

    # Retrieve the user from PostgreSQL.
    user = db.get(User, user_id)

    if user is None or not user.is_active:
        raise unauthorized_error

    # Verify that the refresh-token session family is active.
    session_active = has_active_refresh_session(
        db=db,
        user_id=user.id,
        family_id=session_id,
    )

    if not session_active:
        raise unauthorized_error

    return user


# Reusable authenticated-user dependency.
CurrentUser = Annotated[
    User,
    Depends(get_current_user),
]


def require_role(role_name: str):
    """
    Create a dependency requiring a specific user role.

    Authenticated users without the required role receive 403.
    """

    def role_checker(
        current_user: CurrentUser,
        db: DbSession,
    ) -> User:

        if not user_has_role(
            db,
            current_user.id,
            role_name,
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to access this resource.",
            )

        return current_user

    return role_checker
