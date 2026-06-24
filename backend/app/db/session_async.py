from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.core.config import settings

async_engine = create_async_engine(settings.database_url, pool_pre_ping=True, future=True)
AsyncSessionLocal = async_sessionmaker(bind=async_engine, autoflush=False, expire_on_commit=False)
