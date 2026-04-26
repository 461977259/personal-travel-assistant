import os
from app.integrations.tencent_ci import (
    _mock_classify,
    _mock_processed_url,
)


class TestTencentCIMock:
    """Tests for mock data functions."""

    def test_mock_classify_portrait(self):
        tags = _mock_classify("https://example.com/portrait.jpg")
        assert "人物" in tags
        assert "人像" in tags

    def test_mock_classify_nature(self):
        tags = _mock_classify("https://example.com/landscape.jpg")
        assert "自然" in tags
        assert "风景" in tags

    def test_mock_classify_food(self):
        tags = _mock_classify("https://example.com/food_dish.jpg")
        assert "美食" in tags

    def test_mock_classify_building(self):
        tags = _mock_classify("https://example.com/building.jpg")
        assert "建筑" in tags

    def test_mock_classify_unknown(self):
        tags = _mock_classify("https://example.com/random.jpg")
        assert "未知类别" in tags or "综合" in tags

    def test_mock_processed_url(self):
        url = _mock_processed_url("https://example.com/image.jpg", "enhance")
        assert "processed=enhance" in url


class TestTencentCIAPI:
    """Integration tests for /api/tencent-ci/* endpoints."""

    def test_classify_endpoint(self):
        os.environ["TENCENT_CI_MOCK_MODE"] = "true"
        from fastapi.testclient import TestClient
        from app.main import app
        client = TestClient(app)
        response = client.post(
            "/api/tencent-ci/classify",
            json={"image_url": "https://example.com/portrait.jpg"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert isinstance(data["data"]["tags"], list)
        assert len(data["data"]["tags"]) > 0

    def test_enhance_endpoint(self):
        os.environ["TENCENT_CI_MOCK_MODE"] = "true"
        from fastapi.testclient import TestClient
        from app.main import app
        client = TestClient(app)
        response = client.post(
            "/api/tencent-ci/enhance",
            json={
                "image_url": "https://example.com/photo.jpg",
                "options": {"denoise": 3, "sharpen": 2},
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert "output_url" in data["data"]

    def test_portrait_matting_endpoint(self):
        os.environ["TENCENT_CI_MOCK_MODE"] = "true"
        from fastapi.testclient import TestClient
        from app.main import app
        client = TestClient(app)
        response = client.post(
            "/api/tencent-ci/portrait-matting",
            json={"image_url": "https://example.com/person.png"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert "output_url" in data["data"]

    def test_super_resolution_endpoint(self):
        os.environ["TENCENT_CI_MOCK_MODE"] = "true"
        from fastapi.testclient import TestClient
        from app.main import app
        client = TestClient(app)
        response = client.post(
            "/api/tencent-ci/super-resolution",
            json={"image_url": "https://example.com/small.jpg", "scale": 4}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert "output_url" in data["data"]

    def test_smart_crop_endpoint(self):
        os.environ["TENCENT_CI_MOCK_MODE"] = "true"
        from fastapi.testclient import TestClient
        from app.main import app
        client = TestClient(app)
        response = client.post(
            "/api/tencent-ci/smart-crop",
            json={"image_url": "https://example.com/wide.jpg", "ratio": "16:9"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert "output_url" in data["data"]
