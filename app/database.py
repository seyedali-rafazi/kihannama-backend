import logging
from typing import AsyncGenerator, Optional
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from .config import settings

logger = logging.getLogger("kihannama.database")

# SQLAlchemy Declarative Base
Base = declarative_base()

# Async PostgreSQL Engine & Sessionmaker
async_engine = create_async_engine(
    settings.ASYNC_DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
    pool_recycle=300,
)

AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# MongoDB Client & Database (Optional/Configurable)
mongo_client: Optional[AsyncIOMotorClient] = None
mongo_db: Optional[AsyncIOMotorDatabase] = None

async def init_mongo() -> bool:
    global mongo_client, mongo_db
    try:
        mongo_client = AsyncIOMotorClient(settings.MONGODB_URL, serverSelectionTimeoutMS=2000)
        # Verify connection
        await mongo_client.admin.command('ping')
        mongo_db = mongo_client[settings.MONGODB_DB_NAME]
        logger.info("MongoDB connected successfully.")
        return True
    except Exception as e:
        logger.warning(f"MongoDB connection skipped or unavailable: {e}")
        mongo_client = None
        mongo_db = None
        return False

async def close_mongo():
    global mongo_client
    if mongo_client:
        mongo_client.close()
        logger.info("MongoDB connection closed.")

async def init_db():
    # Create PostgreSQL tables
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("PostgreSQL database tables initialized.")
    
    # Try connecting to MongoDB
    await init_mongo()

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
