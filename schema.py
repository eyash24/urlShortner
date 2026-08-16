from __future__ import annotations

from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field, EmailStr, HttpUrl

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
    access_group: list[AccessGroupResponse] | None = Field(default=None)

class UserUpdate(BaseModel):
    username: str | None = Field(default=None,  min_length=1, max_length=50)
    email: EmailStr | None = Field(default=None, max_length=120)

class Token(BaseModel):
    access_token: str
    token_type: str

# Access Mail Schema
class AccessMails(BaseModel):
    email: EmailStr
    access_group_id: int
    access_status: bool

class AccessMailCreate(AccessMails):
    pass

class AccessMailUpdate(BaseModel):
    email: EmailStr | None = Field(default=None, max_length=120)
    access_group_id: int | None = Field(default=None)
    access_status: bool | None = Field(default=None)


class AccessMailResponse(AccessMails):
    id: int
    updated_at: datetime


# Access Group Shema
class AccessGroup(BaseModel):
    group_name: str = Field(min_length=1, max_length=20)
    expires_at: datetime

class AccessGroupCreate(AccessGroup):
    pass

class AccessGroupResponse(AccessGroup):
    created_at: datetime
    id: int
    user_id: int

class AccessGroupUpdate(BaseModel):
    group_name: str | None = Field(default=None, min_length=1, max_length=20)
    expires_at: datetime | None = Field(default=None)

# URL schema
class URLBase(BaseModel):
    purpose: str = Field(min_length=1, max_length=100)
    long_url: str = Field(min_length=1, max_length=1000) 
    rate_limit: int | None = Field(default=None)
    expires_at: datetime

class URLCreate(URLBase):
    pass

class URLResponse(URLBase):
    id: int
    short_url: str
    created_at: datetime
    expires_at: datetime
    purpose: str
    access_group_id: int | None = Field(default=None)
    user_id: int

class URLUpdate(BaseModel):
    access_group_id: int | None  = Field(default=None)
    expires_at: datetime | None = Field(default=None)
    rate_limit: int | None = Field(default=None)
    purpose: str | None = Field(default=None, min_length=1, max_length=100)
    long_url: str | None  = Field(default=None, min_length=1, max_length=1000) 

# Pagination schema 
class PaginatedURLResponse(BaseModel):
    urls: list[URLResponse]
    total: int
    skip: int
    limit: int
    has_more: bool

class PaginatedAccessGroupResponse(BaseModel):
    access_groups: list[AccessGroupResponse]
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
    url_id: int

class CreateClickLog(ClickLogs):
    pass

class ClickLogResponse(ClickLogs):
    id: int
    click_at: datetime

class PaginatedClickLogResponse(BaseModel):
    click_logs: list[ClickLogs]
    total: int
    skip: int
    limit: int
    has_more: bool


class AccessLog(BaseModel):
    email: str
    access_group_id: int
    access_status: str

class CreateAccessLog(AccessLog):
    pass

class AccessLogResponse(AccessLog):
    id: int
    updated_at: datetime
    

class PaginatedAccessLogResponse(BaseModel):
    access_logs: list[AccessLogResponse]
    total: int
    skip: int
    limit: int
    has_more: bool
