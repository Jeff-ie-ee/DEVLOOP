
from datetime import UTC, datetime, timedelta
from typing import Any

import jwt
from jwt.exceptions import InvalidTokenError
from pwdlib import PasswordHash

from app.core.config import settings

# Password hashing configuration.
password_hasher = PasswordHash.recommended()


def hash_password(password: str) -> str:
    """Convert a plain-text password into an Argon2 hash."""
    return password_hasher.hash(password)


def verify_password(
    plain_password: str,
    hashed_password: str,
) -> bool:
    """Verify a password against its stored hash."""
    return password_hasher.verify(
        plain_password,
        hashed_password,
    )


def create_access_token(
    subject: str,
    session_id: str,
    expires_delta: timedelta | None = None,
) -> str:
    """
    Create a signed JWT access token bound to a session family.
    """

    now = datetime.now(UTC)

    if expires_delta is None:
        expires_delta = timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    expire = now + expires_delta

    payload = {
        "sub": subject,
        "sid": session_id,
        "iat": now,
        "exp": expire,
    }

    return jwt.encode(
        payload,
        settings.JWT_SECRET_KEY.get_secret_value(),
        algorithm=settings.JWT_ALGORITHM,
    )


def decode_access_token(token: str) -> dict[str, Any]:
    """
    Decode and verify a JWT access token.

    Requires subject, session ID, issue time and expiration.
    """

    payload = jwt.decode(
        token,
        settings.JWT_SECRET_KEY.get_secret_value(),
        algorithms=[settings.JWT_ALGORITHM],
        options={
            "require": ["sub", "sid", "iat", "exp"],
        },
    )

    subject = payload.get("sub")
    session_id = payload.get("sid")

    if not isinstance(subject, str) or not subject:
        raise InvalidTokenError("Invalid token subject.")

    if not isinstance(session_id, str) or not session_id:
        raise InvalidTokenError("Invalid token session ID.")

    return payload
