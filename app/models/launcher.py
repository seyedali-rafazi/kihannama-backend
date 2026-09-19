from sqlalchemy import Column, Integer, String, Float, DateTime, Text, JSON, Index
from datetime import datetime, timezone
from ..database import Base

class Launcher(Base):
    __tablename__ = "launchers"

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

    __table_args__ = (
        Index("idx_launcher_category", "category"),
        Index("idx_launcher_secondary", "secondary"),
    )
