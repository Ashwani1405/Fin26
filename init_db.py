
import asyncio
from app.core.database import engine
from app.models.database_schema import Base

async def init_models():
    async with engine.begin() as conn:
        print("Creating tables if not exist...")
        # Drop dependent tables if needed or just create
        # await conn.run_sync(Base.metadata.drop_all) 
        await conn.run_sync(Base.metadata.create_all)
    print("Tables created.")

if __name__ == "__main__":
    asyncio.run(init_models())
