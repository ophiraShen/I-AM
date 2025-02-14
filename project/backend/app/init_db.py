#I-AM/project/backend/app/init_db.py
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import engine, Base, AsyncSessionLocal
from models import User, Chat, Affirmation, Meditation

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as session:
        # 这里可以添加一些初始数据
        pass

if __name__ == "__main__":
    asyncio.run(init_db()) 