import asyncio
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import settings
from .database import init_db, close_mongo, async_engine, AsyncSessionLocal
from .services.seeder import seed_stations, seed_satellites, seed_launchers, seed_ground_stations
from .api import api_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("kihannama.main")

async def background_seed():
    """Background task to seed database without delaying server startup."""
    await asyncio.sleep(1)  # Allow server to bind and start first
    try:
        async with AsyncSessionLocal() as session:
            await seed_stations(session)
            await seed_ground_stations(session)
            await seed_launchers(session)
            await seed_satellites(session, max_count=5000)
    except Exception as e:
        logger.error(f"Background seeding exception: {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing KihanNama backend services...")
    # Initialize DB schema & connections
    await init_db()
    
    # Launch seeder in background
    seed_task = asyncio.create_task(background_seed())
    
    yield
    
    logger.info("Shutting down KihanNama backend services...")
    if not seed_task.done():
        seed_task.cancel()
    await close_mongo()
    await async_engine.dispose()
    logger.info("Cleanup completed.")

app = FastAPI(
    title="KihanNama API",
    description="Space Tracking & Satellite Catalog Backend for KihanNama (کیهان‌نما)",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS configuration
origins = settings.CORS_ORIGINS if isinstance(settings.CORS_ORIGINS, list) else [settings.CORS_ORIGINS]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins if "*" not in origins else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API routes
app.include_router(api_router, prefix="/api")

@app.get("/")
async def root():
    return {
        "message": "Welcome to KihanNama Backend API (کیهان‌نما)",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": {
            "health": "/api/health",
            "satellites": "/api/satellites",
            "satellites_czml": "/api/satellites/czml",
            "space_stations": "/api/stations/space",
            "space_stations_czml": "/api/czml/space-stations"
        }
    }
