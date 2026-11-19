
from app.core.security import hash_password
from app.models.user import User
from app.repositories.user_repository import (
    create_user,
    create_user_role,
    get_role_by_name,
    get_user_by_email,
    get_user_by_username,
)
from app.schemas.auth import UserRegister
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session


class UserAlreadyExistsError(Exception):
    """Raised when a username or email is already registered."""


class DeveloperRoleUnavailableError(Exception):
    """Raised when the default developer role is unavailable."""


def register_user(db: Session, registration: UserRegister) -> User:
    """
    Register a new DEVLOOP user.

    The operation creates the user and assigns the default developer
    role within one database transaction.
    """

    username = registration.username.strip()
    email = str(registration.email).strip().lower()

    # Check for an existing email.
    if get_user_by_email(db, email):
        raise UserAlreadyExistsError(
            "An account with this email already exists."
        )

    # Check for an existing username.
    if get_user_by_username(db, username):
        raise UserAlreadyExistsError(
            "This username is already taken."
        )

    # Obtain the default role.
    developer_role = get_role_by_name(db, "developer")

    if developer_role is None:
        raise DeveloperRoleUnavailableError(
            "The default developer role has not been configured."
        )

    # Prepare the user record.
    user = User(
        username=username,
        email=email,
        password_hash=hash_password(registration.password),
        is_active=True,
    )

    try:
        # Insert user and assign role in the same transaction.
        user = create_user(db, user)

        create_user_role(
            db,
            user_id=user.id,
            role_id=developer_role.id,
        )

        db.commit()
        db.refresh(user)

        return user

    except IntegrityError as exc:
        db.rollback()

        # Handle concurrent registration attempts safely.
        if (
            get_user_by_email(db, email)
            or get_user_by_username(db, username)
        ):
            raise UserAlreadyExistsError(
                "The username or email is already registered."
            ) from exc

        raise

    except Exception:
        db.rollback()
        raise
