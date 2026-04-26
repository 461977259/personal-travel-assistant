from sqlalchemy import Column, Integer, String, DateTime, JSON, ForeignKey
from datetime import datetime
from app.models.base import Base


class Content(Base):
    __tablename__ = "contents"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(100), nullable=False, index=True)
    trip_id = Column(Integer, ForeignKey("trips.id"), nullable=True)
    content_type = Column(String(50), nullable=False)
    title = Column(String(255), nullable=True)
    body = Column(String(5000), nullable=True)
    style = Column(String(50), nullable=True)
    tags = Column(String(255), nullable=True)
    photos = Column(JSON, nullable=True)
    vlog_timestamps = Column(JSON, nullable=True)
    exported_text = Column(String(5000), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
