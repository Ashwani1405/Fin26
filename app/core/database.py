
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from typing import AsyncGenerator


# Validated Fallback: Use SQLite because Docker is not available on this machine
DATABASE_URL = "sqlite+aiosqlite:///./fin26.db"

engine = create_async_engine(
    DATABASE_URL,
    echo=True,
    future=True
)

AsyncSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for injecting DB sessions into routes."""
    async with AsyncSessionLocal() as session:
        yield session
