"""Auth routes."""
from http import HTTPStatus
from typing import Any

from fastapi import Response
from app.auth.exceptions import BadRequestException
from app.auth.services import create_user
from app.auth.services import create_access_token
from app.auth.services import get_current_active_user
from app.auth.services import get_password_hash
from app.auth.services import login
from app.auth.services import verify_password
from app.auth.services import verify_refresh_token
from app.auth.constants import AUTH_TOKEN_TYPE
from app.auth.schemas import ChangePassword
from app.auth.schemas import RefreshToken
from app.auth.schemas import Token
from app.auth.schemas import UserEmail
from app.auth.schemas import UserLogin
from app.auth.schemas import UserSchema
from app.database import db_session
from app.models import User
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from fastapi import APIRouter

router = APIRouter(prefix="/api/v1")


@router.post("/auth/signup")
async def create_user_profile(*, response: Response, schema_in: UserLogin, session: AsyncSession = Depends(db_session)):
    """User signup."""
    await create_user(session, schema_in.email, get_password_hash(schema_in.password))
    response.status_code = HTTPStatus.CREATED
    return UserEmail(email=schema_in.email)


@router.post("/auth/login", response_model=Token)
async def login_api(*, schema_in: UserLogin, session: AsyncSession = Depends(db_session)) -> Any:
    """Login via API."""
    return await login(schema_in.email, schema_in.password, session)


@router.post("/auth/refresh", response_model=Token)
async def refresh(*, schema_in: RefreshToken) -> Any:
    """Refresh access token."""
    email = verify_refresh_token(schema_in.refresh_token)
    return Token(
        access_token=create_access_token(email), refresh_token=schema_in.refresh_token, token_type=AUTH_TOKEN_TYPE
    )


@router.post('/me/change_password')
async def change_password(
        *,
        schema_in: ChangePassword,
        current_user: User = Depends(get_current_active_user),
        session: AsyncSession = Depends(db_session),
):
    """Change my password."""
    if not verify_password(schema_in.old_password, current_user.hashed_password):
        raise BadRequestException(message="Old password is incorrect.")
    current_user.hashed_password = get_password_hash(schema_in.new_password)
    await current_user.save(session)
    return {"success": True, "message": "Password changed successfully."}


@router.get("/users/me", response_model=UserSchema)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    """Get current user."""
    return UserSchema.from_orm(current_user)
