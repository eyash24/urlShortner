from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field, EmailStr

# User schema
class UserBase(BaseModel):
    username: str = Field(min_length=1, max_length=50)
    email: EmailStr = Field(max_length=150)

class UserCreate(UserBase):
    password: str = Field(min_length=8)

class UserPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    username: str = Field(min_length=1,max_length=50)

class UserPrivate(UserPublic):
    email: EmailStr = Field(max_length=120)

class UserUpdate(BaseModel):
    username: str | None = Field(default=None,  min_length=1, max_length=50)
    email: EmailStr | None = Field(default=None, max_length=120)

class Token(BaseModel):
    access_token: str
    token_type: str

# Access Group + Mail Schema
class AccessMails(BaseModel):
    email: EmailStr

class AccessGroup(BaseModel):
    author: UserBase
    emails: list[AccessMails]

class AccessGroupCreate(AccessGroup):
    pass

class AccessGroupResponse(AccessGroup):
    created_at: datetime


# URL schema
class URLBase(BaseModel):
    purpose: str = Field(min_length=1, max_length=100)
    long_url: str = Field(min_length=1, max_length=1000)
    rate_limit: int | None = Field(default=None)
    duration: int

class URLCreate(URLBase):
    pass

class URLResponse(URLBase):
    model_config = ConfigDict(from_attributes=True)
    short_url: str
    access_group: AccessGroup
    created_at: datetime
    expires_at: datetime

class URLUpdate(BaseModel):
    acces_group: AccessGroup | None
    duration: int | None
    rate_limit: int | None
    purpose: str | None = Field(min_length=1, max_length=100)

# Pagination schema 
class PaginatedURLResponse(BaseModel):
    urls: list[URLResponse]
    total: int
    skip: int
    limit: int
    has_more: bool

# Auth Schema 
class ForgotPasswordRequest(BaseModel):
    email: EmailStr = Field(max_length=120)

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str = Field(min_length=8)

class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str = Field(min_length=8)

# Logs
class ClickLogs(BaseModel):
    url_id: URLResponse
    click_at: datetime

