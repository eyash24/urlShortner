from typing import Annotated
import secrets 
from fastapi import Depends

from database import get_url_db
from config import settings
import models

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


async def create_short_url(
    db: Annotated[AsyncSession, Depends(get_url_db)]
) -> str:
    while True:
        hash_hex = secrets.token_hex(settings.secrets_hash_hex)
        short_url = f'{settings.frontend_url}/link/{hash_hex}'

        result = await db.execute(
            select(models.Url)
            .where(models.Url.short_url == short_url)
        )

        url = result.scalar().first()

        if not url:
            return short_url

