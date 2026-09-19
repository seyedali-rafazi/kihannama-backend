from typing import Optional, List, Any, Dict
from pydantic import BaseModel

class SpaceStationBase(BaseModel):
    slug: str
    object_name: str
    norad_cat_id: str
    object_id: Optional[str] = None
    epoch: Optional[str] = None
    mean_motion: float
    eccentricity: float
    inclination: float
    ra_of_asc_node: float
    arg_of_pericenter: float
    mean_anomaly: float
    altitude: float
    velocity: float
    period: float
    station_group: str
    station_type: str
    status: str = "operational"
    year: int = 2026
    name_fa: Optional[str] = None
    operator_en: str
    operator_fa: str
    description_en: Optional[str] = None
    description_fa: Optional[str] = None
    badge_en: Optional[str] = None
    badge_fa: Optional[str] = None
    image_url: Optional[str] = None
    abilities_en: Optional[List[str]] = None
    abilities_fa: Optional[List[str]] = None
    infographic_left: Optional[List[Dict[str, Any]]] = None
    infographic_right: Optional[List[Dict[str, Any]]] = None

class SpaceStationResponse(SpaceStationBase):
    id: int

    class Config:
        from_attributes = True

class SpaceStationListResponse(BaseModel):
    total: int
    page: int = 1
    limit: int = 12
    stations: List[SpaceStationResponse]


class GroundStationBase(BaseModel):
    id: str
    name: str
    image: Optional[str] = None
    color: Optional[List[int]] = None
    badge_en: Optional[str] = None
    badge_fa: Optional[str] = None
    operator_en: str
    operator_fa: str
    year: int
    category: str
    secondary: str
    sort_metric: float
    steps: int = 4
    description_en: Optional[str] = None
    description_fa: Optional[str] = None
    abilities_en: Optional[List[str]] = None
    abilities_fa: Optional[List[str]] = None
    center_caption_en: Optional[str] = None
    center_caption_fa: Optional[str] = None
    infographic_left: Optional[List[Dict[str, Any]]] = None
    infographic_right: Optional[List[Dict[str, Any]]] = None


class GroundStationResponse(GroundStationBase):
    class Config:
        from_attributes = True


class GroundStationListResponse(BaseModel):
    total: int
    page: int = 1
    limit: int = 12
    stations: List[GroundStationResponse]

