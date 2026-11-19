
from app.core.security import hash_password, verify_password
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


class InvalidCredentialsError(Exception):
    """Raised when login credentials are invalid."""


def register_user(db: Session, registration: UserRegister) -> User:
    """
    Register a new DEVLOOP user.

    Creates the user and assigns the default developer role
    within one database transaction.
    """

    username = registration.username.strip()
    email = str(registration.email).strip().lower()

    if get_user_by_email(db, email):
        raise UserAlreadyExistsError(
            "An account with this email already exists."
        )

    if get_user_by_username(db, username):
        raise UserAlreadyExistsError(
            "This username is already taken."
        )

    developer_role = get_role_by_name(db, "developer")

    if developer_role is None:
        raise DeveloperRoleUnavailableError(
            "The default developer role has not been configured."
        )

    user = User(
        username=username,
        email=email,
        password_hash=hash_password(registration.password),
        is_active=True,
    )

    try:
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


def authenticate_user(
    db: Session,
    identifier: str,
    password: str,
) -> User:
    """
    Authenticate an existing DEVLOOP user using username or email.

    Inactive accounts and invalid credentials are rejected.
    """

    identifier = identifier.strip()

    if "@" in identifier:
        user = get_user_by_email(db, identifier.lower())
    else:
        user = get_user_by_username(db, identifier)

    if user is None:
        raise InvalidCredentialsError(
            "Invalid username/email or password."
        )

    if not verify_password(password, user.password_hash):
        raise InvalidCredentialsError(
            "Invalid username/email or password."
        )

    if not user.is_active:
        raise InvalidCredentialsError(
            "Invalid username/email or password."
        )

    return user
