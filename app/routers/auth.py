from fastapi import APIRouter, HTTPException, Response, status

from app.core.config import get_settings
from app.core.deps import CurrentUser, DbSession
from app.core.security import (
    ACCESS_TOKEN_COOKIE_NAME,
    create_access_token,
    verify_password,
)
from app.crud.user import get_user_by_email
from app.schemas.auth import LoginRequest
from app.schemas.user import UserRead

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


@router.post("/login", response_model=UserRead)
def login(credentials: LoginRequest, response: Response, db: DbSession) -> UserRead:
    user = get_user_by_email(db, credentials.email)
    invalid_credentials = HTTPException(
        status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password"
    )
    if user is None or not user.is_active:
        raise invalid_credentials
    if not verify_password(credentials.password, user.hashed_password):
        raise invalid_credentials

    settings = get_settings()
    token = create_access_token(user.id)
    response.set_cookie(
        key=ACCESS_TOKEN_COOKIE_NAME,
        value=token,
        httponly=True,
        secure=settings.is_production,
        samesite="lax",
        max_age=settings.jwt_access_token_expire_minutes * 60,
    )
    return user


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(response: Response) -> None:
    response.delete_cookie(ACCESS_TOKEN_COOKIE_NAME)


@router.get("/me", response_model=UserRead)
def me(current_user: CurrentUser) -> UserRead:
    return current_user
