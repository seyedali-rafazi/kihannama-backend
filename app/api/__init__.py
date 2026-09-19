from fastapi import APIRouter
from .health import router as health_router
from .satellites import router as satellites_router
from .stations import router as stations_router
from .launchers import router as launchers_router
from .czml import router as czml_router

api_router = APIRouter()
api_router.include_router(health_router, prefix="/health", tags=["Health"])
api_router.include_router(satellites_router, prefix="/satellites", tags=["Satellites"])
api_router.include_router(stations_router, prefix="/stations", tags=["Space & Ground Stations"])
api_router.include_router(launchers_router, prefix="/launchers", tags=["Launchers"])
api_router.include_router(czml_router, prefix="/czml", tags=["CZML"])

