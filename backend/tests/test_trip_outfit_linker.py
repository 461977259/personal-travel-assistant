"""
Tests for Trip Outfit Linker Service.

Covers:
  - Auto-linkage during trip generation
  - User-triggered regenerate-outfit API
  - Empty wardrobe friendly message
"""
import pytest

from app.services.trip_outfit_linker import (
    link_outfit_to_trip,
    get_trip_outfits,
    _extract_weather,
    _fill_empty_outfit,
)


class TestTripOutfitLinker:
    """Tests for trip_outfit_linker.py."""

    @pytest.fixture
    def sample_trip_data(self):
        """A minimal trip_data structure returned by generate_trip."""
        return {
            "days": [
                {
                    "day": 1,
                    "date": "2026-05-01",
                    "weather": {"temp": 22, "condition": "晴", "wind_speed": 12, "humidity": 65},
                    "outfit_scene": "城市漫游",
                    "places": [
                        {"name": "天安门", "type": "景点"},
                        {"name": "故宫", "type": "景点"},
                    ],
                    "outfit": {},  # initially empty
                },
                {
                    "day": 2,
                    "date": "2026-05-02",
                    "weather": {"temp": 28, "condition": "多云", "wind_speed": 15, "humidity": 70},
                    "outfit_scene": "户外徒步",
                    "places": [
                        {"name": "颐和园", "type": "公园"},
                    ],
                    "outfit": {},
                },
            ],
            "traffic_summary": {"destination": "北京", "total_days": 2},
            "total_cost_estimate": "¥1500-2000",
        }

    @pytest.fixture
    def sample_wardrobe(self):
        return [
            {"id": 1, "name": "白色T恤", "type": "上装", "color": "白色", "thickness": "薄", "scene": "日常"},
            {"id": 2, "name": "深蓝西装外套", "type": "外套", "color": "深蓝色", "thickness": "中等", "scene": "商务"},
            {"id": 3, "name": "黑色直筒裤", "type": "裤装", "color": "黑色", "thickness": "中等", "scene": "日常"},
            {"id": 4, "name": "灰色运动鞋", "type": "鞋", "color": "灰色", "thickness": "中等", "scene": "休闲"},
        ]

    # -------------------------------------------------------------------------
    # link_outfit_to_trip
    # -------------------------------------------------------------------------

    def test_link_outfit_populates_each_day(self, sample_trip_data, sample_wardrobe):
        result = link_outfit_to_trip(sample_trip_data, user_id=1, wardrobe_items=sample_wardrobe)
        assert "days" in result
        assert len(result["days"]) == 2
        for day in result["days"]:
            assert "outfit" in day
            assert "outfit" in day["outfit"]   # key from outfit_engine
            assert "reason" in day["outfit"]
            assert "tips" in day["outfit"]

    def test_link_outfit_returns_new_dict(self, sample_trip_data, sample_wardrobe):
        import copy
        original = copy.deepcopy(sample_trip_data)
        result = link_outfit_to_trip(sample_trip_data, user_id=1, wardrobe_items=sample_wardrobe)
        # Result should be a new dict (not same object)
        assert result is not sample_trip_data
        # Outer-level keys should be new references
        assert result["days"] is not sample_trip_data["days"]
        # Original nested data preserved (shallow-copy isolation)
        for orig_day, result_day in zip(sample_trip_data["days"], result["days"]):
            assert orig_day["day"] == result_day["day"]

    def test_link_outfit_empty_wardrobe_friendly_message(self, sample_trip_data):
        result = link_outfit_to_trip(sample_trip_data, user_id=1, wardrobe_items=[])
        assert "days" in result
        for day in result["days"]:
            assert day["outfit"]["outfit"] == []
            assert "衣橱" in day["outfit"]["reason"] or "衣橱" in day["outfit"]["tips"]

    def test_link_outfit_missing_days_key(self):
        result = link_outfit_to_trip({}, user_id=1, wardrobe_items=[])
        assert result == {}

    def test_link_outfit_none_wardrobe_uses_empty(self, sample_trip_data):
        # Passing None wardrobe is equivalent to empty
        result = link_outfit_to_trip(sample_trip_data, user_id=1, wardrobe_items=None)
        for day in result["days"]:
            assert day["outfit"]["outfit"] == []

    # -------------------------------------------------------------------------
    # _extract_weather
    # -------------------------------------------------------------------------

    def test_extract_weather_trip_engine_format(self):
        day_plan = {"weather": {"temp": 22, "condition": "晴"}}
        w = _extract_weather(day_plan)
        assert w["temperature"] == 22
        assert w["condition"] == "晴"

    def test_extract_weather_outfit_engine_format(self):
        day_plan = {"weather": {"temperature": 22, "condition": "晴", "wind_speed": 12}}
        w = _extract_weather(day_plan)
        assert w["temperature"] == 22

    def test_extract_weather_missing_weather(self):
        w = _extract_weather({})
        assert w == {}

    # -------------------------------------------------------------------------
    # _fill_empty_outfit
    # -------------------------------------------------------------------------

    def test_fill_empty_outfit_all_days(self, sample_trip_data):
        result = _fill_empty_outfit(sample_trip_data)
        for day in result["days"]:
            assert day["outfit"]["outfit"] == []
            assert "衣橱" in day["outfit"]["reason"]

    # -------------------------------------------------------------------------
    # get_trip_outfits
    # -------------------------------------------------------------------------

    def test_get_trip_outfits_returns_all_days(self, sample_trip_data):
        outfits = get_trip_outfits(sample_trip_data)
        assert len(outfits) == 2
        assert outfits[0]["day"] == 1
        assert outfits[1]["day"] == 2

    def test_get_trip_outfits_missing_days(self):
        assert get_trip_outfits({}) == []

    def test_get_trip_outfits_includes_scene(self, sample_trip_data):
        outfits = get_trip_outfits(sample_trip_data)
        assert outfits[0]["outfit_scene"] == "城市漫游"
        assert outfits[1]["outfit_scene"] == "户外徒步"
