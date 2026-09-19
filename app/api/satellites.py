from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from ..database import get_db
from ..models.satellite import Satellite
from ..schemas.satellite import SatelliteResponse, SatelliteListResponse
from ..services.czml_generator import generate_czml_dataset, satellite_to_czml_packets, create_czml_document

router = APIRouter()

@router.get("", response_model=SatelliteListResponse)
async def list_satellites(
    search: Optional[str] = Query(None, description="Search by name or NORAD ID"),
    orbit_class: Optional[str] = Query(None, description="Filter by LEO, MEO, GEO, HEO"),
    category: Optional[str] = Query(None, description="Filter by category"),
    sort: Optional[str] = Query(None, description="Sort order: nameAsc, nameDesc, altitudeAsc, altitudeDesc, periodAsc, periodDesc"),
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=500),
    db: AsyncSession = Depends(get_db)
):
    query = select(Satellite)
    count_query = select(func.count(Satellite.id))

    filters = []
    if search:
        search_pattern = f"%{search.strip()}%"
        filters.append(or_(Satellite.name.ilike(search_pattern), Satellite.norad_id.ilike(search_pattern)))
    if orbit_class:
        filters.append(Satellite.orbit_class == orbit_class.upper())
    if category:
        filters.append(Satellite.category.ilike(f"%{category.strip()}%"))

    if filters:
        query = query.where(*filters)
        count_query = count_query.where(*filters)

    total_res = await db.execute(count_query)
    total = total_res.scalar() or 0

    if sort == "nameAsc":
        query = query.order_by(Satellite.name.asc())
    elif sort == "nameDesc":
        query = query.order_by(Satellite.name.desc())
    elif sort == "altitudeAsc":
        query = query.order_by(Satellite.altitude.asc())
    elif sort == "altitudeDesc":
        query = query.order_by(Satellite.altitude.desc())
    elif sort == "periodAsc":
        query = query.order_by(Satellite.period.asc())
    elif sort == "periodDesc":
        query = query.order_by(Satellite.period.desc())
    else:
        query = query.order_by(Satellite.id.asc())

    query = query.offset((page - 1) * limit).limit(limit)
    result = await db.execute(query)
    satellites = result.scalars().all()

    return {
        "total": total,
        "page": page,
        "limit": limit,
        "satellites": satellites
    }

@router.get("/czml")
async def get_satellites_czml(
    search: Optional[str] = Query(None, description="Filter by satellite name"),
    orbit_class: Optional[str] = Query(None, description="Filter by LEO, MEO, GEO"),
    category: Optional[str] = Query(None, description="Filter by category"),
    norad_ids: Optional[str] = Query(None, description="Comma-separated NORAD IDs"),
    limit: int = Query(50, ge=1, le=250, description="Max satellites in CZML payload"),
    db: AsyncSession = Depends(get_db)
):
    query = select(Satellite)
    filters = []

    if norad_ids:
        ids_list = [i.strip() for i in norad_ids.split(",") if i.strip()]
        filters.append(Satellite.norad_id.in_(ids_list))
    else:
        if search:
            filters.append(Satellite.name.ilike(f"%{search.strip()}%"))
        if orbit_class:
            filters.append(Satellite.orbit_class == orbit_class.upper())
        if category:
            filters.append(Satellite.category.ilike(f"%{category.strip()}%"))

    if filters:
        query = query.where(*filters)

    query = query.limit(limit)
    result = await db.execute(query)
    satellites = result.scalars().all()

    czml_data = generate_czml_dataset(satellites, name=f"KihanNama Active Satellites ({len(satellites)})")
    return czml_data

@router.get("/{norad_id}", response_model=SatelliteResponse)
async def get_satellite(norad_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Satellite).where(Satellite.norad_id == norad_id.strip()))
    satellite = result.scalar_one_or_none()
    if not satellite:
        raise HTTPException(status_code=404, detail=f"Satellite with NORAD ID {norad_id} not found")
    return satellite

@router.get("/{norad_id}/czml")
async def get_single_satellite_czml(norad_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Satellite).where(Satellite.norad_id == norad_id.strip()))
    satellite = result.scalar_one_or_none()
    if not satellite:
        raise HTTPException(status_code=404, detail=f"Satellite with NORAD ID {norad_id} not found")
    
    doc = create_czml_document(name=f"{satellite.name} Orbit CZML")
    packets = satellite_to_czml_packets(satellite, path_width=2.0)
    return [doc, *packets]
