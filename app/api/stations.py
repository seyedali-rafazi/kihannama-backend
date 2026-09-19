from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from ..database import get_db
from ..models.station import SpaceStation, GroundStation
from ..schemas.station import (
    SpaceStationResponse,
    SpaceStationListResponse,
    GroundStationResponse,
    GroundStationListResponse
)
from ..services.czml_generator import generate_czml_dataset, satellite_to_czml_packets, create_czml_document

router = APIRouter()


@router.get("/space", response_model=SpaceStationListResponse)
async def list_space_stations(
    group: Optional[str] = Query(None, description="Filter by group (ISS, Tiangong)"),
    type: Optional[str] = Query(None, description="Filter by type (coreModule, labModule, crewCraft, cargoCraft)"),
    search: Optional[str] = Query(None, description="Search by name or operator"),
    db: AsyncSession = Depends(get_db)
):
    query = select(SpaceStation)
    filters = []

    if group:
        filters.append(SpaceStation.station_group.ilike(f"%{group.strip()}%"))
    if type:
        filters.append(SpaceStation.station_type == type.strip())
    if search:
        pattern = f"%{search.strip()}%"
        filters.append(or_(
            SpaceStation.object_name.ilike(pattern),
            SpaceStation.name_fa.ilike(pattern),
            SpaceStation.operator_en.ilike(pattern),
            SpaceStation.operator_fa.ilike(pattern)
        ))

    if filters:
        query = query.where(*filters)

    query = query.order_by(SpaceStation.id.asc())
    result = await db.execute(query)
    stations = result.scalars().all()

    return {
        "total": len(stations),
        "stations": stations
    }

@router.get("/space/{identifier}", response_model=SpaceStationResponse)
async def get_space_station(identifier: str, db: AsyncSession = Depends(get_db)):
    ident = identifier.strip()
    result = await db.execute(
        select(SpaceStation).where(
            or_(
                SpaceStation.slug == ident,
                SpaceStation.norad_cat_id == ident,
                SpaceStation.object_name.ilike(ident)
            )
        )
    )
    station = result.scalar_one_or_none()
    if not station:
        raise HTTPException(status_code=404, detail=f"Space station '{identifier}' not found")
    return station

@router.get("/space/{identifier}/czml")
async def get_space_station_czml(identifier: str, db: AsyncSession = Depends(get_db)):
    ident = identifier.strip()
    result = await db.execute(
        select(SpaceStation).where(
            or_(
                SpaceStation.slug == ident,
                SpaceStation.norad_cat_id == ident,
                SpaceStation.object_name.ilike(ident)
            )
        )
    )
    station = result.scalar_one_or_none()
    if not station:
        raise HTTPException(status_code=404, detail=f"Space station '{identifier}' not found")

    sat_adapted = {
        "norad_id": station.norad_cat_id,
        "name": station.object_name,
        "altitude": station.altitude,
        "inclination": station.inclination,
        "raan": station.ra_of_asc_node,
        "mean_anomaly": station.mean_anomaly,
        "period": station.period,
        "category": "Space Station",
        "orbit_class": "LEO",
    }
    
    doc = create_czml_document(name=f"{station.object_name} Orbit CZML")
    packets = satellite_to_czml_packets(sat_adapted, path_width=2.5)
    return [doc, *packets]


@router.get("/ground", response_model=GroundStationListResponse)
async def list_ground_stations(
    category: Optional[str] = Query(None, description="Filter by category (tracking, communications, launch, research)"),
    region: Optional[str] = Query(None, description="Filter by region (americas, europe, asia, middleEast)"),
    search: Optional[str] = Query(None, description="Search by name, operator, or description"),
    sort: Optional[str] = Query(None, description="Sort order: nameAsc, nameDesc, yearAsc, yearDesc, metricAsc, metricDesc"),
    db: AsyncSession = Depends(get_db)
):
    query = select(GroundStation)
    filters = []

    if category and category != "all":
        filters.append(GroundStation.category == category.strip())
    if region and region != "all":
        filters.append(GroundStation.secondary == region.strip())
    if search:
        pattern = f"%{search.strip()}%"
        filters.append(
            or_(
                GroundStation.name.ilike(pattern),
                GroundStation.operator_en.ilike(pattern),
                GroundStation.operator_fa.ilike(pattern),
                GroundStation.description_en.ilike(pattern),
                GroundStation.description_fa.ilike(pattern),
            )
        )

    if filters:
        query = query.where(*filters)

    if sort == "nameAsc":
        query = query.order_by(GroundStation.name.asc())
    elif sort == "nameDesc":
        query = query.order_by(GroundStation.name.desc())
    elif sort == "yearAsc":
        query = query.order_by(GroundStation.year.asc())
    elif sort == "yearDesc":
        query = query.order_by(GroundStation.year.desc())
    elif sort == "metricAsc":
        query = query.order_by(GroundStation.sort_metric.asc())
    elif sort == "metricDesc":
        query = query.order_by(GroundStation.sort_metric.desc())
    else:
        query = query.order_by(GroundStation.sort_metric.desc())

    result = await db.execute(query)
    stations = result.scalars().all()

    return {
        "total": len(stations),
        "stations": stations
    }


@router.get("/ground/{identifier}", response_model=GroundStationResponse)
async def get_ground_station(identifier: str, db: AsyncSession = Depends(get_db)):
    ident = identifier.strip()
    result = await db.execute(
        select(GroundStation).where(
            or_(
                GroundStation.id == ident,
                GroundStation.name.ilike(ident)
            )
        )
    )
    station = result.scalar_one_or_none()
    if not station:
        raise HTTPException(status_code=404, detail=f"Ground station '{identifier}' not found")
    return station

