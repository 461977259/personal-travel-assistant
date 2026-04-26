from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


class UserPreference(Base):
    __tablename__ = "user_preferences"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(100), unique=True, nullable=False, index=True)
    body_type = Column(String(50), nullable=True)  # pear, apple, hourglass, inverted_triangle, rectangle, other
    style_preference = Column(String(100), nullable=True)
    color_preference = Column(String(255), nullable=True)
    clothing_size = Column(String(20), nullable=True)
    common_scenes = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
