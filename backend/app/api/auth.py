
from typing import Annotated

from app.core.config import settings
from app.core.database import get_db
from app.core.dependencies import CurrentUser
from app.core.security import create_access_token
from app.models.user import User
from app.schemas.auth import (
    LoginRequest,
    TokenResponse,
    UserRead,
    UserRegister,
)
from app.services.auth_service import (
    DeveloperRoleUnavailableError,
    InvalidCredentialsError,
    UserAlreadyExistsError,
    authenticate_user,
    register_user,
)
from app.services.session_service import (
    InvalidRefreshTokenError,
    RefreshTokenReuseError,
    create_refresh_session,
    revoke_refresh_session,
    rotate_refresh_session,
)
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Request,
    Response,
    status,
)
from sqlalchemy.orm import Session

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)

DbSession = Annotated[Session, Depends(get_db)]


def set_refresh_cookie(
    response: Response,
    token: str,
) -> None:
    """Set the refresh token as an HTTP-only browser cookie."""

    response.set_cookie(
        key=settings.REFRESH_TOKEN_COOKIE_NAME,
        value=token,
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
        httponly=True,
        secure=settings.REFRESH_TOKEN_COOKIE_SECURE,
        samesite="lax",
        path="/auth",
    )


def clear_refresh_cookie(response: Response) -> None:
    """Remove the refresh-token cookie from the browser."""

    response.delete_cookie(
        key=settings.REFRESH_TOKEN_COOKIE_NAME,
        httponly=True,
        secure=settings.REFRESH_TOKEN_COOKIE_SECURE,
        samesite="lax",
        path="/auth",
    )


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


@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
)
def login(
    credentials: LoginRequest,
    response: Response,
    db: DbSession,
) -> TokenResponse:
    """Authenticate a user and establish a refresh-token session."""

    try:
        user = authenticate_user(
            db=db,
            identifier=credentials.identifier,
            password=credentials.password,
        )

    except InvalidCredentialsError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username/email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc

    # Create the refresh-token session in PostgreSQL.
    refresh_token = create_refresh_session(
        db=db,
        user_id=user.id,
    )

    # Persist the refresh-token record.
    db.commit()

    # Store the raw refresh token only in an HTTP-only cookie.
    set_refresh_cookie(response, refresh_token)

    # Return the short-lived access token in the response body.
    access_token = create_access_token(
        subject=str(user.id),
    )

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


@router.post(
    "/refresh",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
)
def refresh_access_token(
    request: Request,
    response: Response,
    db: DbSession,
) -> TokenResponse:
    """Rotate a refresh token and issue a new access token."""

    raw_token = request.cookies.get(
        settings.REFRESH_TOKEN_COOKIE_NAME
    )

    if not raw_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token is missing.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        user, new_refresh_token = rotate_refresh_session(
            db=db,
            raw_token=raw_token,
        )

    except RefreshTokenReuseError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh-token reuse detected. Login again.",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc

    except InvalidRefreshTokenError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token.",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc

    # Replace the browser's old refresh cookie.
    set_refresh_cookie(response, new_refresh_token)

    # Generate a new short-lived access token.
    access_token = create_access_token(
        subject=str(user.id),
    )

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


@router.post(
    "/logout",
    status_code=status.HTTP_200_OK,
)
def logout(
    request: Request,
    response: Response,
    db: DbSession,
) -> dict[str, str]:
    """Revoke the refresh-token session and clear its cookie."""

    raw_token = request.cookies.get(
        settings.REFRESH_TOKEN_COOKIE_NAME
    )

    if raw_token:
        revoke_refresh_session(
            db=db,
            raw_token=raw_token,
        )

    clear_refresh_cookie(response)

    return {
        "message": "Logged out successfully.",
    }


@router.get(
    "/me",
    response_model=UserRead,
    status_code=status.HTTP_200_OK,
)
def get_my_profile(
    current_user: CurrentUser,
) -> User:
    """Return the authenticated developer's profile."""

    return current_user
