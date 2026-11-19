
from datetime import timedelta

import pytest
from app.core.database import Base, get_db
from app.core.security import create_access_token
from app.main import app
from app.models.user import User
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool


@pytest.fixture
def db_session():
    """Create an isolated SQLite database for current-user tests."""

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
    """Use the isolated test database for API requests."""

    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.pop(get_db, None)


def create_test_user(db_session, is_active=True):
    """Create a test developer account."""

    user = User(
        username="identity_developer",
        email="identity_developer@example.com",
        password_hash="test-hash-not-used-for-this-endpoint",
        is_active=is_active,
    )

    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    return user


def test_authenticated_user_profile(client, db_session):
    """A valid JWT should return the authenticated user's profile."""

    user = create_test_user(db_session)

    token = create_access_token(str(user.id))

    response = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == user.id
    assert data["username"] == user.username
    assert data["email"] == user.email
    assert data["is_active"] is True

    assert "password" not in data
    assert "password_hash" not in data


def test_missing_token_rejected(client):
    """Requests without an Authorization header must be rejected."""

    response = client.get("/auth/me")

    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Bearer"


def test_invalid_token_rejected(client):
    """Malformed JWT tokens must be rejected."""

    response = client.get(
        "/auth/me",
        headers={"Authorization": "Bearer invalid-token"},
    )

    assert response.status_code == 401


def test_expired_token_rejected(client, db_session):
    """Expired access tokens must not provide account access."""

    user = create_test_user(db_session)

    token = create_access_token(
        str(user.id),
        expires_delta=timedelta(seconds=-1),
    )

    response = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 401


def test_unknown_user_rejected(client):
    """A valid JWT referencing a nonexistent user must be rejected."""

    token = create_access_token("999999")

    response = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 401


def test_inactive_user_rejected(client, db_session):
    """An inactive account must not access protected endpoints."""

    user = create_test_user(
        db_session,
        is_active=False,
    )

    token = create_access_token(str(user.id))

    response = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 401
