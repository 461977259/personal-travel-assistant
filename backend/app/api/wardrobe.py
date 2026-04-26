"""
Wardrobe API endpoint.
POST /api/wardrobe/items   - Upload a clothing item
GET  /api/wardrobe/items   - List all items
DELETE /api/wardrobe/items/{item_id} - Delete an item
"""
import os
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session

from app.models.database import get_db
from app.models.wardrobe import WardrobeItem

router = APIRouter()


# ---------------------------------------------------------------------------
# Pydantic Schemas
# ---------------------------------------------------------------------------

class WardrobeItemCreate(BaseModel):
    name: str
    type: str  # 上装/下装/鞋/配饰
    color: str
    thickness: str  # 薄/中等/厚
    scene: str  # 日常/正式/运动/休闲
    photo_url: Optional[str] = None
    brand: Optional[str] = None
    size: Optional[str] = None


class WardrobeItemResponse(BaseModel):
    id: int
    name: str
    type: str
    color: str
    thickness: str
    scene: str
    photo_url: Optional[str]
    brand: Optional[str]
    size: Optional[str]
    created_at: str

    model_config = ConfigDict(from_attributes=True)


class TagSuggestion(BaseModel):
    suggested_type: Optional[str] = None
    suggested_color: Optional[str] = None
    suggested_thickness: Optional[str] = None
    suggested_scene: Optional[str] = None
    suggested_tags: list[str] = []


# ---------------------------------------------------------------------------
# LLM Tagging (mock)
# ---------------------------------------------------------------------------

async def _mock_llm_tag(image_url: str) -> TagSuggestion:
    """
    Mock LLM tagger. In production, call OpenAI/MiniMax/etc with vision model.
    Returns realistic suggested tags based on image URL pattern.
    """
    # Check environment for real LLM mode
    if os.getenv("LLM_TAG_MODE", "mock") == "real":
        # TODO: integrate with MiniMax/OpenAI vision API
        pass

    # Mock: return sensible suggestions based on URL keywords
    url_lower = image_url.lower() if image_url else ""
    if "jacket" in url_lower or "coat" in url_lower:
        return TagSuggestion(
            suggested_type="上装",
            suggested_color="未知",
            suggested_thickness="厚",
            suggested_scene="日常",
            suggested_tags=["外套", "冬季"],
        )
    elif "shirt" in url_lower or "top" in url_lower:
        return TagSuggestion(
            suggested_type="上装",
            suggested_color="未知",
            suggested_thickness="薄",
            suggested_scene="日常",
            suggested_tags=["T恤", "夏季"],
        )
    elif "pants" in url_lower or "jean" in url_lower:
        return TagSuggestion(
            suggested_type="下装",
            suggested_color="未知",
            suggested_thickness="中等",
            suggested_scene="日常",
            suggested_tags=["裤子"],
        )
    elif "shoe" in url_lower or "sneaker" in url_lower:
        return TagSuggestion(
            suggested_type="鞋",
            suggested_color="未知",
            suggested_thickness="中等",
            suggested_scene="日常",
            suggested_tags=["鞋子", "休闲"],
        )
    else:
        return TagSuggestion(
            suggested_type="未知",
            suggested_color="未知",
            suggested_thickness="中等",
            suggested_scene="日常",
            suggested_tags=["待分类"],
        )


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@router.post("/wardrobe/items", response_model=WardrobeItemResponse)
def create_wardrobe_item(item: WardrobeItemCreate, db: Session = Depends(get_db)):
    """Upload a new clothing item to the wardrobe."""
    db_item = WardrobeItem(
        name=item.name,
        type=item.type,
        color=item.color,
        thickness=item.thickness,
        scene=item.scene,
        photo_url=item.photo_url,
        brand=item.brand,
        size=item.size,
    )
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return WardrobeItemResponse(
        id=db_item.id,
        name=db_item.name,
        type=db_item.type,
        color=db_item.color,
        thickness=db_item.thickness,
        scene=db_item.scene,
        photo_url=db_item.photo_url,
        brand=db_item.brand,
        size=db_item.size,
        created_at=db_item.created_at.isoformat(),
    )


@router.get("/wardrobe/items", response_model=list[WardrobeItemResponse])
def list_wardrobe_items(
    scene: Optional[str] = Query(None, description="Filter by scene"),
    type: Optional[str] = Query(None, description="Filter by type"),
    db: Session = Depends(get_db),
):
    """List all wardrobe items, optionally filtered by scene or type."""
    query = db.query(WardrobeItem)
    if scene:
        query = query.filter(WardrobeItem.scene == scene)
    if type:
        query = query.filter(WardrobeItem.type == type)
    items = query.order_by(WardrobeItem.created_at.desc()).all()
    return [
        WardrobeItemResponse(
            id=item.id,
            name=item.name,
            type=item.type,
            color=item.color,
            thickness=item.thickness,
            scene=item.scene,
            photo_url=item.photo_url,
            brand=item.brand,
            size=item.size,
            created_at=item.created_at.isoformat(),
        )
        for item in items
    ]


@router.delete("/wardrobe/items/{item_id}")
def delete_wardrobe_item(item_id: int, db: Session = Depends(get_db)):
    """Delete a wardrobe item by ID."""
    item = db.query(WardrobeItem).filter(WardrobeItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    db.delete(item)
    db.commit()
    return {"message": "Item deleted", "id": item_id}


@router.post("/wardrobe/suggest-tags", response_model=TagSuggestion)
async def suggest_tags(photo_url: str = Query(..., description="Image URL")):
    """
    Semi-automatic tagging: call LLM to suggest tags for an image.
    User confirms or edits the suggested tags before saving.
    """
    suggestion = await _mock_llm_tag(photo_url)
    return suggestion
