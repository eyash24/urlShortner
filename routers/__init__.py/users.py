from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
    Query,
    BackgroundTasks
)

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import delete as sql_delete

import models
from database import get_url_db
from schema import (
    UserCreate,
    UserUpdate,
    UserPublic,
    UserPrivate,
    Token,
    PaginatedURLResponse,
    ChangePasswordRequest,
    ForgotPasswordRequest,
    ResetPasswordRequest
)

from datetime import timedelta, UTC, datetime
from fastapi.security import OAuth2PasswordRequestForm

from auth import (
    CurrentUser,
    create_access_token,
    hash_password,
    verify_password,
    generate_reset_token,
    hash_reset_token
)

from config import settings
from starlette.concurrency import run_in_threadpool

from email_utils import send_password_reset_email
