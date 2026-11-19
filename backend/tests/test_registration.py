
import pytest
from app.core.database import Base, get_db
from app.main import app
from app.models.role import Role
from app.models.user import User
from app.models.user_role import UserRole
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool


@pytest.fixture
def db_session():
    """Create an isolated SQLite database for each test."""

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
        db.add(
            Role(
                name="developer",
                description="Standard DEVLOOP developer",
            )
        )
        db.commit()

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


def registration_payload():
    """Return valid test registration data."""

    return {
        "username": "test_developer",
        "email": "test_developer@example.com",
        "password": "DEVLOOP-Test-Password-2026!",
    }


def test_successful_registration(client):
    response = client.post(
        "/auth/register",
        json=registration_payload(),
    )

    assert response.status_code == 201

    data = response.json()

    assert data["username"] == "test_developer"
    assert data["email"] == "test_developer@example.com"
    assert data["is_active"] is True

    assert "password" not in data
    assert "password_hash" not in data


def test_duplicate_email_rejected(client):
    payload = registration_payload()

    first_response = client.post(
        "/auth/register",
        json=payload,
    )

    assert first_response.status_code == 201

    duplicate_payload = {
        **payload,
        "username": "another_developer",
    }

    response = client.post(
        "/auth/register",
        json=duplicate_payload,
    )

    assert response.status_code == 409


def test_duplicate_username_rejected(client):
    payload = registration_payload()

    first_response = client.post(
        "/auth/register",
        json=payload,
    )

    assert first_response.status_code == 201

    duplicate_payload = {
        **payload,
        "email": "another_developer@example.com",
    }

    response = client.post(
        "/auth/register",
        json=duplicate_payload,
    )

    assert response.status_code == 409


def test_invalid_email_rejected(client, db_session):
    payload = registration_payload()
    payload["email"] = "invalid-email"

    response = client.post(
        "/auth/register",
        json=payload,
    )

    assert response.status_code == 422
    assert db_session.scalar(select(User)) is None


def test_short_password_rejected(client, db_session):
    payload = registration_payload()
    payload["password"] = "short123"

    response = client.post(
        "/auth/register",
        json=payload,
    )

    assert response.status_code == 422
    assert db_session.scalar(select(User)) is None


def test_developer_role_automatically_assigned(client, db_session):
    response = client.post(
        "/auth/register",
        json=registration_payload(),
    )

    assert response.status_code == 201

    user_id = response.json()["id"]

    assignment = db_session.scalar(
        select(UserRole).where(UserRole.user_id == user_id)
    )

    assert assignment is not None

    assigned_role = db_session.get(Role, assignment.role_id)

    assert assigned_role is not None
    assert assigned_role.name == "developer"
