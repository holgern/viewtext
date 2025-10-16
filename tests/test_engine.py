import os
import tempfile

from viewtext.engine import LayoutEngine
from viewtext.loader import LayoutLoader
from viewtext.registry import BaseFieldRegistry
from viewtext.registry_builder import RegistryBuilder


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


class TestLayoutEngineWithComputedFields:
    def test_integration_celsius_to_fahrenheit(self):
        fields_content = """
[fields.temp_f]
operation = "celsius_to_fahrenheit"
sources = ["temp_c"]
default = 0.0
"""
        layouts_content = """
[layouts.temperature]
name = "Temperature"

[[layouts.temperature.lines]]
field = "temp_f"
index = 0
formatter = "number"

[layouts.temperature.lines.formatter_params]
decimals = 1
suffix = "°F"
"""
        tmp_fields = tempfile.NamedTemporaryFile(
            mode="w", suffix=".toml", delete=False, encoding="utf-8"
        )
        tmp_fields.write(fields_content)
        tmp_fields.close()
        fields_path = tmp_fields.name

        tmp_layouts = tempfile.NamedTemporaryFile(
            mode="w", suffix=".toml", delete=False, encoding="utf-8"
        )
        tmp_layouts.write(layouts_content)
        tmp_layouts.close()
        layouts_path = tmp_layouts.name

        try:
            loader = LayoutLoader(config_path=layouts_path, fields_path=fields_path)
            layout = loader.get_layout("temperature")

            registry = RegistryBuilder.build_from_config(loader=loader)

            engine = LayoutEngine(field_registry=registry)
            context = {"temp_c": 25}

            result = engine.build_line_str(layout, context)

            assert result == ["77.0°F"]
        finally:
            os.unlink(fields_path)
            os.unlink(layouts_path)

    def test_integration_multiply_operation(self):
        fields_content = """
[fields.total]
operation = "multiply"
sources = ["price", "quantity"]
default = 0.0
"""
        layouts_content = """
[layouts.shopping]
name = "Shopping"

[[layouts.shopping.lines]]
field = "total"
index = 0
formatter = "price"

[layouts.shopping.lines.formatter_params]
symbol = "$"
decimals = 2
"""
        tmp_fields = tempfile.NamedTemporaryFile(
            mode="w", suffix=".toml", delete=False, encoding="utf-8"
        )
        tmp_fields.write(fields_content)
        tmp_fields.close()
        fields_path = tmp_fields.name

        tmp_layouts = tempfile.NamedTemporaryFile(
            mode="w", suffix=".toml", delete=False, encoding="utf-8"
        )
        tmp_layouts.write(layouts_content)
        tmp_layouts.close()
        layouts_path = tmp_layouts.name

        try:
            loader = LayoutLoader(config_path=layouts_path, fields_path=fields_path)
            layout = loader.get_layout("shopping")

            registry = RegistryBuilder.build_from_config(loader=loader)

            engine = LayoutEngine(field_registry=registry)
            context = {"price": 19.99, "quantity": 3}

            result = engine.build_line_str(layout, context)

            assert result == ["$59.97"]
        finally:
            os.unlink(fields_path)
            os.unlink(layouts_path)

    def test_integration_average_operation(self):
        fields_content = """
[fields.avg]
operation = "average"
sources = ["score1", "score2", "score3"]
default = 0.0
"""
        layouts_content = """
[layouts.scores]
name = "Scores"

[[layouts.scores.lines]]
field = "avg"
index = 0
formatter = "number"

[layouts.scores.lines.formatter_params]
decimals = 2
"""
        tmp_fields = tempfile.NamedTemporaryFile(
            mode="w", suffix=".toml", delete=False, encoding="utf-8"
        )
        tmp_fields.write(fields_content)
        tmp_fields.close()
        fields_path = tmp_fields.name

        tmp_layouts = tempfile.NamedTemporaryFile(
            mode="w", suffix=".toml", delete=False, encoding="utf-8"
        )
        tmp_layouts.write(layouts_content)
        tmp_layouts.close()
        layouts_path = tmp_layouts.name

        try:
            loader = LayoutLoader(config_path=layouts_path, fields_path=fields_path)
            layout = loader.get_layout("scores")

            registry = RegistryBuilder.build_from_config(loader=loader)

            engine = LayoutEngine(field_registry=registry)
            context = {"score1": 85, "score2": 90, "score3": 88}

            result = engine.build_line_str(layout, context)

            assert result == ["87.67"]
        finally:
            os.unlink(fields_path)
            os.unlink(layouts_path)

    def test_integration_linear_transform(self):
        fields_content = """
[fields.scaled]
operation = "linear_transform"
sources = ["value"]
multiply = 2.5
add = 10
default = 0.0
"""
        layouts_content = """
[layouts.transform]
name = "Transform"

[[layouts.transform.lines]]
field = "scaled"
index = 0
formatter = "number"

[layouts.transform.lines.formatter_params]
decimals = 1
"""
        tmp_fields = tempfile.NamedTemporaryFile(
            mode="w", suffix=".toml", delete=False, encoding="utf-8"
        )
        tmp_fields.write(fields_content)
        tmp_fields.close()
        fields_path = tmp_fields.name

        tmp_layouts = tempfile.NamedTemporaryFile(
            mode="w", suffix=".toml", delete=False, encoding="utf-8"
        )
        tmp_layouts.write(layouts_content)
        tmp_layouts.close()
        layouts_path = tmp_layouts.name

        try:
            loader = LayoutLoader(config_path=layouts_path, fields_path=fields_path)
            layout = loader.get_layout("transform")

            registry = RegistryBuilder.build_from_config(loader=loader)

            engine = LayoutEngine(field_registry=registry)
            context = {"value": 20}

            result = engine.build_line_str(layout, context)

            assert result == ["60.0"]
        finally:
            os.unlink(fields_path)
            os.unlink(layouts_path)

    def test_integration_missing_source_uses_default(self):
        fields_content = """
[fields.temp_f]
operation = "celsius_to_fahrenheit"
sources = ["temp_c"]
default = 32.0
"""
        layouts_content = """
[layouts.temperature]
name = "Temperature"

[[layouts.temperature.lines]]
field = "temp_f"
index = 0
formatter = "number"

[layouts.temperature.lines.formatter_params]
decimals = 1
suffix = "°F"
"""
        tmp_fields = tempfile.NamedTemporaryFile(
            mode="w", suffix=".toml", delete=False, encoding="utf-8"
        )
        tmp_fields.write(fields_content)
        tmp_fields.close()
        fields_path = tmp_fields.name

        tmp_layouts = tempfile.NamedTemporaryFile(
            mode="w", suffix=".toml", delete=False, encoding="utf-8"
        )
        tmp_layouts.write(layouts_content)
        tmp_layouts.close()
        layouts_path = tmp_layouts.name

        try:
            loader = LayoutLoader(config_path=layouts_path, fields_path=fields_path)
            layout = loader.get_layout("temperature")

            registry = RegistryBuilder.build_from_config(loader=loader)

            engine = LayoutEngine(field_registry=registry)
            context = {}

            result = engine.build_line_str(layout, context)

            assert result == ["32.0°F"]
        finally:
            os.unlink(fields_path)
            os.unlink(layouts_path)

    def test_integration_multiple_computed_fields(self):
        fields_content = """
[fields.temp_f]
operation = "celsius_to_fahrenheit"
sources = ["temp_c"]
default = 0.0

[fields.total]
operation = "multiply"
sources = ["price", "qty"]
default = 0.0
"""
        layouts_content = """
[layouts.multi]
name = "Multi"

[[layouts.multi.lines]]
field = "temp_f"
index = 0
formatter = "number"

[layouts.multi.lines.formatter_params]
decimals = 1
suffix = "°F"

[[layouts.multi.lines]]
field = "total"
index = 1
formatter = "price"

[layouts.multi.lines.formatter_params]
symbol = "$"
decimals = 2
"""
        tmp_fields = tempfile.NamedTemporaryFile(
            mode="w", suffix=".toml", delete=False, encoding="utf-8"
        )
        tmp_fields.write(fields_content)
        tmp_fields.close()
        fields_path = tmp_fields.name

        tmp_layouts = tempfile.NamedTemporaryFile(
            mode="w", suffix=".toml", delete=False, encoding="utf-8"
        )
        tmp_layouts.write(layouts_content)
        tmp_layouts.close()
        layouts_path = tmp_layouts.name

        try:
            loader = LayoutLoader(config_path=layouts_path, fields_path=fields_path)
            layout = loader.get_layout("multi")

            registry = RegistryBuilder.build_from_config(loader=loader)

            engine = LayoutEngine(field_registry=registry)
            context = {"temp_c": 0, "price": 10.50, "qty": 2}

            result = engine.build_line_str(layout, context)

            assert result == ["32.0°F", "$21.00"]
        finally:
            os.unlink(fields_path)
            os.unlink(layouts_path)
