from typing import List, Optional
from fastapi import APIRouter, Depends, Query, Body, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ..database import get_db
from ..models.satellite import Satellite
from ..models.station import SpaceStation
from ..services.czml_generator import generate_czml_dataset, satellite_to_czml_packets, create_czml_document
from ..services.tle_parser import parse_tle_file

router = APIRouter()

@router.get("/active")
async def get_active_satellites_czml(
    limit: int = Query(50, ge=1, le=200),
    orbit_class: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    query = select(Satellite)
    if orbit_class:
        query = query.where(Satellite.orbit_class == orbit_class.upper())
    query = query.limit(limit)
    result = await db.execute(query)
    satellites = result.scalars().all()
    return generate_czml_dataset(satellites, name=f"Active Satellites ({len(satellites)})")

@router.get("/space-stations")
async def get_space_stations_czml(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(SpaceStation))
    stations = result.scalars().all()

    sats_adapted = [
        {
            "norad_id": stn.norad_cat_id,
            "name": stn.object_name,
            "altitude": stn.altitude,
            "inclination": stn.inclination,
            "raan": stn.ra_of_asc_node,
            "mean_anomaly": stn.mean_anomaly,
            "period": stn.period,
            "category": "Space Station",
            "orbit_class": "LEO",
        }
        for stn in stations
    ]

    return generate_czml_dataset(sats_adapted, name="Space Stations & Modules CZML", multiplier=60.0)

@router.post("/from-tle")
async def convert_tle_to_czml(tle_text: str = Body(..., media_type="text/plain")):
    lines = [line.strip() for line in tle_text.strip().splitlines() if line.strip()]
    if len(lines) < 2:
        raise HTTPException(status_code=400, detail="Invalid TLE input. Must have at least 2 lines.")

    name = lines[0] if len(lines) >= 3 else "Satellite"
    l1 = lines[1] if len(lines) >= 3 else lines[0]
    l2 = lines[2] if len(lines) >= 3 else lines[1]

    try:
        norad_id = l1[2:7].strip()
        inc = float(l2[8:16])
        raan = float(l2[17:25])
        mean_anomaly = float(l2[43:51])
        mean_motion = float(l2[52:63])
        period_min = 1440.0 / mean_motion
        n_rad_s = (mean_motion * 2.0 * 3.1415926535) / 86400.0
        semi_major_km = pow(398600.4418 / (n_rad_s * n_rad_s), 1.0 / 3.0)
        altitude_km = semi_major_km - 6378.137

        sat = {
            "norad_id": norad_id,
            "name": name,
            "altitude": altitude_km,
            "inclination": inc,
            "raan": raan,
            "mean_anomaly": mean_anomaly,
            "period": period_min,
            "category": "Custom TLE",
            "orbit_class": "LEO" if altitude_km < 2000 else "MEO",
        }
        doc = create_czml_document(name=f"{name} Custom CZML")
        packets = satellite_to_czml_packets(sat)
        return [doc, *packets]
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to parse TLE: {str(e)}")
