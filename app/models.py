"""Base models."""
from sqlalchemy.ext.asyncio import AsyncSession

from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import Integer
from sqlalchemy import String

from app.database import db


class CRUDMixin:
    """Crud methods mixin."""

    async def save(self, session: AsyncSession):
        """Save method."""
        session.add(self)
        await session.flush()
        return self

    async def delete(self, session: AsyncSession):
        await session.delete(self)
        await session.flush()


class PkModel(db.Model, CRUDMixin):
    """Base model with id."""

    __abstract__ = True

    id = Column(Integer, primary_key=True)


class User(PkModel):
    """User model."""

    __tablename__ = "users"
    __verbose_name__ = "User"

    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True)
    active = Column(Boolean, default=True)
    hashed_password = Column(String(255), nullable=True)
    last_login_date = Column(DateTime, nullable=True)
    last_active_date = Column(DateTime, nullable=True)

    def __str__(self):
        """Str rerp."""
        return self.email
