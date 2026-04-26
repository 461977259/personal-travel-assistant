"""
Tests for Outfit Engine.
"""
import pytest
from app.services.outfit_engine import (
    recommend_outfit,
    _get_layer_count,
    _colors_compatible,
    _score_item_for_scene,
    _generate_reason,
    _generate_tips,
    _get_required_types,
    _ensure_color_harmony,
)


class TestOutfitEngine:
    """Test outfit recommendation engine."""

    @pytest.fixture
    def sample_wardrobe(self):
        return [
            {"id": 1, "name": "白色T恤", "type": "上装", "color": "白色", "thickness": "薄", "scene": "日常"},
            {"id": 2, "name": "深蓝西装外套", "type": "外套", "color": "深蓝色", "thickness": "中等", "scene": "商务"},
            {"id": 3, "name": "黑色直筒裤", "type": "裤装", "color": "黑色", "thickness": "中等", "scene": "日常"},
            {"id": 4, "name": "灰色运动鞋", "type": "鞋", "color": "灰色", "thickness": "中等", "scene": "休闲"},
            {"id": 5, "name": "红色连衣裙", "type": "裙装", "color": "红色", "thickness": "薄", "scene": "休闲"},
            {"id": 6, "name": "黑色大衣", "type": "外套", "color": "黑色", "thickness": "厚", "scene": "商务"},
            {"id": 7, "name": "保暖内衣", "type": "上装", "color": "灰色", "thickness": "厚", "scene": "日常"},
            {"id": 8, "name": "卡其色休闲裤", "type": "裤装", "color": "卡其色", "thickness": "中等", "scene": "休闲"},
            {"id": 9, "name": "蓝色针织衫", "type": "上装", "color": "浅蓝色", "thickness": "中等", "scene": "商务"},
            {"id": 10, "name": "米色长裙", "type": "裙装", "color": "米色", "thickness": "薄", "scene": "休闲"},
        ]

    @pytest.mark.parametrize("temperature,expected_layers", [
        (-5, 3),   # <5°C -> 3 layers
        (0, 3),    # <5°C -> 3 layers
        (5, 2),    # 5~15°C -> 2 layers
        (10, 2),   # 5~15°C -> 2 layers
        (15, 2),   # 15~25°C -> 2 layers
        (20, 2),   # 15~25°C -> 2 layers
        (25, 1),   # >25°C -> 1 layer
        (30, 1),   # >25°C -> 1 layer
    ])
    def test_layer_count(self, temperature, expected_layers):
        assert _get_layer_count(temperature) == expected_layers

    def test_colors_compatible_same_color(self):
        assert _colors_compatible("黑色", "黑色") is True

    def test_colors_compatible_same_family(self):
        assert _colors_compatible("白色", "浅灰色") is True

    def test_colors_compatible_different_family(self):
        # Black and white should be compatible
        assert _colors_compatible("黑色", "白色") is True

    def test_colors_incompatible_high_saturation(self):
        # High saturation colors shouldn't clash
        assert _colors_compatible("红色", "黄色") is False

    def test_score_item_for_scene_direct_match(self):
        item = {"scene": "商务", "type": "外套"}
        score = _score_item_for_scene(item, "商务")
        assert score >= 5.0

    def test_score_item_for_scene_proximity(self):
        item = {"scene": "商务", "type": "上装"}
        score = _score_item_for_scene(item, "通勤")
        assert score >= 3.0

    def test_recommend_outfit_hot_weather(self, sample_wardrobe):
        weather = {"temperature": 30, "wind_speed": 10, "humidity": 60, "condition": "晴"}
        result = recommend_outfit(sample_wardrobe, weather, "休闲")
        assert "outfit" in result
        assert "reason" in result
        assert "tips" in result
        assert len(result["outfit"]) > 0

    def test_recommend_outfit_cold_weather(self, sample_wardrobe):
        weather = {"temperature": 2, "wind_speed": 15, "humidity": 50, "condition": "阴"}
        result = recommend_outfit(sample_wardrobe, weather, "通勤")
        assert "outfit" in result
        # Cold weather should produce more items (3 layers)
        assert len(result["outfit"]) >= 2

    def test_recommend_outfit_empty_wardrobe(self):
        weather = {"temperature": 22, "wind_speed": 10, "humidity": 60, "condition": "多云"}
        result = recommend_outfit([], weather, "休闲")
        assert result["outfit"] == []

    def test_recommend_outfit_with_body_type(self, sample_wardrobe):
        weather = {"temperature": 22, "wind_speed": 10, "humidity": 60, "condition": "晴"}
        result = recommend_outfit(sample_wardrobe, weather, "旅行", body_type="苹果型")
        assert "outfit" in result
        assert "reason" in result
        # Body type should be mentioned in reason
        assert "苹果型" in result["reason"]

    def test_generate_reason_contains_temp(self, sample_wardrobe):
        weather = {"temperature": 22, "wind_speed": 10, "humidity": 60, "condition": "晴"}
        result = recommend_outfit(sample_wardrobe, weather, "休闲")
        assert "22" in result["reason"]

    def test_generate_tips_rainy(self, sample_wardrobe):
        weather = {"temperature": 18, "wind_speed": 10, "humidity": 80, "condition": "小雨"}
        result = recommend_outfit(sample_wardrobe, weather, "旅行")
        assert "雨" in result["tips"]

    def test_generate_tips_windy(self, sample_wardrobe):
        weather = {"temperature": 15, "wind_speed": 25, "humidity": 50, "condition": "多云"}
        result = recommend_outfit(sample_wardrobe, weather, "休闲")
        assert "风" in result["tips"]

    def test_get_required_types_cold(self):
        types = _get_required_types("通勤", 3)
        assert "外套" in types
        assert "上装" in types
        assert "裤装" in types

    def test_get_required_types_hot(self):
        types = _get_required_types("休闲", 1)
        assert "上装" in types
        assert "裤装" in types
        assert "鞋" in types

    def test_ensure_color_harmony(self):
        outfit = [
            {"item": "白衬衫", "type": "上装", "color": "白色", "layer": 1},
            {"item": "黑裤子", "type": "裤装", "color": "黑色", "layer": 1},
            {"item": "红鞋", "type": "鞋", "color": "红色", "layer": 1},
        ]
        # White and black are compatible, but red might clash
        result = _ensure_color_harmony(outfit)
        assert len(result) >= 1

    def test_recommend_outfit_scene_travel(self, sample_wardrobe):
        weather = {"temperature": 25, "wind_speed": 12, "humidity": 55, "condition": "晴"}
        result = recommend_outfit(sample_wardrobe, weather, "旅行")
        assert "outfit" in result
        assert "舒适" in result["reason"] or "旅行" in result["reason"]

    def test_recommend_outfit_scene_sports(self, sample_wardrobe):
        weather = {"temperature": 20, "wind_speed": 8, "humidity": 50, "condition": "晴"}
        result = recommend_outfit(sample_wardrobe, weather, "运动")
        assert "outfit" in result
        # Sports scene should prioritize functionality
        assert "tips" in result

    def test_recommend_outfit_scene_business(self, sample_wardrobe):
        weather = {"temperature": 18, "wind_speed": 10, "humidity": 55, "condition": "多云"}
        result = recommend_outfit(sample_wardrobe, weather, "商务")
        assert "outfit" in result
        # Business should mention formal/proper
        assert "商务" in result["reason"] or "得体" in result["reason"]
