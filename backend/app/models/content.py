from sqlalchemy import Column, Integer, String, DateTime, Text, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


class Content(Base):
    __tablename__ = "contents"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(100), nullable=False, index=True)
    trip_id = Column(Integer, ForeignKey("trips.id"), nullable=True)
    content_type = Column(String(50), nullable=False)  # vlog_script, social_post, photo_diary
    title = Column(String(255), nullable=True)
    body = Column(Text, nullable=True)
    style = Column(String(50), nullable=True)  # literary, lively, minimalist, guide
    tags = Column(String(255), nullable=True)
    photos = Column(JSON, nullable=True)  # list of photo references
    vlog_timestamps = Column(JSON, nullable=True)  # {scenes: [], scripts: []}
    exported_text = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
