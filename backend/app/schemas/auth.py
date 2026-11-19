
import re
from datetime import datetime
from typing import Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    field_validator,
)


class UserRegister(BaseModel):
    """Data required to register a new DEVLOOP account."""

    username: str = Field(
        min_length=3,
        max_length=50,
    )

    email: EmailStr

    password: str = Field(
        min_length=12,
        max_length=128,
    )

    @field_validator("username")
    @classmethod
    def validate_username(cls, value: str) -> str:
        value = value.strip()

        if not re.fullmatch(r"[A-Za-z0-9_.-]+", value):
            raise ValueError(
                "Username can contain only letters, numbers, "
                "underscores, dots and hyphens."
            )

        return value

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: EmailStr) -> str:
        return str(value).strip().lower()


class UserRead(BaseModel):
    """Safe user information returned by the API."""

    id: int
    username: str
    email: EmailStr
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class LoginRequest(BaseModel):
    """Credentials submitted during login."""

    identifier: str = Field(
        min_length=3,
        max_length=255,
        description="Registered username or email address.",
    )

    password: str = Field(
        min_length=1,
        max_length=128,
    )

    @field_validator("identifier")
    @classmethod
    def normalize_identifier(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("Username or email is required.")

        return value


class TokenResponse(BaseModel):
    """JWT access token returned after successful login."""

    access_token: str

    token_type: Literal["bearer"] = "bearer"

    expires_in: int = Field(
        description="Token lifetime in seconds.",
    )
