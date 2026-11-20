
from typing import Annotated

from app.core.database import get_db
from app.core.dependencies import require_role
from app.models.user import User
from app.repositories.user_repository import list_users
from app.schemas.auth import UserRead
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

router = APIRouter(
    prefix="/admin",
    tags=["Administration"],
)

DbSession = Annotated[Session, Depends(get_db)]

AdminUser = Annotated[
    User,
    Depends(require_role("admin")),
]


@router.get(
    "/users",
    response_model=list[UserRead],
)
def get_registered_users(
    current_admin: AdminUser,
    db: DbSession,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
) -> list[User]:
    """
    Retrieve registered DEVLOOP users.

    Administrator access is required.
    """

    return list_users(
        db,
        offset=(page - 1) * page_size,
        limit=page_size,
    )
