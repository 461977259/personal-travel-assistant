from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


class WardrobeItem(Base):
    __tablename__ = "wardrobe_items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    category = Column(String(50), nullable=False)  # outerwear, top, bottom, shoes, accessory
    color = Column(String(50), nullable=False)
    thickness = Column(String(20), nullable=False)  # thin, medium, thick, extra_thick
    scene = Column(String(50), nullable=False)  # commute, casual, business, sports, formal, travel
    image_url = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
