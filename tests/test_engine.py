from viewtext.engine import LayoutEngine
from viewtext.registry import BaseFieldRegistry


class TestLayoutEngine:
    def test_build_line_str_basic(self):
        registry = BaseFieldRegistry()

        def temp_getter(ctx):
            return ctx["temperature"]

        registry.register("temp", temp_getter)

        engine = LayoutEngine(field_registry=registry)
        layout_config = {
            "lines": [
                {"field": "temp", "index": 0},
            ]
        }
        context = {"temperature": 25}

        result = engine.build_line_str(layout_config, context)

        assert result == ["25"]

    def test_build_line_str_multiple_lines(self):
        registry = BaseFieldRegistry()

        def temp_getter(ctx):
            return ctx["temperature"]

        def humidity_getter(ctx):
            return ctx["humidity"]

        registry.register("temp", temp_getter)
        registry.register("humidity", humidity_getter)

        engine = LayoutEngine(field_registry=registry)
        layout_config = {
            "lines": [
                {"field": "temp", "index": 0},
                {"field": "humidity", "index": 1},
            ]
        }
        context = {"temperature": 25, "humidity": 60}

        result = engine.build_line_str(layout_config, context)

        assert result == ["25", "60"]

    def test_build_line_str_with_formatter(self):
        registry = BaseFieldRegistry()

        def price_getter(ctx):
            return ctx["price"]

        registry.register("price", price_getter)

        engine = LayoutEngine(field_registry=registry)
        layout_config = {
            "lines": [
                {
                    "field": "price",
                    "index": 0,
                    "formatter": "price",
                    "formatter_params": {"symbol": "$", "decimals": 2},
                },
            ]
        }
        context = {"price": 123.45}

        result = engine.build_line_str(layout_config, context)

        assert result == ["$123.45"]

    def test_build_line_str_from_context_without_registry(self):
        engine = LayoutEngine(field_registry=None)
        layout_config = {
            "lines": [
                {"field": "temperature", "index": 0},
            ]
        }
        context = {"temperature": 25}

        result = engine.build_line_str(layout_config, context)

        assert result == ["25"]

    def test_build_line_str_missing_field_returns_empty(self):
        registry = BaseFieldRegistry()
        engine = LayoutEngine(field_registry=registry)
        layout_config = {
            "lines": [
                {"field": "nonexistent", "index": 0},
            ]
        }
        context = {}

        result = engine.build_line_str(layout_config, context)

        assert result == [""]

    def test_build_line_str_with_text_formatter(self):
        registry = BaseFieldRegistry()

        def name_getter(ctx):
            return ctx["name"]

        registry.register("name", name_getter)

        engine = LayoutEngine(field_registry=registry)
        layout_config = {
            "lines": [
                {
                    "field": "name",
                    "index": 0,
                    "formatter": "text",
                    "formatter_params": {"prefix": "Hello, ", "suffix": "!"},
                },
            ]
        }
        context = {"name": "World"}

        result = engine.build_line_str(layout_config, context)

        assert result == ["Hello, World!"]

    def test_build_line_str_with_number_formatter(self):
        registry = BaseFieldRegistry()

        def count_getter(ctx):
            return ctx["count"]

        registry.register("count", count_getter)

        engine = LayoutEngine(field_registry=registry)
        layout_config = {
            "lines": [
                {
                    "field": "count",
                    "index": 0,
                    "formatter": "number",
                    "formatter_params": {"thousands_sep": ","},
                },
            ]
        }
        context = {"count": 1234567}

        result = engine.build_line_str(layout_config, context)

        assert result == ["1,234,567"]

    def test_build_line_str_with_unknown_formatter_falls_back_to_text(self):
        registry = BaseFieldRegistry()

        def value_getter(ctx):
            return ctx["value"]

        registry.register("value", value_getter)

        engine = LayoutEngine(field_registry=registry)
        layout_config = {
            "lines": [
                {
                    "field": "value",
                    "index": 0,
                    "formatter": "unknown_formatter",
                    "formatter_params": {},
                },
            ]
        }
        context = {"value": "test"}

        result = engine.build_line_str(layout_config, context)

        assert result == ["test"]

    def test_build_line_str_empty_lines(self):
        engine = LayoutEngine(field_registry=None)
        layout_config = {"lines": []}
        context = {}

        result = engine.build_line_str(layout_config, context)

        assert result == [""]

    def test_build_line_str_missing_index_or_field_skipped(self):
        registry = BaseFieldRegistry()
        engine = LayoutEngine(field_registry=registry)
        layout_config = {
            "lines": [
                {"field": "temp"},
                {"index": 0},
                {"field": "valid", "index": 1},
            ]
        }
        context = {"valid": "test"}

        result = engine.build_line_str(layout_config, context)

        assert result == ["", "test"]

    def test_get_field_value_registry_priority(self):
        registry = BaseFieldRegistry()

        def custom_getter(ctx):
            return "from_registry"

        registry.register("field", custom_getter)

        engine = LayoutEngine(field_registry=registry)

        result = engine._get_field_value("field", {"field": "from_context"})

        assert result == "from_registry"

    def test_get_field_value_from_context_fallback(self):
        registry = BaseFieldRegistry()
        engine = LayoutEngine(field_registry=registry)

        result = engine._get_field_value("field", {"field": "from_context"})

        assert result == "from_context"

    def test_get_field_value_not_found(self):
        registry = BaseFieldRegistry()
        engine = LayoutEngine(field_registry=registry)

        result = engine._get_field_value("nonexistent", {})

        assert result is None
