from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from ..database import get_db
from ..models.launcher import Launcher
from ..schemas.launcher import LauncherResponse, LauncherListResponse

router = APIRouter()

@router.get("", response_model=LauncherListResponse)
async def list_launchers(
    category: Optional[str] = Query(None, description="Filter by category (heavyLift, mediumLift, smallLift, reusable)"),
    status: Optional[str] = Query(None, description="Filter by status (active, legacy, developmental)"),
    search: Optional[str] = Query(None, description="Search by name, operator, or description"),
    sort: Optional[str] = Query(None, description="Sort order: nameAsc, nameDesc, yearAsc, yearDesc, metricAsc, metricDesc"),
    db: AsyncSession = Depends(get_db)
):
    query = select(Launcher)
    filters = []

    if category and category != "all":
        filters.append(Launcher.category == category.strip())
    if status and status != "all":
        filters.append(Launcher.secondary == status.strip())
    if search:
        pattern = f"%{search.strip()}%"
        filters.append(
            or_(
                Launcher.name.ilike(pattern),
                Launcher.operator_en.ilike(pattern),
                Launcher.operator_fa.ilike(pattern),
                Launcher.description_en.ilike(pattern),
                Launcher.description_fa.ilike(pattern),
            )
        )

    if filters:
        query = query.where(*filters)

    # Sort
    if sort == "nameAsc":
        query = query.order_by(Launcher.name.asc())
    elif sort == "nameDesc":
        query = query.order_by(Launcher.name.desc())
    elif sort == "yearAsc":
        query = query.order_by(Launcher.year.asc())
    elif sort == "yearDesc":
        query = query.order_by(Launcher.year.desc())
    elif sort == "metricAsc":
        query = query.order_by(Launcher.sort_metric.asc())
    elif sort == "metricDesc":
        query = query.order_by(Launcher.sort_metric.desc())
    else:
        query = query.order_by(Launcher.sort_metric.desc())

    result = await db.execute(query)
    launchers = result.scalars().all()

    return {
        "total": len(launchers),
        "launchers": launchers
    }

@router.get("/{id}", response_model=LauncherResponse)
async def get_launcher(id: str, db: AsyncSession = Depends(get_db)):
    launcher_id = id.strip()
    result = await db.execute(
        select(Launcher).where(
            or_(
                Launcher.id == launcher_id,
                Launcher.name.ilike(launcher_id)
            )
        )
    )
    launcher = result.scalar_one_or_none()
    if not launcher:
        raise HTTPException(status_code=404, detail=f"Launcher '{id}' not found")
    return launcher
