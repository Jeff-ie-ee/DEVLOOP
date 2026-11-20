from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest
from app.core.config import settings
from app.core.database import Base, get_db
from app.core.security import (
    hash_password,
)
from app.main import app
from app.models.refresh_token import RefreshToken
from app.models.user import User
from app.services.session_service import (
    generate_refresh_token,
    hash_refresh_token,
)
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

TEST_PASSWORD = "DEVLOOP-Session-Test-2026!"
COOKIE_NAME = settings.REFRESH_TOKEN_COOKIE_NAME


@pytest.fixture
def db_session():
    """Create an isolated SQLite database for session tests."""

    test_engine = create_engine(
        "sqlite+pysqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    Base.metadata.create_all(bind=test_engine)

    TestingSessionLocal = sessionmaker(
        bind=test_engine,
        autoflush=False,
        autocommit=False,
        expire_on_commit=False,
    )

    with TestingSessionLocal() as db:
        yield db

    Base.metadata.drop_all(bind=test_engine)
    test_engine.dispose()


@pytest.fixture
def client(db_session):
    """Override the application database for API testing."""

    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.pop(get_db, None)


def create_test_user(db_session):
    """Create an active developer account."""

    user = User(
        username="session_developer",
        email="session_developer@example.com",
        password_hash=hash_password(TEST_PASSWORD),
        is_active=True,
    )

    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    return user


def login_user(client, db_session):
    """Log in and establish a refresh-token session."""

    user = create_test_user(db_session)

    response = client.post(
        "/auth/login",
        json={
            "identifier": user.username,
            "password": TEST_PASSWORD,
        },
    )

    return user, response


def test_login_creates_refresh_cookie(client, db_session):
    """Successful login creates an HTTP-only refresh cookie."""

    user, response = login_user(client, db_session)

    assert response.status_code == 200

    refresh_token = response.cookies.get(COOKIE_NAME)

    assert refresh_token is not None

    set_cookie = response.headers.get("set-cookie", "")

    assert "httponly" in set_cookie.lower()
    assert "samesite=lax" in set_cookie.lower()

    record = db_session.scalar(
        select(RefreshToken).where(
            RefreshToken.token_hash
            == hash_refresh_token(refresh_token)
        )
    )

    assert record is not None
    assert record.user_id == user.id
    assert record.token_hash != refresh_token
    assert record.revoked_at is None


def test_refresh_rotates_token(client, db_session):
    """Refreshing replaces the old token with a new token."""

    user, login_response = login_user(client, db_session)

    assert login_response.status_code == 200

    old_token = login_response.cookies.get(COOKIE_NAME)

    old_record = db_session.scalar(
        select(RefreshToken).where(
            RefreshToken.token_hash
            == hash_refresh_token(old_token)
        )
    )

    assert old_record is not None

    old_record_id = old_record.id
    family_id = old_record.family_id

    response = client.post("/auth/refresh")

    assert response.status_code == 200

    new_token = response.cookies.get(COOKIE_NAME)

    assert new_token is not None
    assert new_token != old_token
    assert response.json()["access_token"]

    db_session.refresh(old_record)

    assert old_record.revoked_at is not None

    assert old_record.replaced_by_token_id is not None

    replacement = db_session.get(
        RefreshToken,
        old_record.replaced_by_token_id,
    )

    assert replacement is not None
    assert replacement.user_id == user.id
    assert replacement.family_id == family_id
    assert replacement.token_hash == hash_refresh_token(new_token)
    assert replacement.id != old_record_id
    assert replacement.revoked_at is None


def test_reused_refresh_token_revokes_family(
    client,
    db_session,
):
    """Reuse of an already-rotated token revokes the entire family."""

    _, login_response = login_user(client, db_session)

    old_token = login_response.cookies.get(COOKIE_NAME)

    original_record = db_session.scalar(
        select(RefreshToken).where(
            RefreshToken.token_hash
            == hash_refresh_token(old_token)
        )
    )

    assert original_record is not None

    family_id = original_record.family_id

    rotation_response = client.post("/auth/refresh")

    assert rotation_response.status_code == 200

    # Simulate the theft or replay of the previous refresh token.
    client.cookies.set(
        COOKIE_NAME,
        old_token,
        domain="testserver.local",
        path="/auth",
    )

    replay_response = client.post("/auth/refresh")

    assert replay_response.status_code == 401

    assert "reuse detected" in (
        replay_response.json()["detail"].lower()
    )

    db_session.expire_all()

    family_records = db_session.scalars(
        select(RefreshToken).where(
            RefreshToken.family_id == family_id
        )
    ).all()

    assert len(family_records) == 2

    assert all(
        record.revoked_at is not None
        for record in family_records
    )


def test_expired_refresh_token_rejected(client, db_session):
    """Expired refresh tokens cannot create new access tokens."""

    user = create_test_user(db_session)

    raw_token = generate_refresh_token()

    record = RefreshToken(
        user_id=user.id,
        token_hash=hash_refresh_token(raw_token),
        family_id=str(uuid4()),
        expires_at=datetime.now(UTC) - timedelta(days=1),
    )

    db_session.add(record)
    db_session.commit()
    db_session.refresh(record)

    client.cookies.set(
        COOKIE_NAME,
        raw_token,
        domain="testserver.local",
        path="/auth",
    )

    response = client.post("/auth/refresh")

    assert response.status_code == 401

    db_session.refresh(record)

    assert record.revoked_at is not None


def test_missing_refresh_cookie_rejected(client):
    """Refresh requests without a cookie must be rejected."""

    response = client.post("/auth/refresh")

    assert response.status_code == 401

    assert response.json()["detail"] == (
        "Refresh token is missing."
    )


def test_logout_revokes_session(client, db_session):
    """Logout revokes the session and clears its cookie."""

    _, login_response = login_user(client, db_session)

    raw_token = login_response.cookies.get(COOKIE_NAME)

    record = db_session.scalar(
        select(RefreshToken).where(
            RefreshToken.token_hash
            == hash_refresh_token(raw_token)
        )
    )

    assert record is not None

    family_id = record.family_id

    response = client.post("/auth/logout")

    assert response.status_code == 200

    assert response.json() == {
        "message": "Logged out successfully."
    }

    assert "max-age=0" in (
        response.headers.get("set-cookie", "").lower()
    )

    db_session.refresh(record)

    assert record.revoked_at is not None

    family_records = db_session.scalars(
        select(RefreshToken).where(
            RefreshToken.family_id == family_id
        )
    ).all()

    assert all(
        token.revoked_at is not None
        for token in family_records
    )


def test_refresh_after_logout_rejected(client, db_session):
    """A revoked refresh token cannot be reused after logout."""

    _, login_response = login_user(client, db_session)

    old_token = login_response.cookies.get(COOKIE_NAME)

    logout_response = client.post("/auth/logout")

    assert logout_response.status_code == 200

    # Attempt to reuse the revoked token.
    client.cookies.set(
        COOKIE_NAME,
        old_token,
        domain="testserver.local",
        path="/auth",
    )

    response = client.post("/auth/refresh")

    assert response.status_code == 401

def test_logout_immediately_invalidates_access_token(
    client,
    db_session,
):
    """Logout immediately invalidates its associated access JWT."""

    _, login_response = login_user(client, db_session)

    access_token = login_response.json()["access_token"]

    headers = {
        "Authorization": f"Bearer {access_token}",
    }

    # The access token should work before logout.
    before_logout = client.get(
        "/auth/me",
        headers=headers,
    )

    assert before_logout.status_code == 200

    # Revoke the refresh-token family.
    logout_response = client.post("/auth/logout")

    assert logout_response.status_code == 200

    # The previously issued access token must now be rejected.
    after_logout = client.get(
        "/auth/me",
        headers=headers,
    )

    assert after_logout.status_code == 401


def test_reuse_immediately_invalidates_access_tokens(
    client,
    db_session,
):
    """Refresh-token reuse invalidates all access JWTs in its family."""

    _, login_response = login_user(client, db_session)

    original_access_token = login_response.json()["access_token"]
    old_refresh_token = login_response.cookies.get(COOKIE_NAME)

    # Confirm the original access token is initially valid.
    original_check = client.get(
        "/auth/me",
        headers={
            "Authorization": f"Bearer {original_access_token}",
        },
    )

    assert original_check.status_code == 200

    # Rotate the refresh token and obtain another access JWT.
    rotation_response = client.post("/auth/refresh")

    assert rotation_response.status_code == 200

    rotated_access_token = rotation_response.json()["access_token"]

    rotated_check = client.get(
        "/auth/me",
        headers={
            "Authorization": f"Bearer {rotated_access_token}",
        },
    )

    assert rotated_check.status_code == 200

    # Simulate replay of the previously consumed refresh token.
    client.cookies.set(
        COOKIE_NAME,
        old_refresh_token,
        domain="testserver.local",
        path="/auth",
    )

    replay_response = client.post("/auth/refresh")

    assert replay_response.status_code == 401

    # Both access JWTs belong to the revoked session family.
    for access_token in (
        original_access_token,
        rotated_access_token,
    ):
        response = client.get(
            "/auth/me",
            headers={
                "Authorization": f"Bearer {access_token}",
            },
        )

        assert response.status_code == 401
