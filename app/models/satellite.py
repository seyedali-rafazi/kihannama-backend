from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Index
from datetime import datetime, timezone
from ..database import Base

class Satellite(Base):
    __tablename__ = "satellites"

    id = Column(Integer, primary_key=True, autoincrement=True)
    norad_id = Column(String(10), unique=True, index=True, nullable=False)
    name = Column(String(100), index=True, nullable=False)
    intl_desig = Column(String(20), nullable=True)
    epoch = Column(String(30), nullable=True)
    
    # Keplerian elements
    inclination = Column(Float, nullable=False)
    raan = Column(Float, nullable=False)
    eccentricity = Column(Float, nullable=False)
    arg_perigee = Column(Float, nullable=False)
    mean_anomaly = Column(Float, nullable=False)
    mean_motion = Column(Float, nullable=False)
    
    # Derived orbital values
    semi_major_axis = Column(Float, nullable=False)
    altitude = Column(Float, nullable=False)
    perigee_altitude = Column(Float, nullable=True)
    apogee_altitude = Column(Float, nullable=True)
    period = Column(Float, nullable=False)  # Minutes
    
    # Classification
    orbit_class = Column(String(10), index=True, nullable=False)  # LEO, MEO, GEO, HEO
    category = Column(String(50), index=True, nullable=True)      # Starlink, GPS, Weather, etc.
    
    # Raw TLE
    tle_line1 = Column(String(100), nullable=True)
    tle_line2 = Column(String(100), nullable=True)
    
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        Index("idx_sat_orbit_class", "orbit_class"),
        Index("idx_sat_name", "name"),
    )
