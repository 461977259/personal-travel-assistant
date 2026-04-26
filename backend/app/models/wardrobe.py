from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from app.models.base import Base


class WardrobeItem(Base):
    __tablename__ = "wardrobe_items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    category = Column(String(50), nullable=False)
    color = Column(String(50), nullable=False)
    thickness = Column(String(20), nullable=False)
    scene = Column(String(50), nullable=False)
    image_url = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
