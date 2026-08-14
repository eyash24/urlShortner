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

)

from config import settings
from datetime import timedelta, UTC, datetime
from auth import CurrentUser

router = APIRouter()


