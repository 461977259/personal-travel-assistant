"""
Tests for /api/copywriting/* endpoints.
"""

from fastapi.testclient import TestClient


class TestCopywritingAPI:
    """Tests for the copywriting generation API."""

    def test_generate_copywriting_friend_circle(self, test_db):
        """Test generating friend circle copywriting."""
        from app.main import app
        from app.models.database import get_db

        app.dependency_overrides[get_db] = lambda: test_db
        client = TestClient(app)

        try:
            payload = {
                "photos": [
                    {"scene": "故宫", "location": "北京", "time": "09:30"},
                    {"scene": "长城", "location": "北京", "time": "14:00"},
                ],
                "trip": {"destination": "北京", "days": 3},
                "style": "文艺",
                "platform": "朋友圈",
            }
            response = client.post("/api/copywriting/generate", json=payload)
            assert response.status_code == 200
            data = response.json()
            assert data["platform"] == "朋友圈"
            assert data["style"] == "文艺"
            assert "title" in data
            assert "content" in data
            assert "hashtags" in data
            assert isinstance(data["hashtags"], list)
            assert "photo_suggestions" in data
            assert len(data["photo_suggestions"]) == 2
        finally:
            app.dependency_overrides.clear()

    def test_generate_copywriting_xiaohongshu(self, test_db):
        """Test generating Xiaohongshu copywriting."""
        from app.main import app
        from app.models.database import get_db

        app.dependency_overrides[get_db] = lambda: test_db
        client = TestClient(app)

        try:
            payload = {
                "photos": [{"scene": "西湖", "location": "杭州", "time": "08:00"}],
                "style": "活泼",
                "platform": "小红书",
            }
            response = client.post("/api/copywriting/generate", json=payload)
            assert response.status_code == 200
            data = response.json()
            assert data["platform"] == "小红书"
            assert data["style"] == "活泼"
            assert "故宫" in data["title"] or "西湖" in data["title"] or "远方" in data["title"]
        finally:
            app.dependency_overrides.clear()

    def test_generate_copywriting_invalid_style(self, test_db):
        """Test that invalid style returns 400."""
        from app.main import app
        from app.models.database import get_db

        app.dependency_overrides[get_db] = lambda: test_db
        client = TestClient(app)

        try:
            payload = {
                "photos": [],
                "style": "不存在风格",
                "platform": "朋友圈",
            }
            response = client.post("/api/copywriting/generate", json=payload)
            assert response.status_code == 400
        finally:
            app.dependency_overrides.clear()

    def test_generate_copywriting_invalid_platform(self, test_db):
        """Test that invalid platform returns 400."""
        from app.main import app
        from app.models.database import get_db

        app.dependency_overrides[get_db] = lambda: test_db
        client = TestClient(app)

        try:
            payload = {
                "photos": [],
                "style": "文艺",
                "platform": "不存在的平台",
            }
            response = client.post("/api/copywriting/generate", json=payload)
            assert response.status_code == 400
        finally:
            app.dependency_overrides.clear()

    def test_generate_copywriting_all_styles(self, test_db):
        """Test generating copywriting with all available styles."""
        from app.main import app
        from app.models.database import get_db

        app.dependency_overrides[get_db] = lambda: test_db
        client = TestClient(app)

        try:
            for style in ["文艺", "活泼", "简约", "攻略型", "日记型"]:
                payload = {
                    "photos": [{"scene": "测试景点", "location": "测试城市"}],
                    "style": style,
                    "platform": "朋友圈",
                }
                response = client.post("/api/copywriting/generate", json=payload)
                assert response.status_code == 200, f"Style {style} failed"
                data = response.json()
                assert data["style"] == style
        finally:
            app.dependency_overrides.clear()

    def test_generate_copywriting_all_platforms(self, test_db):
        """Test generating copywriting for all supported platforms."""
        from app.main import app
        from app.models.database import get_db

        app.dependency_overrides[get_db] = lambda: test_db
        client = TestClient(app)

        try:
            for platform in ["朋友圈", "小红书", "抖音", "微博"]:
                payload = {
                    "photos": [{"scene": "测试景点"}],
                    "style": "文艺",
                    "platform": platform,
                }
                response = client.post("/api/copywriting/generate", json=payload)
                assert response.status_code == 200, f"Platform {platform} failed"
                data = response.json()
                assert data["platform"] == platform
        finally:
            app.dependency_overrides.clear()

    def test_generate_copywriting_minimal(self, test_db):
        """Test generating copywriting with minimal data."""
        from app.main import app
        from app.models.database import get_db

        app.dependency_overrides[get_db] = lambda: test_db
        client = TestClient(app)

        try:
            payload = {
                "photos": [],
            }
            response = client.post("/api/copywriting/generate", json=payload)
            assert response.status_code == 200
            data = response.json()
            assert "title" in data
            assert "content" in data
        finally:
            app.dependency_overrides.clear()


class TestVlogScriptAPI:
    """Tests for the Vlog script generation API."""

    def test_generate_vlog_script(self, test_db):
        """Test generating a Vlog script."""
        from app.main import app
        from app.models.database import get_db

        app.dependency_overrides[get_db] = lambda: test_db
        client = TestClient(app)

        try:
            payload = {
                "trip": {
                    "destination": "北京",
                    "days": 3,
                    "itinerary": {
                        "days": [
                            {
                                "name": "故宫",
                                "highlights": ["航拍全景", "红墙特写"],
                            },
                            {
                                "name": "长城",
                                "highlights": ["航拍", "好汉坡"],
                            },
                        ]
                    },
                },
                "style": "文艺",
            }
            response = client.post("/api/copywriting/vlog", json=payload)
            assert response.status_code == 200
            data = response.json()
            assert "title" in data
            assert "total_duration" in data
            assert "scenes" in data
            assert isinstance(data["scenes"], list)
            assert len(data["scenes"]) > 0

            # Check scene structure
            scene = data["scenes"][0]
            assert "scene" in scene
            assert "location" in scene
            assert "duration" in scene
            assert "shots" in scene
            assert "narration" in scene
            assert "music" in scene
        finally:
            app.dependency_overrides.clear()

    def test_generate_vlog_script_minimal(self, test_db):
        """Test generating Vlog script with minimal trip data."""
        from app.main import app
        from app.models.database import get_db

        app.dependency_overrides[get_db] = lambda: test_db
        client = TestClient(app)

        try:
            payload = {
                "trip": {"destination": "成都", "days": 2},
                "style": "活泼",
            }
            response = client.post("/api/copywriting/vlog", json=payload)
            assert response.status_code == 200
            data = response.json()
            assert "title" in data
            assert "成都" in data["title"]
        finally:
            app.dependency_overrides.clear()

    def test_generate_vlog_script_invalid_style(self, test_db):
        """Test that invalid style returns 400."""
        from app.main import app
        from app.models.database import get_db

        app.dependency_overrides[get_db] = lambda: test_db
        client = TestClient(app)

        try:
            payload = {
                "trip": {"destination": "北京", "days": 3},
                "style": "不存在的风格",
            }
            response = client.post("/api/copywriting/vlog", json=payload)
            assert response.status_code == 400
        finally:
            app.dependency_overrides.clear()


class TestStylesAPI:
    """Tests for the /api/copywriting/styles endpoint."""

    def test_list_styles(self, test_db):
        """Test listing all available styles."""
        from app.main import app
        from app.models.database import get_db

        app.dependency_overrides[get_db] = lambda: test_db
        client = TestClient(app)

        try:
            response = client.get("/api/copywriting/styles")
            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, list)
            assert len(data) == 5

            # Check all expected styles are present
            style_names = [s["name"] for s in data]
            for expected in ["文艺", "活泼", "简约", "攻略型", "日记型"]:
                assert expected in style_names, f"Missing style: {expected}"

            # Check structure
            for style_info in data:
                assert "name" in style_info
                assert "guide" in style_info
                assert "platforms" in style_info
                assert isinstance(style_info["platforms"], list)
        finally:
            app.dependency_overrides.clear()


class TestCopywritingSaveAPI:
    """Tests for the /api/copywriting/save endpoint."""

    def test_save_copywriting(self, test_db):
        """Test saving a copywriting to the database."""
        from app.main import app
        from app.models.database import get_db

        app.dependency_overrides[get_db] = lambda: test_db
        client = TestClient(app)

        try:
            payload = {
                "content_type": "copywriting",
                "title": "北京3日｜一场与自己的对话",
                "body": "🌿 故宫\n光影穿过树梢...",
                "content_body": {
                    "platform": "朋友圈",
                    "style": "文艺",
                    "content": "🌿 故宫\n光影穿过树梢...",
                    "hashtags": ["#旅行", "#北京", "#故宫"],
                    "photo_suggestions": [],
                },
                "style": "文艺",
                "tags": "旅行,北京,故宫",
                "user_id": "test_user",
            }
            response = client.post("/api/copywriting/save", json=payload)
            assert response.status_code == 200
            data = response.json()
            assert "id" in data
            assert data["content_type"] == "copywriting"
            assert data["title"] == "北京3日｜一场与自己的对话"
            assert data["message"] == "文案保存成功"
        finally:
            app.dependency_overrides.clear()

    def test_save_vlog_script(self, test_db):
        """Test saving a Vlog script to the database."""
        from app.main import app
        from app.models.database import get_db

        app.dependency_overrides[get_db] = lambda: test_db
        client = TestClient(app)

        try:
            payload = {
                "content_type": "vlog_script",
                "title": "北京Vlog",
                "content_body": {
                    "title": "北京3日｜一场与自己的对话",
                    "total_duration": "~5分钟",
                    "scenes": [],
                },
                "style": "文艺",
                "user_id": "test_user",
            }
            response = client.post("/api/copywriting/save", json=payload)
            assert response.status_code == 200
            data = response.json()
            assert data["content_type"] == "vlog_script"
        finally:
            app.dependency_overrides.clear()

    def test_save_copywriting_invalid_type(self, test_db):
        """Test that invalid content_type returns 400."""
        from app.main import app
        from app.models.database import get_db

        app.dependency_overrides[get_db] = lambda: test_db
        client = TestClient(app)

        try:
            payload = {
                "content_type": "invalid_type",
                "title": "测试",
                "user_id": "test_user",
            }
            response = client.post("/api/copywriting/save", json=payload)
            assert response.status_code == 400
        finally:
            app.dependency_overrides.clear()
