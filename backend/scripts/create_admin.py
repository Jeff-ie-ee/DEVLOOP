
import getpass
import sys
from pathlib import Path

from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

# Make the backend application importable.
BACKEND_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_DIR))

from app.core.database import SessionLocal
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


def main() -> int:
    """Create a separate DEVLOOP administrator account."""

    print("\n========================================")
    print("       DEVLOOP ADMIN PROVISIONING")
    print("========================================")
    print("Create a separate administrator account.")
    print("The password will not be displayed.\n")

    username = input("Administrator username: ").strip()
    email = input("Administrator email: ").strip()

    password = getpass.getpass("Administrator password: ")
    confirmation = getpass.getpass("Confirm password: ")

    if password != confirmation:
        print("\nERROR: Passwords do not match.")
        return 1

    # Validate username, email and password.
    try:
        registration = UserRegister(
            username=username,
            email=email,
            password=password,
        )

    except ValidationError as exc:
        print("\nERROR: Invalid administrator details.")

        for error in exc.errors():
            field = ".".join(str(item) for item in error["loc"])
            print(f"- {field}: {error['msg']}")

        return 1

    normalized_email = str(registration.email).strip().lower()

    # Connect to PostgreSQL.
    with SessionLocal() as db:
        try:
            # Verify that the admin role exists.
            admin_role = get_role_by_name(db, "admin")

            if admin_role is None:
                print("\nERROR: Admin role does not exist.")
                print("Run: python -m alembic upgrade head")
                return 1

            # Never modify or promote an existing account.
            existing_username = get_user_by_username(
                db,
                registration.username,
            )

            existing_email = get_user_by_email(
                db,
                normalized_email,
            )

            if existing_username or existing_email:
                print("\nERROR: Username or email already exists.")
                print("No existing account was modified.")
                return 1

            # Generate a secure Argon2 password hash.
            password_hash = hash_password(registration.password)

            # Create the administrator account.
            user = User(
                username=registration.username,
                email=normalized_email,
                password_hash=password_hash,
                is_active=True,
            )

            user = create_user(db, user)

            # Assign the administrator role.
            create_user_role(
                db,
                user_id=user.id,
                role_id=admin_role.id,
            )

            # Commit user creation and role assignment together.
            db.commit()

            print("\n========================================")
            print("ADMINISTRATOR CREATED SUCCESSFULLY")
            print("========================================")
            print(f"User ID: {user.id}")
            print(f"Username: {user.username}")
            print(f"Email: {user.email}")
            print("Role: admin")
            print("Account status: Active")
            print("Password: Hashed using Argon2")
            print("========================================")

            return 0

        except IntegrityError:
            db.rollback()

            print("\nERROR: Database constraint violation.")
            print("Username, email or role assignment conflict.")
            print("Transaction rolled back. No partial account remains.")

            return 1

        except SQLAlchemyError as exc:
            db.rollback()

            original_error = getattr(exc, "orig", None)

            print("\nERROR: Database operation failed.")
            print("Transaction rolled back.")

            if original_error is not None:
                print(
                    "Database error type:",
                    type(original_error).__name__,
                )

                sqlstate = (
                    getattr(original_error, "sqlstate", None)
                    or getattr(original_error, "sql_state", None)
                )

                if sqlstate:
                    print("SQLSTATE:", sqlstate)

                diagnostic = str(original_error).splitlines()

                if diagnostic:
                    print(
                        "Database diagnostic:",
                        diagnostic[0][:400],
                    )

            else:
                print("Error type:", type(exc).__name__)

            print("No changes were committed.")

            return 1


if __name__ == "__main__":
    raise SystemExit(main())
