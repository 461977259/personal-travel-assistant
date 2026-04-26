from fastapi.testclient import TestClient


class TestWardrobeAPI:
    """Tests for /api/wardrobe/* endpoints."""

    def test_create_wardrobe_item(self, test_db):
        from app.main import app
        from app.models.database import get_db
        app.dependency_overrides[get_db] = lambda: test_db
        client = TestClient(app)
        payload = {
            "name": "白色T恤",
            "type": "上装",
            "color": "白色",
            "thickness": "薄",
            "scene": "日常",
            "brand": "优衣库",
            "size": "M",
        }
        try:
            response = client.post("/api/wardrobe/items", json=payload)
            assert response.status_code == 200
            data = response.json()
            assert data["name"] == "白色T恤"
            assert data["type"] == "上装"
            assert data["brand"] == "优衣库"
            assert data["size"] == "M"
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
            assert response.status_code == 200
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
            # Create an item first
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
