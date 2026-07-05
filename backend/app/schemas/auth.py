from datetime import datetime

from pydantic import BaseModel, Field, field_validator

from app.database.models.user import UserRole


class UserCreate(BaseModel):
    email: str
    full_name: str = Field(min_length=2, max_length=255)
    password: str = Field(min_length=8, max_length=128)
    role: UserRole = UserRole.student

    @field_validator("email")
    @classmethod
    def validate_dev_email(cls, value: str) -> str:
        normalized = value.strip().lower()
        if not normalized or "@" not in normalized:
            raise ValueError("Invalid email address format.")
        local_part, domain = normalized.rsplit("@", 1)
        if not local_part or not domain:
            raise ValueError("Invalid email address format.")
        if "." not in domain and domain != "localhost":
            raise ValueError("Invalid email address format.")
        return normalized


class UserLogin(BaseModel):
    email: str
    password: str

    @field_validator("email")
    @classmethod
    def validate_dev_email(cls, value: str) -> str:
        normalized = value.strip().lower()
        if not normalized or "@" not in normalized:
            raise ValueError("Invalid email address format.")
        local_part, domain = normalized.rsplit("@", 1)
        if not local_part or not domain:
            raise ValueError("Invalid email address format.")
        if "." not in domain and domain != "localhost":
            raise ValueError("Invalid email address format.")
        return normalized


class UserRead(BaseModel):
    id: int
    email: str
    full_name: str
    role: UserRole
    created_at: datetime

    model_config = {"from_attributes": True}


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserRead
