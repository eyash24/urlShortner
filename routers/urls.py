from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status
)

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import delete as sql_delete

import models
from database import get_url_db
from schema import (
    URLCreate,
    URLResponse,
    URLUpdate
)

from auth import CurrentUser
from utils import create_short_url

router = APIRouter()

@router.get('/', response_model=list[URLResponse])
async def get_urls(
    db: Annotated[AsyncSession, Depends(get_url_db)],
    current_user: CurrentUser
):
    result = await db.execute(
        select(models.Url)
        .where(models.Url.user_id == current_user.id)
        .order_by(models.Url.created_at.desc())
    )
    urls = result.scalars().all()
    return urls

@router.post(
    '',
    response_models=URLResponse,
    status_code=status.HTTP_201_CREATED
)
async def create_url(
    url: URLCreate, 
    current_user: CurrentUser, 
    db: Annotated[AsyncSession, Depends(get_url_db)],
    access_group_id: int 
):

    short_url = create_short_url()
    
    new_url = models.Url(
        long_url = url.long_url,
        short_url = short_url,
        purpose = url.purpose,
        rate_limit = url.rate_limit,
        expires_at = url.expires_at,
        access_group_id = access_group_id,
        user_id = current_user.id
    )

    db.add(new_url)
    await db.commit()
    await db.refresh(new_url, attribute_names=['author', 'access_group'])
    return new_url


@router.get('/{url_id}', response_model=URLResponse)
async def get_url_info(
    url_id: int,
    db: Annotated[AsyncSession, Depends(get_url_db)],
    current_user: CurrentUser
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

    if url_info.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Not authorised to retrieve url infomation'
        )
    
    return url_info


@router.put('/{url_id}', response_model=URLResponse)
async def update_url_full(
    url_id: int,
    url_data: URLCreate,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_url_db)]
):
    result = await db.execute(
        select(models.Url)
        .where(models.Url.id == url_id and models.Url.user_id == current_user)
    )
    url = result.scalars().first()

    if not url:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Url not found'
        )

    if url.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Not authorised to update url information'
        )

    url.access_group_id = url_data.access_group_id
    url.expires_at = url_data.expires_at
    url.rate_limit = url_data.rate_limit
    url.purpose = url_data.purpose
    url.long_url = url_data.long_url

    await db.commit()
    await db.refresh(url, attribute_names=['author', 'access_group'])


@router.patch('/{url_id}', response_model=URLResponse)
async def update_url_partial(
    url_id: int,
    url_data: URLUpdate,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_url_db)]
):
    result = await db.execute(
        select(models.Url)
        .where(models.Url.id == url_id)
    )
    url = result.scalars().first()
    if not url:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Url not found'
        )

    if url.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Not authorised to update url information'
        )

    update_data = url_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(url, field, value)

    await db.commit()
    await db.refresh(url)
    return url


@router.delete('/{url_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_url(
    url_id: int,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_url_db)]
):
    result = await db.execute(
        select(models.Url)
        .where(models.Url.id == url_id)
    )
    url = result.scalars().first()
    if not url:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Url not found'
        )

    if url.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Not authorised to delete url'
        )

    await db.delete(url)
    await db.commit()
    


