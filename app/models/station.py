from sqlalchemy import Column, Integer, String, Float, DateTime, Text, JSON
from datetime import datetime, timezone
from ..database import Base

class SpaceStation(Base):
    __tablename__ = "space_stations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    slug = Column(String(60), unique=True, index=True, nullable=False)
    object_name = Column(String(100), index=True, nullable=False)
    norad_cat_id = Column(String(10), index=True, nullable=False)
    object_id = Column(String(30), nullable=True)  # COSPAR ID
    epoch = Column(String(50), nullable=True)

    # Orbital parameters
    mean_motion = Column(Float, nullable=False)
    eccentricity = Column(Float, nullable=False)
    inclination = Column(Float, nullable=False)
    ra_of_asc_node = Column(Float, nullable=False)
    arg_of_pericenter = Column(Float, nullable=False)
    mean_anomaly = Column(Float, nullable=False)

    # Derived values
    altitude = Column(Float, nullable=False)       # km
    velocity = Column(Float, nullable=False)       # km/s
    period = Column(Float, nullable=False)         # minutes

    # Metadata & Categorization
    station_group = Column(String(50), index=True, nullable=False)  # ISS, Tiangong, Visiting Craft, etc.
    station_type = Column(String(50), index=True, nullable=False)   # coreModule, labModule, crewCraft, etc.
    status = Column(String(30), default="operational")
    year = Column(Integer, default=2026)

    # Bilingual info
    name_fa = Column(String(100), nullable=True)
    operator_en = Column(String(100), nullable=False)
    operator_fa = Column(String(100), nullable=False)
    description_en = Column(Text, nullable=True)
    description_fa = Column(Text, nullable=True)
    badge_en = Column(String(50), nullable=True)
    badge_fa = Column(String(50), nullable=True)
    image_url = Column(String(255), nullable=True)
    
    # Abilities & Infographic arrays (JSON)
    abilities_en = Column(JSON, nullable=True)
    abilities_fa = Column(JSON, nullable=True)
    infographic_left = Column(JSON, nullable=True)
    infographic_right = Column(JSON, nullable=True)

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class GroundStation(Base):
    __tablename__ = "ground_stations"

    id = Column(String(60), primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True)
    image = Column(String(255), nullable=True)
    color = Column(JSON, nullable=True)
    badge_en = Column(String(60), nullable=True)
    badge_fa = Column(String(60), nullable=True)
    operator_en = Column(String(100), nullable=False)
    operator_fa = Column(String(100), nullable=False)
    year = Column(Integer, nullable=False)
    category = Column(String(50), nullable=False, index=True)
    secondary = Column(String(50), nullable=False, index=True)
    sort_metric = Column(Float, nullable=False)
    steps = Column(Integer, default=4)
    description_en = Column(Text, nullable=True)
    description_fa = Column(Text, nullable=True)
    abilities_en = Column(JSON, nullable=True)
    abilities_fa = Column(JSON, nullable=True)
    center_caption_en = Column(String(150), nullable=True)
    center_caption_fa = Column(String(150), nullable=True)
    infographic_left = Column(JSON, nullable=True)
    infographic_right = Column(JSON, nullable=True)

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

