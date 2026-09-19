from typing import Any, Dict, List, Optional
from pydantic import BaseModel

class CzmlDocumentClock(BaseModel):
    interval: str
    currentTime: str
    multiplier: float = 60.0
    range: str = "LOOP"
    step: str = "SYSTEM_CLOCK_MULTIPLIER"

class CzmlPacket(BaseModel):
    id: str
    name: Optional[str] = None
    availability: Optional[str] = None
    clock: Optional[CzmlDocumentClock] = None
    polyline: Optional[Dict[str, Any]] = None
    position: Optional[Dict[str, Any]] = None
    billboard: Optional[Dict[str, Any]] = None
    label: Optional[Dict[str, Any]] = None

    class Config:
        extra = "allow"

class CzmlDocumentResponse(BaseModel):
    count: int
    interval: str
    czml: List[Dict[str, Any]]
