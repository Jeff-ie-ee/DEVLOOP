
from datetime import timedelta

import pytest
from app.core.database import Base, get_db
from app.core.security import (
    create_access_token,
    decode_access_token,
    hash_password,
)
from app.main import app
from app.models.user import User
from fastapi.testclient import TestClient
from jwt.exceptions import InvalidTokenError
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

TEST_PASSWORD = "DEVLOOP-Test-Password-2026!"


@pytest.fixture
def db_session():
    """Create an isolated SQLite database for authentication tests."""

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
    """Override the application database with the test database."""

    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.pop(get_db, None)


def create_test_user(db_session, is_active=True):
    """Create a test account with an Argon2 password hash."""

    user = User(
        username="login_developer",
        email="login_developer@example.com",
        password_hash=hash_password(TEST_PASSWORD),
        is_active=is_active,
    )

    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    return user


def test_login_with_username(client, db_session):
    """A registered user can log in using their username."""

    user = create_test_user(db_session)

    response = client.post(
        "/auth/login",
        json={
            "identifier": user.username,
            "password": TEST_PASSWORD,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["token_type"] == "bearer"
    assert data["expires_in"] == 1800
    assert data["access_token"]

    payload = decode_access_token(data["access_token"])

    assert payload["sub"] == str(user.id)


def test_login_with_email(client, db_session):
    """A registered user can log in using their email."""

    user = create_test_user(db_session)

    response = client.post(
        "/auth/login",
        json={
            "identifier": user.email.upper(),
            "password": TEST_PASSWORD,
        },
    )

    assert response.status_code == 200
    assert response.json()["token_type"] == "bearer"


def test_incorrect_password_rejected(client, db_session):
    """An incorrect password must not generate a token."""

    user = create_test_user(db_session)

    response = client.post(
        "/auth/login",
        json={
            "identifier": user.username,
            "password": "Wrong-Password-2026!",
        },
    )

    assert response.status_code == 401
    assert response.json()["detail"] == (
        "Invalid username/email or password."
    )
    assert response.headers["www-authenticate"] == "Bearer"


def test_unknown_user_rejected(client):
    """An unknown username must be rejected."""

    response = client.post(
        "/auth/login",
        json={
            "identifier": "unknown_developer",
            "password": TEST_PASSWORD,
        },
    )

    assert response.status_code == 401


def test_inactive_account_rejected(client, db_session):
    """An inactive account must not receive an access token."""

    user = create_test_user(
        db_session,
        is_active=False,
    )

    response = client.post(
        "/auth/login",
        json={
            "identifier": user.username,
            "password": TEST_PASSWORD,
        },
    )

    assert response.status_code == 401


def test_expired_jwt_rejected():
    """An expired JWT must not be accepted."""

    expired_token = create_access_token(
        subject="1",
        session_id="test-session",
        expires_delta=timedelta(seconds=-1),
    )

    with pytest.raises(InvalidTokenError):
        decode_access_token(expired_token)