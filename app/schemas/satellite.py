from typing import Optional, List
from pydantic import BaseModel, Field

class SatelliteBase(BaseModel):
    norad_id: str
    name: str
    intl_desig: Optional[str] = None
    epoch: Optional[str] = None
    inclination: float
    raan: float
    eccentricity: float
    arg_perigee: float
    mean_anomaly: float
    mean_motion: float
    semi_major_axis: float
    altitude: float
    perigee_altitude: Optional[float] = None
    apogee_altitude: Optional[float] = None
    period: float
    orbit_class: str
    category: Optional[str] = None

class SatelliteResponse(SatelliteBase):
    id: int
    tle_line1: Optional[str] = None
    tle_line2: Optional[str] = None

    class Config:
        from_attributes = True

class SatelliteListResponse(BaseModel):
    total: int
    page: int
    limit: int
    satellites: List[SatelliteResponse]

class SatelliteFilterParams(BaseModel):
    search: Optional[str] = None
    orbit_class: Optional[str] = None
    category: Optional[str] = None
    page: int = Field(1, ge=1)
    limit: int = Field(50, ge=1, le=500)
