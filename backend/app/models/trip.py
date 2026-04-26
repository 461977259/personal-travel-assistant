from sqlalchemy import Column, Integer, String, DateTime, Float, JSON
from datetime import datetime
from app.models.base import Base


class Trip(Base):
    __tablename__ = "trips"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(100), nullable=False, index=True)
    destination = Column(String(255), nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    days = Column(Integer, nullable=False)
    itinerary = Column(JSON, nullable=True)
    weather_summary = Column(JSON, nullable=True)
    transportation = Column(JSON, nullable=True)
    daily_outfits = Column(JSON, nullable=True)
    total_cost = Column(Float, nullable=True)
    notes = Column(String(2000), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
