from typing import Optional, List, Any, Dict
from pydantic import BaseModel

class LauncherBase(BaseModel):
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

class LauncherResponse(LauncherBase):
    class Config:
        from_attributes = True

class LauncherListResponse(BaseModel):
    total: int
    launchers: List[LauncherResponse]
