from typing import Annotated

from fastapi import FastAPI, Request, HTTPException, status, Depends
from contextlib import asynccontextmanager

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from database import Base, engine, get_url_db
from routers import users, urls, access_groups

@asynccontextmanager
async def lifespan(_app: FastAPI):
    async with engine.begin() as main_conn:
        await main_conn.run_sync(Base.metadata.create_all)
    yield

    await engine.dispose()


app = FastAPI(lifespan=lifespan)

app.get('/', include_in_schema=False)
async def home(request: Request):
    return {'message':'Welcome to URL Shortner'}


app.include_router(users.router, prefix='/api/users', tags=['user'])
