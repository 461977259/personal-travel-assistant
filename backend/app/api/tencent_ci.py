"""
腾讯云数据万象 CI API endpoint.
POST /api/tencent-ci/classify          - 图片标签分类
POST /api/tencent-ci/enhance          - 图像增强
POST /api/tencent-ci/portrait-matting - 人像抠图
POST /api/tencent-ci/super-resolution - 超分辨率
POST /api/tencent-ci/smart-crop       - 智能裁剪
"""
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from app.integrations.tencent_ci import (
    classify_image,
    enhance_image,
    portrait_matting,
    super_resolution,
    smart_crop,
)

router = APIRouter()


class ClassifyRequest(BaseModel):
    image_url: str


class EnhanceRequest(BaseModel):
    image_url: str
    options: Optional[dict] = None


class MattingRequest(BaseModel):
    image_url: str


class SuperResolutionRequest(BaseModel):
    image_url: str
    scale: int = 2


class SmartCropRequest(BaseModel):
    image_url: str
    ratio: str = "1:1"


@router.post("/tencent-ci/classify")
async def ci_classify(req: ClassifyRequest):
    """
    Classify an image and return tag labels.
    E.g., ["户外", "自然", "建筑"]
    """
    tags = await classify_image(req.image_url)
    return {"code": 0, "data": {"tags": tags}, "message": "success"}


@router.post("/tencent-ci/enhance")
async def ci_enhance(req: EnhanceRequest):
    """
    Enhance an image (denoise, sharpen, color correct).
    Returns the URL of the processed image.
    """
    output_url = await enhance_image(req.image_url, req.options)
    return {"code": 0, "data": {"output_url": output_url}, "message": "success"}


@router.post("/tencent-ci/portrait-matting")
async def ci_portrait_matting(req: MattingRequest):
    """
    Remove background from a portrait image.
    Returns the URL of the transparent PNG.
    """
    output_url = await portrait_matting(req.image_url)
    return {"code": 0, "data": {"output_url": output_url}, "message": "success"}


@router.post("/tencent-ci/super-resolution")
async def ci_super_resolution(req: SuperResolutionRequest):
    """
    Upscale an image (2x or 4x).
    Returns the URL of the upscaled image.
    """
    output_url = await super_resolution(req.image_url, req.scale)
    return {"code": 0, "data": {"output_url": output_url}, "message": "success"}


@router.post("/tencent-ci/smart-crop")
async def ci_smart_crop(req: SmartCropRequest):
    """
    Smart crop an image to the specified aspect ratio.
    ratio: "1:1", "4:3", "16:9", "9:16"
    Returns the URL of the cropped image.
    """
    output_url = await smart_crop(req.image_url, req.ratio)
    return {"code": 0, "data": {"output_url": output_url}, "message": "success"}
