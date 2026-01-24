import os
from typing import AsyncGenerator
from dotenv import load_dotenv

from sqlalchemy.ext.asyncio import (
    create_async_engine,AsyncSession,async_sessionmaker
)
from sqlalchemy.orm import declarative_base

load_dotenv()

DATABASE_URL=os.getenv("DATABASE_URL")


if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not set")

engine=create_async_engine(DATABASE_URL,echo=False,future=True)



async_session_maker=async_sessionmaker(
    engine,
    expire_on_commit=False,
    class_=AsyncSession
)

Base=declarative_base()

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session

