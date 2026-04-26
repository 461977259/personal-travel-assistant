from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from app.models.base import Base


class WardrobeItem(Base):
    __tablename__ = "wardrobe_items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    type = Column(String(50), nullable=False)  # 上装/下装/鞋/配饰等
    color = Column(String(50), nullable=False)
    thickness = Column(String(20), nullable=False)  # 薄/中等/厚
    scene = Column(String(50), nullable=False)  # 日常/正式/运动/休闲等
    photo_url = Column(String(500), nullable=True)
    brand = Column(String(100), nullable=True)  # 品牌
    size = Column(String(20), nullable=True)   # 尺码
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
