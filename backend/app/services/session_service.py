
import hashlib
import secrets
from datetime import UTC, datetime, timedelta
from uuid import uuid4

from app.core.config import settings
from app.models.refresh_token import RefreshToken
from app.models.user import User
from sqlalchemy import select, update
from sqlalchemy.orm import Session


class InvalidRefreshTokenError(Exception):
    """Raised when a refresh token is invalid or expired."""


class RefreshTokenReuseError(Exception):
    """Raised when an already-rotated refresh token is reused."""


def hash_refresh_token(token: str) -> str:
    """Generate a SHA-256 hash of a refresh token."""

    return hashlib.sha256(
        token.encode("utf-8")
    ).hexdigest()


def generate_refresh_token() -> str:
    """Generate a cryptographically random refresh token."""

    return secrets.token_urlsafe(48)


def create_refresh_session(
    db: Session,
    user_id: int,
) -> tuple[str, str]:
    """Create a new refresh-token session."""

    raw_token = generate_refresh_token()
    family_id = str(uuid4())

    refresh_record = RefreshToken(
        user_id=user_id,
        token_hash=hash_refresh_token(raw_token),
        family_id=family_id,
        expires_at=datetime.now(UTC)
        + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
    )

    db.add(refresh_record)
    db.flush()

    return raw_token, family_id


def _revoke_token_family(
    db: Session,
    family_id: str,
    now: datetime,
) -> None:
    """Revoke all active refresh tokens in a session family."""

    db.execute(
        update(RefreshToken)
        .where(
            RefreshToken.family_id == family_id,
            RefreshToken.revoked_at.is_(None),
        )
        .values(revoked_at=now)
    )


def _is_expired(
    token: RefreshToken,
    now: datetime,
) -> bool:
    """Compare expiration timestamps safely."""

    expires_at = token.expires_at

    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=UTC)

    return expires_at <= now


def has_active_refresh_session(
    db: Session,
    user_id: int,
    family_id: str,
) -> bool:
    """
    Verify that the user's session family has an active
    and unexpired refresh-token record.

    Used to enforce immediate access-token revocation.
    """

    now = datetime.now(UTC)

    records = db.scalars(
        select(RefreshToken).where(
            RefreshToken.user_id == user_id,
            RefreshToken.family_id == family_id,
            RefreshToken.revoked_at.is_(None),
        )
    ).all()

    return any(
        not _is_expired(record, now)
        for record in records
    )


def rotate_refresh_session(
    db: Session,
    raw_token: str,
) -> tuple[User, str, str]:
    """Validate and rotate an existing refresh-token session."""

    now = datetime.now(UTC)

    token_record = db.scalar(
        select(RefreshToken)
        .where(
            RefreshToken.token_hash == hash_refresh_token(raw_token)
        )
        .with_for_update()
    )

    if token_record is None:
        raise InvalidRefreshTokenError(
            "Invalid refresh token."
        )

    if token_record.revoked_at is not None:

        if token_record.replaced_by_token_id is not None:
            _revoke_token_family(
                db,
                token_record.family_id,
                now,
            )

            db.commit()

            raise RefreshTokenReuseError(
                "Previously rotated refresh token was reused."
            )

        raise InvalidRefreshTokenError(
            "Refresh token has already been revoked."
        )

    if _is_expired(token_record, now):
        token_record.revoked_at = now
        db.commit()

        raise InvalidRefreshTokenError(
            "Refresh token has expired."
        )

    user = db.get(User, token_record.user_id)

    if user is None or not user.is_active:
        _revoke_token_family(
            db,
            token_record.family_id,
            now,
        )

        db.commit()

        raise InvalidRefreshTokenError(
            "User account is unavailable."
        )

    # Generate replacement token within the same session family.
    new_raw_token = generate_refresh_token()

    replacement = RefreshToken(
        user_id=user.id,
        token_hash=hash_refresh_token(new_raw_token),
        family_id=token_record.family_id,
        expires_at=now
        + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
    )

    db.add(replacement)
    db.flush()

    # Revoke the old token and link it to its replacement.
    token_record.revoked_at = now
    token_record.replaced_by_token_id = replacement.id

    db.commit()

    return user, new_raw_token, token_record.family_id


def revoke_refresh_session(
    db: Session,
    raw_token: str,
) -> bool:
    """Revoke the complete session family associated with a token."""

    now = datetime.now(UTC)

    token_record = db.scalar(
        select(RefreshToken)
        .where(
            RefreshToken.token_hash == hash_refresh_token(raw_token)
        )
        .with_for_update()
    )

    if token_record is None:
        return False

    _revoke_token_family(
        db,
        token_record.family_id,
        now,
    )

    db.commit()

    return True
