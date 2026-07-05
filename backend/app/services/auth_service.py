from datetime import timedelta

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.security import create_access_token, get_password_hash, verify_password
from app.database.models import User, UserRole
from app.schemas.auth import TokenResponse, UserCreate, UserLogin


class AuthService:
    def __init__(self, db: Session):
        self.db = db
        self.settings = get_settings()

    def register(self, payload: UserCreate) -> User:
        if payload.role == UserRole.admin:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin registration is disabled")

        existing = self.db.scalar(select(User).where(User.email == payload.email.lower()))
        if existing:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

        user = User(
            email=payload.email.lower(),
            full_name=payload.full_name,
            hashed_password=get_password_hash(payload.password),
            role=payload.role,
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def login(self, payload: UserLogin) -> TokenResponse:
        user = self.db.scalar(select(User).where(User.email == payload.email.lower()))
        if not user or not verify_password(payload.password, user.hashed_password):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")

        token = create_access_token(
            subject=user.id, expires_delta=timedelta(minutes=self.settings.jwt_expire_minutes)
        )
        return TokenResponse(access_token=token, user=user)
