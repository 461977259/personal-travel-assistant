"""
腾讯云数据万象 CI (Cloud Infinite) 集成。
API Docs: https://cloud.tencent.com/document/product/1590
当前阶段：MVP 使用 mock 数据，真实 API Key 注册后切换。
"""
import os
import httpx
from typing import Optional

TENCENT_CI_BASE_URL = "https://image.myqcloud.com"


def _is_mock_mode() -> bool:
    """Check if mock mode is enabled."""
    return os.getenv("TENCENT_CI_MOCK_MODE", "true").lower() == "true"


def _get_tencent_credentials() -> tuple[str, str]:
    """Get Tencent CI credentials from environment variables."""
    secret_id = os.getenv("TENCENT_CI_SECRET_ID", "")
    secret_key = os.getenv("TENCENT_CI_SECRET_KEY", "")
    if not secret_id or not secret_key:
        raise ValueError(
            "TENCENT_CI_SECRET_ID and TENCENT_CI_SECRET_KEY "
            "environment variables must be set"
        )
    return secret_id, secret_key


async def _call_tencent_ci(
    path: str,
    params: dict,
    data: Optional[dict] = None,
) -> dict:
    """
    Make an authenticated call to Tencent CI API.
    Note: Real implementation requires COS authentication.
    """
    secret_id, secret_key = _get_tencent_credentials()
    headers = {
        "Authorization": f"Bearer {secret_id}:{secret_key}",
    }
    async with httpx.AsyncClient(timeout=60.0) as client:
        if data:
            response = await client.post(
                f"{TENCENT_CI_BASE_URL}{path}",
                json=data,
                params=params,
                headers=headers,
            )
        else:
            response = await client.get(
                f"{TENCENT_CI_BASE_URL}{path}",
                params=params,
                headers=headers,
            )
        response.raise_for_status()
        return response.json()


async def classify_image(image_url: str) -> list[str]:
    """
    Classify an image and return a list of tags/categories.
    E.g., ["户外", "自然", "白天", "建筑"]
    """
    if _is_mock_mode():
        return _mock_classify(image_url)

    result = await _call_tencent_ci(
        "/image/classify",
        params={"url": image_url},
    )
    return result.get("tags", [])


async def enhance_image(image_url: str, options: Optional[dict] = None) -> str:
    """
    Enhance an image (denoise, sharpen, color correct, etc.).
    Returns the URL of the processed image.
    options: {"denoise": 3, "sharpen": 2, "contrast": 1}
    """
    if _is_mock_mode():
        return _mock_processed_url(image_url, "enhance")

    data = {"url": image_url, "options": options or {}}
    result = await _call_tencent_ci("/image/enhance", params={}, data=data)
    return result.get("output_url", "")


async def portrait_matting(image_url: str) -> str:
    """
    Remove the background from a portrait image (human segmentation).
    Returns the URL of the transparent PNG.
    """
    if _is_mock_mode():
        return _mock_processed_url(image_url, "matting")

    data = {"url": image_url, "mode": "portrait"}
    result = await _call_tencent_ci("/image/matting", params={}, data=data)
    return result.get("output_url", "")


async def super_resolution(image_url: str, scale: int = 2) -> str:
    """
    Super-resolution upscaling of an image.
    scale: 2 or 4 (2x or 4x upscaling)
    Returns the URL of the upscaled image.
    """
    if _is_mock_mode():
        return _mock_processed_url(image_url, f"sr{scale}x")

    if scale not in (2, 4):
        raise ValueError("scale must be 2 or 4")
    data = {"url": image_url, "scale": scale}
    result = await _call_tencent_ci("/image/super_resolution", params={}, data=data)
    return result.get("output_url", "")


async def smart_crop(image_url: str, ratio: str = "1:1") -> str:
    """
    Smart crop an image to the specified aspect ratio.
    ratio: "1:1", "4:3", "16:9", "9:16", etc.
    Returns the URL of the cropped image.
    """
    if _is_mock_mode():
        return _mock_processed_url(image_url, f"crop_{ratio}")

    data = {"url": image_url, "ratio": ratio}
    result = await _call_tencent_ci("/image/smart_crop", params={}, data=data)
    return result.get("output_url", "")


# ---------------------------------------------------------------------------
# Mock helpers
# ---------------------------------------------------------------------------

def _mock_processed_url(original_url: str, operation: str) -> str:
    """
    Generate a realistic mock processed image URL.
    Uses the original URL with a processed indicator.
    """
    if "?" in original_url:
        return f"{original_url}&processed={operation}"
    return f"{original_url}?processed={operation}"


def _mock_classify(image_url: str) -> list[str]:
    """
    Return realistic image classification tags based on URL patterns.
    """
    url_lower = image_url.lower()
    if "portrait" in url_lower or "selfie" in url_lower or "avatar" in url_lower:
        return ["人物", "人像", "室内", "正面"]
    elif "landscape" in url_lower or "nature" in url_lower:
        return ["自然", "户外", "风景", "白天"]
    elif "food" in url_lower or "dish" in url_lower or "meal" in url_lower:
        return ["美食", "食物", "室内", "餐饮"]
    elif "building" in url_lower or "city" in url_lower or "street" in url_lower:
        return ["建筑", "城市", "户外", "白天"]
    elif "clothes" in url_lower or "dress" in url_lower or "shoe" in url_lower:
        return ["服饰", "物品", "室内", "商品"]
    else:
        return ["物品", "综合", "未知类别"]
