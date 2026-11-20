
import pytest
from app.core.database import Base, get_db
from app.core.security import create_access_token
from app.main import app
from app.models.role import Role
from app.models.user import User
from app.models.user_role import UserRole
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

TEST_PASSWORD = "DEVLOOP-RBAC-Test-2026!"


@pytest.fixture
def db_session():
    """Create an isolated SQLite database for RBAC tests."""

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
        db.add_all(
            [
                Role(
                    name="developer",
                    description="Standard DEVLOOP developer",
                ),
                Role(
                    name="admin",
                    description="DEVLOOP platform administrator",
                ),
            ]
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


def create_test_user(
    db_session,
    role_name: str,
    is_active: bool = True,
) -> User:
    """Create a test user and assign the specified role."""

    role = db_session.scalar(
        select(Role).where(Role.name == role_name)
    )

    assert role is not None

    user = User(
        username=f"test_{role_name}",
        email=f"test_{role_name}@example.com",
        password_hash="test-hash-not-used-for-this-endpoint",
        is_active=is_active,
    )

    db_session.add(user)
    db_session.flush()

    assignment = UserRole(
        user_id=user.id,
        role_id=role.id,
    )

    db_session.add(assignment)
    db_session.commit()
    db_session.refresh(user)

    return user


def test_admin_can_list_users(client, db_session):
    """An administrator can retrieve registered user profiles."""

    admin = create_test_user(db_session, "admin")
    developer = create_test_user(db_session, "developer")

    token = create_access_token(str(admin.id))

    response = client.get(
        "/admin/users",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 2

    usernames = {user["username"] for user in data}

    assert usernames == {
        admin.username,
        developer.username,
    }

    for user_data in data:
        assert "password" not in user_data
        assert "password_hash" not in user_data


def test_developer_cannot_access_admin_endpoint(
    client,
    db_session,
):
    """A developer must receive HTTP 403."""

    developer = create_test_user(
        db_session,
        "developer",
    )

    token = create_access_token(str(developer.id))

    response = client.get(
        "/admin/users",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 403

    assert response.json()["detail"] == (
        "You do not have permission to access this resource."
    )


def test_missing_token_rejected(client):
    """Requests without authentication must receive HTTP 401."""

    response = client.get("/admin/users")

    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Bearer"


def test_inactive_admin_rejected(client, db_session):
    """An inactive administrator must receive HTTP 401."""

    admin = create_test_user(
        db_session,
        "admin",
        is_active=False,
    )

    token = create_access_token(str(admin.id))

    response = client.get(
        "/admin/users",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 401


def test_public_registration_cannot_assign_admin_role(
    client,
    db_session,
):
    """Public registration cannot promote a user to administrator."""

    response = client.post(
        "/auth/register",
        json={
            "username": "public_developer",
            "email": "public_developer@example.com",
            "password": "DEVLOOP-Registration-2026!",
            "role": "admin",
        },
    )

    assert response.status_code == 201

    user = db_session.scalar(
        select(User).where(
            User.username == "public_developer"
        )
    )

    assert user is not None

    assigned_role = db_session.scalar(
        select(Role.name)
        .join(
            UserRole,
            UserRole.role_id == Role.id,
        )
        .where(UserRole.user_id == user.id)
    )

    assert assigned_role == "developer"
    assert assigned_role != "admin"
