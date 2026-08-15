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
    access_group: list[AccessGroupResponse] | None

class UserUpdate(BaseModel):
    username: str | None = Field(default=None,  min_length=1, max_length=50)
    email: EmailStr | None = Field(default=None, max_length=120)

class Token(BaseModel):
    access_token: str
    token_type: str

# Access Mail Schema
class AccessMails(BaseModel):
    email: EmailStr
    status: bool
    updated_at: datetime
    access_group: int

class AccessMailCreate(AccessMails):
    pass

class AccessMailUpdate(AccessMails):
    pass

class AccessMailLogs(AccessMails):
    pass


# Access Group Shema
class AccessGroup(BaseModel):
    author: UserBase
    group_name: str
    emails: list[AccessMails]

class AccessGroupCreate(AccessGroup):
    user_id: int

class AccessGroupResponse(AccessGroup):
    created_at: datetime
    id: int
    user_id: int

class AccessGroupUpdate(BaseModel):
    id: int
    group_name: str | None = Field(default=None)
    emails: list[AccessMails] | None = Field(default=None)

# URL schema
class URLBase(BaseModel):
    purpose: str = Field(min_length=1, max_length=100)
    long_url: str = Field(min_length=1, max_length=1000)
    rate_limit: int | None = Field(default=None)
    expires_at: datetime

class URLCreate(URLBase):
    purpose: str
    author: UserPrivate
    pass

class URLResponse(URLBase):
    model_config = ConfigDict(from_attributes=True)
    short_url: str
    access_group: AccessGroupResponse
    created_at: datetime
    expires_at: datetime
    purpose: str


class URLUpdate(BaseModel):
    access_group_id: AccessGroup | None
    expires_at: datetime | None
    rate_limit: int | None
    purpose: str | None = Field(min_length=1, max_length=100)
    long_url: str | None = Field(min_length=1, max_length=1000)

# Pagination schema 
class PaginatedURLResponse(BaseModel):
    urls: list[URLResponse]
    total: int
    skip: int
    limit: int
    has_more: bool

class PaginatedURLAccessResponse(BaseModel):
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
    url_id: URLResponse
    click_at: datetime
    method: str

class AppendClickLog(ClickLogs):
    pass


class AccessLog(BaseModel):
    email: str
    group_id: int
    access_status: str
    updated_at: datetime

class AppendAccessLog(BaseModel):
    pass