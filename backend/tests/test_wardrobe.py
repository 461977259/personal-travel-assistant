from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
import pytest


class TestWardrobeAPI:
    """Tests for /api/wardrobe/* endpoints."""

    def test_create_wardrobe_item(self, test_db):
        """POST /api/wardrobe/items -> 201"""
        from app.main import app
        from app.models.database import get_db
        app.dependency_overrides[get_db] = lambda: test_db
        client = TestClient(app)
        payload = {
            "name": "深蓝色外套",
            "type": "外套",
            "color": "深蓝色",
            "thickness": "厚",
            "scene": "日常",
            "brand": "某品牌",
            "size": "L",
        }
        try:
            response = client.post("/api/wardrobe/items", json=payload)
            assert response.status_code == 201
            data = response.json()
            assert data["name"] == "深蓝色外套"
            assert data["type"] == "外套"
            assert data["color"] == "深蓝色"
            assert data["thickness"] == "厚"
            assert data["brand"] == "某品牌"
            assert data["size"] == "L"
            assert "id" in data
        finally:
            app.dependency_overrides.clear()

    def test_create_wardrobe_item_minimal(self, test_db):
        from app.main import app
        from app.models.database import get_db
        app.dependency_overrides[get_db] = lambda: test_db
        client = TestClient(app)
        payload = {
            "name": "牛仔裤",
            "type": "下装",
            "color": "蓝色",
            "thickness": "中等",
            "scene": "日常",
        }
        try:
            response = client.post("/api/wardrobe/items", json=payload)
            # API returns 201 for successful creation
            assert response.status_code == 201
            data = response.json()
            assert data["name"] == "牛仔裤"
            assert data["brand"] is None
            assert data["size"] is None
        finally:
            app.dependency_overrides.clear()

    def test_list_wardrobe_items(self, test_db):
        from app.main import app
        from app.models.database import get_db
        app.dependency_overrides[get_db] = lambda: test_db
        client = TestClient(app)
        try:
            client.post("/api/wardrobe/items", json={
                "name": "测试外套",
                "type": "上装",
                "color": "黑色",
                "thickness": "厚",
                "scene": "正式",
            })
            response = client.get("/api/wardrobe/items")
            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, list)
            assert any(item["name"] == "测试外套" for item in data)
        finally:
            app.dependency_overrides.clear()

    def test_list_wardrobe_items_filter_by_scene(self, test_db):
        from app.main import app
        from app.models.database import get_db
        app.dependency_overrides[get_db] = lambda: test_db
        client = TestClient(app)
        try:
            client.post("/api/wardrobe/items", json={
                "name": "运动裤",
                "type": "下装",
                "color": "黑色",
                "thickness": "中等",
                "scene": "运动",
            })
            response = client.get("/api/wardrobe/items?scene=运动")
            assert response.status_code == 200
            data = response.json()
            assert all(item["scene"] == "运动" for item in data)
        finally:
            app.dependency_overrides.clear()

    def test_delete_wardrobe_item(self, test_db):
        from app.main import app
        from app.models.database import get_db
        app.dependency_overrides[get_db] = lambda: test_db
        client = TestClient(app)
        try:
            create_resp = client.post("/api/wardrobe/items", json={
                "name": "待删除衣物",
                "type": "上装",
                "color": "红色",
                "thickness": "薄",
                "scene": "日常",
            })
            item_id = create_resp.json()["id"]
            del_resp = client.delete(f"/api/wardrobe/items/{item_id}")
            assert del_resp.status_code == 200
            assert del_resp.json()["id"] == item_id
            list_resp = client.get("/api/wardrobe/items")
            assert all(item["id"] != item_id for item in list_resp.json())
        finally:
            app.dependency_overrides.clear()

    def test_delete_wardrobe_item_not_found(self, test_db):
        from app.main import app
        from app.models.database import get_db
        app.dependency_overrides[get_db] = lambda: test_db
        client = TestClient(app)
        try:
            response = client.delete("/api/wardrobe/items/99999")
            assert response.status_code == 404
        finally:
            app.dependency_overrides.clear()

    def test_suggest_tags(self, test_db):
        from app.main import app
        client = TestClient(app)
        response = client.post("/api/wardrobe/suggest-tags?photo_url=https://example.com/jacket.jpg")
        assert response.status_code == 200
        data = response.json()
        assert "suggested_type" in data
        assert "suggested_tags" in data
        assert data["suggested_type"] == "上装"

    def test_wardrobe_filter_by_type(self, test_db):
        """GET /api/wardrobe/items?type=外套"""
        from app.main import app
        from app.models.database import get_db
        app.dependency_overrides[get_db] = lambda: test_db
        client = TestClient(app)
        try:
            client.post("/api/wardrobe/items", json={
                "name": "卡其色风衣",
                "type": "外套",
                "color": "卡其色",
                "thickness": "中等",
                "scene": "日常",
            })
            client.post("/api/wardrobe/items", json={
                "name": "白色T恤",
                "type": "上装",
                "color": "白色",
                "thickness": "薄",
                "scene": "日常",
            })
            response = client.get("/api/wardrobe/items?type=外套")
            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, list)
            assert all(item["type"] == "外套" for item in data)
            assert any(item["name"] == "卡其色风衣" for item in data)
        finally:
            app.dependency_overrides.clear()

    def test_wardrobe_filter_by_color(self, test_db):
        """GET /api/wardrobe/items?color=深蓝"""
        from app.main import app
        from app.models.database import get_db
        app.dependency_overrides[get_db] = lambda: test_db
        client = TestClient(app)
        try:
            # Create a deep blue item with a unique name to avoid any cross-test confusion
            unique_name = f"深蓝专用测试外套_{id(test_db)}"
            client.post("/api/wardrobe/items", json={
                "name": unique_name,
                "type": "外套",
                "color": "深蓝色",
                "thickness": "中等",
                "scene": "商务",
            })
            # Verify the color filter works: only deep blue items should be returned
            response = client.get("/api/wardrobe/items?color=深蓝色")
            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, list)
            # The specific item we created must be present
            assert any(item["name"] == unique_name for item in data), \
                f"Expected {unique_name} in results, got {[i['name'] for i in data]}"
            # All returned items must have the correct color
            assert all(item["color"] == "深蓝色" for item in data), \
                f"All items should have color 深蓝色, got {[i['color'] for i in data]}"
        finally:
            app.dependency_overrides.clear()


class TestOutfitAPI:
    """Tests for /api/outfit/* endpoints."""

    def _mock_weather_hot(self, city):
        return {
            "temperature": 30.0,
            "wind_speed": 10.0,
            "humidity": 60.0,
            "condition": "晴",
            "city": city,
        }

    def _mock_weather_cold(self, city):
        return {
            "temperature": 2.0,
            "wind_speed": 15.0,
            "humidity": 50.0,
            "condition": "阴",
            "city": city,
        }

    def test_outfit_recommend_hot_weather(self, test_db):
        """Temperature >25°C, verify layered output."""
        from app.main import app
        from app.models.database import get_db
        from app.api import outfit as outfit_module
        app.dependency_overrides[get_db] = lambda: test_db
        client = TestClient(app)
        try:
            client.post("/api/wardrobe/items", json={
                "name": "白色T恤",
                "type": "上装",
                "color": "白色",
                "thickness": "薄",
                "scene": "日常",
            })
            client.post("/api/wardrobe/items", json={
                "name": "黑色短裤",
                "type": "裤装",
                "color": "黑色",
                "thickness": "薄",
                "scene": "休闲",
            })
            client.post("/api/wardrobe/items", json={
                "name": "凉鞋",
                "type": "鞋",
                "color": "棕色",
                "thickness": "薄",
                "scene": "休闲",
            })
            with patch.object(outfit_module, "get_weather", new_callable=AsyncMock) as mock_wx:
                mock_wx.return_value = self._mock_weather_hot("广州")
                response = client.get(
                    "/api/outfit/recommend?city=广州&scene=休闲&date=2026-07-01"
                )
            assert response.status_code == 200
            data = response.json()
            assert "outfit" in data
            assert "reason" in data
            assert "tips" in data
            outfit_items = data["outfit"]
            assert isinstance(outfit_items, list)
            layers = [oi.get("layer", 0) for oi in outfit_items]
            # Hot weather: max 2 layers
            assert max(layers) <= 2
        finally:
            app.dependency_overrides.clear()

    def test_outfit_recommend_cold_weather(self, test_db):
        """Temperature <5°C, verify 3-layer warmth."""
        from app.main import app
        from app.models.database import get_db
        from app.api import outfit as outfit_module
        app.dependency_overrides[get_db] = lambda: test_db
        client = TestClient(app)
        try:
            client.post("/api/wardrobe/items", json={
                "name": "保暖内衣",
                "type": "上装",
                "color": "灰色",
                "thickness": "厚",
                "scene": "日常",
            })
            client.post("/api/wardrobe/items", json={
                "name": "羊毛衫",
                "type": "上装",
                "color": "深蓝色",
                "thickness": "厚",
                "scene": "日常",
            })
            client.post("/api/wardrobe/items", json={
                "name": "羽绒服",
                "type": "外套",
                "color": "黑色",
                "thickness": "厚",
                "scene": "日常",
            })
            client.post("/api/wardrobe/items", json={
                "name": "加绒裤",
                "type": "裤装",
                "color": "黑色",
                "thickness": "厚",
                "scene": "日常",
            })
            with patch.object(outfit_module, "get_weather", new_callable=AsyncMock) as mock_wx:
                mock_wx.return_value = self._mock_weather_cold("哈尔滨")
                response = client.get(
                    "/api/outfit/recommend?city=哈尔滨&scene=通勤&date=2026-01-15"
                )
            assert response.status_code == 200
            data = response.json()
            assert "outfit" in data
            assert "reason" in data
            assert "tips" in data
            outfit_items = data["outfit"]
            assert isinstance(outfit_items, list)
            # Cold weather (<5°C): max layer value should reach 3
            layers = [oi.get("layer", 0) for oi in outfit_items]
            assert max(layers) == 3, f"Cold weather should reach layer 3, got {layers}"
        finally:
            app.dependency_overrides.clear()

    def test_outfit_recommend_scene_commute(self, test_db):
        """Commute scene, verify formal/proper appearance."""
        from app.main import app
        from app.models.database import get_db
        from app.api import outfit as outfit_module
        app.dependency_overrides[get_db] = lambda: test_db
        client = TestClient(app)
        try:
            client.post("/api/wardrobe/items", json={
                "name": "白色衬衫",
                "type": "上装",
                "color": "白色",
                "thickness": "薄",
                "scene": "商务",
            })
            client.post("/api/wardrobe/items", json={
                "name": "深蓝西装外套",
                "type": "外套",
                "color": "深蓝色",
                "thickness": "中等",
                "scene": "商务",
            })
            client.post("/api/wardrobe/items", json={
                "name": "黑色西裤",
                "type": "裤装",
                "color": "黑色",
                "thickness": "中等",
                "scene": "商务",
            })
            with patch.object(outfit_module, "get_weather", new_callable=AsyncMock) as mock_wx:
                mock_wx.return_value = {
                    "temperature": 20.0,
                    "wind_speed": 10.0,
                    "humidity": 55.0,
                    "condition": "晴",
                    "city": "北京",
                }
                response = client.get(
                    "/api/outfit/recommend?city=北京&scene=通勤&date=2026-05-01"
                )
            assert response.status_code == 200
            data = response.json()
            assert "outfit" in data
            assert "reason" in data
            # Commute scene should include formal/proper mention
            assert "通勤" in data["reason"] or "得体" in data["reason"] or "商务" in data["reason"]
        finally:
            app.dependency_overrides.clear()

    def test_outfit_recommend_body_type(self, test_db):
        """Apple body type, verify outfit suggestions are appropriate."""
        from app.main import app
        from app.models.database import get_db
        from app.api import outfit as outfit_module
        app.dependency_overrides[get_db] = lambda: test_db
        client = TestClient(app)
        try:
            client.post("/api/wardrobe/items", json={
                "name": "白色T恤",
                "type": "上装",
                "color": "白色",
                "thickness": "薄",
                "scene": "日常",
            })
            client.post("/api/wardrobe/items", json={
                "name": "A字裙",
                "type": "裤装",
                "color": "深蓝色",
                "thickness": "薄",
                "scene": "休闲",
            })
            client.post("/api/wardrobe/items", json={
                "name": "运动鞋",
                "type": "鞋",
                "color": "白色",
                "thickness": "中等",
                "scene": "休闲",
            })
            with patch.object(outfit_module, "get_weather", new_callable=AsyncMock) as mock_wx:
                mock_wx.return_value = {
                    "temperature": 22.0,
                    "wind_speed": 10.0,
                    "humidity": 55.0,
                    "condition": "晴",
                    "city": "北京",
                }
                response = client.get(
                    "/api/outfit/recommend?city=北京&scene=休闲&body_type=苹果型&date=2026-05-01"
                )
            assert response.status_code == 200
            data = response.json()
            assert "outfit" in data
            assert "reason" in data
            # Body type should be mentioned in reason
            assert "苹果型" in data["reason"]
            outfit = data["outfit"]
            assert isinstance(outfit, list)
            assert len(outfit) > 0
        finally:
            app.dependency_overrides.clear()

    def test_outfit_color_coordination(self, test_db):
        """Verify color coordination rules are applied."""
        from app.main import app
        from app.models.database import get_db
        from app.api import outfit as outfit_module
        from app.services.outfit_engine import _colors_compatible
        # First verify the color compatibility function works
        assert _colors_compatible("黑色", "白色") is True
        assert _colors_compatible("黑色", "灰色") is True
        assert _colors_compatible("红色", "黄色") is False
        app.dependency_overrides[get_db] = lambda: test_db
        client = TestClient(app)
        try:
            client.post("/api/wardrobe/items", json={
                "name": "白色衬衫",
                "type": "上装",
                "color": "白色",
                "thickness": "薄",
                "scene": "商务",
            })
            client.post("/api/wardrobe/items", json={
                "name": "藏青色西裤",
                "type": "裤装",
                "color": "藏青色",
                "thickness": "中等",
                "scene": "商务",
            })
            client.post("/api/wardrobe/items", json={
                "name": "深蓝西装外套",
                "type": "外套",
                "color": "深蓝色",
                "thickness": "中等",
                "scene": "商务",
            })
            with patch.object(outfit_module, "get_weather", new_callable=AsyncMock) as mock_wx:
                mock_wx.return_value = {
                    "temperature": 22.0,
                    "wind_speed": 10.0,
                    "humidity": 55.0,
                    "condition": "晴",
                    "city": "北京",
                }
                response = client.get(
                    "/api/outfit/recommend?city=北京&scene=商务&date=2026-05-01"
                )
            assert response.status_code == 200
            data = response.json()
            outfit = data["outfit"]
            # All selected items should have compatible colors
            colors = [oi.get("color", "") for oi in outfit]
            for c1 in colors:
                for c2 in colors:
                    if c1 and c2:
                        assert _colors_compatible(c1, c2) is True, f"Color {c1} and {c2} should be compatible"
        finally:
            app.dependency_overrides.clear()
