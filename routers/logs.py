from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    Query,
    HTTPException,
    status
)

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

import models
from database import get_url_db
from schema import (
    CreateClickLog,
    CreateAccessLog,
    PaginatedAccessLogResponse,
    PaginatedClickLogResponse,
    ClickLogResponse,
    AccessLogResponse
)

from auth import CurrentUser


router = APIRouter()

# Click Logs
@router.get(
    '/click/{url_id}',
    response_model=PaginatedClickLogResponse
)
async def get_url_click_logs(
    url_id: int,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_url_db)],
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1,le=100)] = 10
):
    result = await db.execute(
        select(models.Url)
        .where(models.Url.id == url_id)
    )

    url_info = result.scalars().first()
    if not url_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Url not found'
        )

    if url_info.user_id != current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Not authorised to view click logs'
        )

    count_log = await db.execute(
        select(func.count())
        .select_from(models.ClickLogs)
        .where(models.ClickLogs.url_id == url_id)
    )
    total = count_log.scalars() or 0

    result = await db.execute(
        select(models.ClickLogs)
        .where(models.ClickLogs.url_id == url_id)
        .order_by(models.ClickLogs.click_at.desc())
        .offset(skip)
        .limit(limit)
    )

    clicklogs = result.scalars().all()
    click_logs = PaginatedClickLogResponse(
        click_logs=clicklogs,
        total=total
    )
    return click_logs
    

@router.post(
    '/click', 
    status_code=status.HTTP_201_CREATED,
    response_model=ClickLogResponse
)
async def create_clicklog(
    click_log_data: CreateClickLog ,
    db: Annotated[AsyncSession, Depends(get_url_db)]
):
    new_click_log = models.ClickLogs(
        url_id=click_log_data.url
    )

    db.add(new_click_log)
    await db.commit()
    await db.refresh(new_click_log)
    return new_click_log



# Access logs
@router.get(
    '/access/{access_group_id}',
    response_model=PaginatedAccessLogResponse
)
async def get_access_logs(
    access_group_id: int, 
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_url_db)],
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1,le=100)] = 10
):
    result = await db.execute(
        select(models.AccessGroupManage)
        .where(models.AccessGroupManage.id == access_group_id)
    )
    access_group_check = result.scalars().first()
    if not access_group_check:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Access group not found'
        )

    if access_group_check.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Not authorised to access access-logs'
        )
    
    count_log = await db.execute(
        select(func.count())
        .select_from(models.AccessLog)
        .where(models.AccessLog.access_group_id == access_group_id)
    )
    total = count_log.scalars() or 0

    result = await db.execute(
        select(models.AccessLog)
        .where(models.AccessLog.access_group_id == access_group_id)
        .order_by(models.AccessLog.click_at.desc())
        .offset(skip)
        .limit(limit)
    )

    accesslogs = result.scalars().all()
    access_logs = PaginatedClickLogResponse(
        click_logs=accesslogs,
        total=total
    )
    return access_logs


@router.post('/access', response_model=AccessLogResponse, status_code=status.HTTP_201_CREATED)
async def create_access_log(
    access_group_data: CreateAccessLog,
    db: Annotated[AsyncSession, Depends(get_url_db)]
):
    new_access_log = models.AccessLog(
        email = access_group_data.email,
        access_group_id = access_group_data.access_group_id,
        status=access_group_data.status
    )

    db.add(new_access_log)
    await db.commit()
    await db.refresh(new_access_log)
    return new_access_log


    

    



