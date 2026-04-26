"""
OutfitLog model - stores confirmed daily outfit records.
"""
from sqlalchemy import Column, Integer, String, Date, JSON, Boolean, DateTime
from datetime import datetime
from app.models.base import Base


class OutfitLog(Base):
    __tablename__ = "outfit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(100), nullable=False, index=True)
    date = Column(Date, nullable=False, index=True)
    scene = Column(String(50), nullable=False)
    weather_summary = Column(String(255), nullable=True)
    outfit_items = Column(JSON, nullable=False)  # [{"item_id": 1, "name": "...", "type": "外套", "layer": 2}, ...]
    confirmed = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
