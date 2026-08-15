from typing import Annotated
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status
)

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

import models
from database import get_url_db
from schema import (
    AccessGroupResponse,
    AccessGroupCreate,
    AccessGroupUpdate,
    AccessMailCreate,
    AccessMailResponse
)

from auth import CurrentUser

router = APIRouter()

# Access Group Management
@router.get('/', response_model=list[AccessGroupResponse])
async def get_access_groups(
    db: Annotated[AsyncSession, Depends(get_url_db)],
    current_user: CurrentUser
):
    result = await db.execute(
        select(models.AccessGroupManage)
        .where(models.AccessGroupManage.user_id == current_user.id)
    )
    access_groups = result.scalars().all()
    return access_groups


@router.post(
    '',
    response_model=AccessGroupResponse,
    status_code=status.HTTP_201_CREATED
)
async def create_access_group(
    access_group: AccessGroupCreate,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_url_db)]
):
    result = await db.execute(
        select(models.AccessGroupManage)
        .where(
                models.AccessGroupManage.group_name == access_group.group_name,
                models.AccessGroupManage.user_id == current_user.id
            )
    )

    access_group_exist = result.scalars().first()
    if access_group_exist:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Access group name already exist'
        )

    new_access_group = models.AccessGroupManage(
        group_name = access_group.group_name,
        expires_at = access_group.expires_at,
        user_id = current_user.id
    )

    db.add(new_access_group)
    await db.commit()
    await db.refresh(new_access_group)
    return new_access_group


@router.get('/{access_group_id}', response_model=AccessGroupResponse)
async def get_access_group_via_id(
    access_group_id: int,
    db: Annotated[AsyncSession, Depends(get_url_db)],
    current_user: CurrentUser
):
    result = await db.execute(
        select(models.AccessGroupManage)
        .where(models.AccessGroupManage.id == access_group_id)
    )
    access_group = result.scalars().first()
    if not access_group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Access group not found'
        )

    if access_group.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Not authorised to retrieve access group information'
        )

    return access_group


@router.put('/{access_group_id}', response_model=AccessGroupResponse)
async def update_access_group_full(
    access_group_id: int,
    access_group_data: AccessGroupUpdate,
    db: Annotated[AsyncSession, Depends(get_url_db)],
    current_user: CurrentUser
):
    result = await db.execute(
        select(models.AccessGroupManage)
        .where(models.AccessGroupManage.id == access_group_id)
    )
    access_group = result.scalars().first()

    if not access_group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Access group not found'
        )

    if access_group.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Not authorised to update access group information'
        )

    result = await db.execute(
        select(models.AccessGroupManage)
        .where(
                models.AccessGroupManage.group_name == access_group.group_name,
                models.AccessGroupManage.user_id == current_user.id
            )
    )

    access_group_exist = result.scalars().first()
    if access_group_exist:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Access group name already exist'
        )

    access_group.group_name = access_group_data.group_name
    access_group.expires_at = access_group_data.expires_at

    await db.commit()
    await db.refresh(access_group)
    

@router.patch('/access_group_id', response_model=AccessGroupResponse)
async def update_access_group_partial(
    access_group_id: int,
    access_group_data: AccessGroupUpdate,
    db: Annotated[AsyncSession, Depends(get_url_db)],
    current_user: CurrentUser
):
    result = await db.execute(
        select(models.AccessGroupManage)
        .where(models.AccessGroupManage.id == access_group_id)
    )
    access_group = result.scalars().first()

    if not access_group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Access group not found'
        )

    if access_group.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Not authorised to update access group information'
        )

    if access_group_data.group_name:
        result = await db.execute(
            select(models.AccessGroupManage)
            .where(
                models.AccessGroupManage.user_id == current_user.id,
                models.AccessGroupManage.group_name == access_group_data.group_name
            )
        )

        access_group_exist = result.scalars().first()
        if access_group_exist:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Access group name already exist'
            )

    update_data = access_group_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(access_group, field, value)

    await db.commit()
    await db.refresh(access_group)
    return access_group


@router.delete('/{access_group_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_access_group(
    access_group_id: int,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_url_db)]
):
    result = await db.execute(
        select(models.AccessGroupManage)
        .options(selectinload(models.AccessGroupManage.author))
        .where(
            models.AccessGroupManage.id == access_group_id,
        )
    )
    access_group = result.scalars().first()
    if not access_group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Access group not found'
        )

    if access_group.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Not authorised to delete access group'
        )

    await db.delete(access_group)
    await db.commit()
    
    
# Access Mail
@router.get('/{access_group_id}', response_model=list[AccessMailResponse])
async def get_access_mails(
    access_group_id: int,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_url_db)]
):
    result = await db.execute(
        select(models.AccessGroupManage)
        .where(
            models.AccessGroupManage.id == access_group_id,
            models.AccessGroupManage.user_id == current_user.id
        )
    )
    access_group = result.scalars().first()

    if not access_group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Access group not found'
        )

    result = await db.execute(
        select(models.AccessMails)
        .where(
                models.AccessMails.access_group_id == access_group_id,
                models.AccessMails.status == True
            )
    )
    mails = result.scalars().all()
    return mails


@router.post('/{access_group_id}', response_model=list[AccessMailResponse])
async def create_access_mails_bulk(
    access_group_id: int,
    current_user: CurrentUser,
    access_mails_list: list[AccessMailCreate],
    db: Annotated[AsyncSession, Depends(get_url_db)]
):
    result = await db.execute(
        select(models.AccessGroupManage)
        .where(
            models.AccessGroupManage.id == access_group_id,
            models.AccessGroupManage.user_id == current_user.id
        )
    )
    access_group = result.scalars().first()

    if not access_group:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Not authorised to create access mails'
        )

    access_mail_created = []

    for access_mail in access_mails_list:
        new_access_mail = models.AccessMails(
            email = access_mail.email,
            access_group_id = access_group_id,
            status=True
        )

        db.add(new_access_mail)
        await db.commit()
        await db.refresh(new_access_mail)
        access_mail_created.append(new_access_mail)

    return access_mail_created

@router.delete('/{access_mail_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_access_mail_via_id(
    access_mail_id: int,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_url_db)]
):
    result = await db.execute(
        select(models.AccessMails)
        .where(models.AccessMails.id == access_mail_id)
    )

    access_mail = result.scalar().first()

    if not access_mail:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Access Mail not found'
        )

    result = await db.execute(
        select(models.AccessGroupManage)
        .where(
            models.AccessGroupManage.id == access_mail.access_group_id,
            models.AccessGroupManage.user_id == current_user.id
        )
    )

    access_group_check = result.scalars().first()
    if not access_group_check:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Not authorised to delete acces mail'
        )

    await db.delete(access_mail)
    await db.commit()


    