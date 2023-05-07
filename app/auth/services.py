"""Auth methods module."""
import secrets
import string
from datetime import datetime
from datetime import timedelta

from app.auth.exceptions import AuthenticationException
from app.auth.exceptions import BadRequestException
from app.auth.exceptions import InvalidRefreshToken
from app.auth.schemas import Token
from app.auth.constants import ACCESS_TOKEN_EXPIRE_MINUTES
from app.auth.constants import ALGORITHM
from app.auth.constants import AUTH_TOKEN_TYPE
from app.auth.constants import oauth2_scheme
from app.auth.constants import pwd_context
from app.auth.constants import REFRESH_TOKEN_EXPIRE_MINUTES
from app.database import db_session
from app.models import User
from fastapi import Depends
from jose import ExpiredSignatureError
from jose import jwt
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from config.settings import get_settings

settings = get_settings()


def verify_password(plain_password, hashed_password) -> str:
    """Verify password."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password) -> str:
    """Password hash."""
    return pwd_context.hash(password)


async def get_user(db: AsyncSession, email: str) -> User | None:
    """Get user from db."""
    return (await db.execute(select(User).filter(User.email == email))).scalars().first()


async def authenticate_user(db: AsyncSession, email: str, password: str) -> User | bool:
    """Check and authenticate user."""
    user = await get_user(db, email)
    if not user or not verify_password(password, user.hashed_password):
        return False
    return user


async def create_user(session: AsyncSession, email: str, hashed_password: str = None):
    """Create user."""
    if await get_user(session, email=email):
        raise BadRequestException(message="Already Exist")
    return await User(email=email, hashed_password=hashed_password).save(session)


def create_access_token(subject: str, expires_delta: timedelta | None = None) -> str:
    """Create access token."""
    return _create_jwt_token(subject, 'access', expires_delta)


def create_refresh_token(subject: str, expires_delta: timedelta | None = None) -> str:
    """Create refresh token."""
    return _create_jwt_token(subject, 'refresh', expires_delta)


def _create_jwt_token(subject: str, token_type: str, expires_delta: timedelta | None = None) -> str:
    """Create JWT token."""
    expires_delta = expires_delta or timedelta(minutes=15)
    to_encode = {"sub": subject, "type": token_type}
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.secret_key, algorithm=ALGORITHM)


async def login(email: str, password: str, db: AsyncSession) -> Token:
    """Login helper."""
    user = await authenticate_user(db, email, password)
    if not user:
        raise AuthenticationException()
    user.last_login_date = datetime.utcnow()
    await user.save(db)
    return Token(
        access_token=create_access_token(user.email, expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)),
        refresh_token=create_refresh_token(user.email, expires_delta=timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)),
        token_type=AUTH_TOKEN_TYPE,
    )


async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(db_session)) -> User:
    """Get current user."""
    credentials_exception = AuthenticationException()
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = await get_user(db, email=email)
    if user is None:
        raise credentials_exception
    user.last_active_date = datetime.utcnow()
    return await user.save(db)


async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Get active user."""
    if not current_user.active:
        raise BadRequestException(message="Inactive user")
    return current_user


def verify_refresh_token(refresh_token: str) -> str:
    """Verify refresh token."""
    try:
        payload = jwt.decode(refresh_token, settings.secret_key, algorithms=[ALGORITHM])
    except ExpiredSignatureError:
        raise InvalidRefreshToken('Refresh token has been expired.')
    except Exception as e:
        raise InvalidRefreshToken('Refresh token is invalid.', str(e))
    email: str = payload.get("sub")
    if not email:
        raise InvalidRefreshToken('Refresh token is wrong.')
    return email


def get_generated_password() -> str:
    """Generate password."""
    return ''.join(secrets.choice(string.ascii_letters + string.digits + string.punctuation) for i in range(16))
