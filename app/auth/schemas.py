from pydantic import BaseModel
from pydantic import EmailStr
from pydantic import Field
from datetime import datetime


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str


class UserSchema(BaseModel):
    email: EmailStr = Field(None, title='Email')
    last_login_date: datetime | None = None
    last_active_date: datetime | None = None

    class Config:
        orm_mode = True


class UserLogin(BaseModel):
    email: EmailStr = Field(..., title='Email')
    password: str = Field(..., title='Password', min_length=8, max_length=24)


class RefreshToken(BaseModel):
    refresh_token: str


class ChangePassword(BaseModel):
    old_password: str = Field(..., title='Old Password', min_length=8, max_length=48)
    new_password: str = Field(..., title='New Password', min_length=8, max_length=48)


class UserEmail(BaseModel):
    email: EmailStr = Field(..., title='Email')
