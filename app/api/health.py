from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text, select, func
from ..database import get_db, mongo_client, mongo_db
from ..models.satellite import Satellite
from ..models.station import SpaceStation, GroundStation
from ..models.launcher import Launcher

router = APIRouter()

@router.get("")
async def check_health(db: AsyncSession = Depends(get_db)):
    postgres_status = "error"
    satellite_count = 0
    space_station_count = 0
    ground_station_count = 0
    launcher_count = 0
    
    try:
        await db.execute(text("SELECT 1"))
        postgres_status = "connected"
        sat_res = await db.execute(select(func.count(Satellite.id)))
        satellite_count = sat_res.scalar() or 0
        stn_res = await db.execute(select(func.count(SpaceStation.id)))
        space_station_count = stn_res.scalar() or 0
        gstn_res = await db.execute(select(func.count(GroundStation.id)))
        ground_station_count = gstn_res.scalar() or 0
        lnc_res = await db.execute(select(func.count(Launcher.id)))
        launcher_count = lnc_res.scalar() or 0
    except Exception as e:
        postgres_status = f"disconnected ({str(e)})"

    mongo_status = "disconnected"
    if mongo_client:
        try:
            await mongo_client.admin.command('ping')
            mongo_status = "connected"
        except Exception:
            mongo_status = "disconnected"

    return {
        "status": "healthy",
        "app": "KihanNama Backend API",
        "version": "1.0.0",
        "databases": {
            "postgresql": postgres_status,
            "mongodb": mongo_status,
        },
        "counts": {
            "satellites": satellite_count,
            "space_stations": space_station_count,
            "ground_stations": ground_station_count,
            "launchers": launcher_count,
        }
    }

