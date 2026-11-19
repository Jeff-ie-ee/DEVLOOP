
from typing import Annotated

from app.core.database import get_db
from app.models.user import User
from app.schemas.auth import UserRead, UserRegister
from app.services.auth_service import (
    DeveloperRoleUnavailableError,
    UserAlreadyExistsError,
    register_user,
)
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)

DbSession = Annotated[Session, Depends(get_db)]


@router.post(
    "/register",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
)
def register(
    registration: UserRegister,
    db: DbSession,
) -> User:
    """Register a new DEVLOOP developer account."""

    try:
        return register_user(db, registration)

    except UserAlreadyExistsError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username or email is already registered.",
        ) from exc

    except DeveloperRoleUnavailableError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Registration is temporarily unavailable.",
        ) from exc
