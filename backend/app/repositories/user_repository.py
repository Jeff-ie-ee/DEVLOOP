
from app.models.role import Role
from app.models.user import User
from app.models.user_role import UserRole
from sqlalchemy import select
from sqlalchemy.orm import Session


def get_user_by_email(db: Session, email: str) -> User | None:
    """Find an existing user by email address."""
    statement = select(User).where(User.email == email)
    return db.scalar(statement)


def get_user_by_username(db: Session, username: str) -> User | None:
    """Find an existing user by username."""
    statement = select(User).where(User.username == username)
    return db.scalar(statement)


def get_role_by_name(db: Session, name: str) -> Role | None:
    """Find a role by its name."""
    statement = select(Role).where(Role.name == name)
    return db.scalar(statement)


def create_user(db: Session, user: User) -> User:
    """Add a new user to the current database transaction."""
    db.add(user)
    db.flush()
    db.refresh(user)
    return user


def create_user_role(
    db: Session,
    user_id: int,
    role_id: int,
) -> UserRole:
    """Assign a role to a user within the current transaction."""
    assignment = UserRole(
        user_id=user_id,
        role_id=role_id,
    )

    db.add(assignment)
    db.flush()

    return assignment


def create_role(
    db: Session,
    name: str,
    description: str | None = None,
) -> Role:
    """Create a platform role within the current transaction."""
    role = Role(
        name=name,
        description=description,
    )

    db.add(role)
    db.flush()
    db.refresh(role)

    return role
