import os
import tempfile
from typing import Any

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

    def test_conditional_operation_integration(self):
        fields_content = """
[fields.price_display]
operation = "conditional"
condition = { field = "currency", equals = "USD" }
if_true = "$~amount~"
if_false = "~amount~ ~currency~"
default = "N/A"

[fields.membership_badge]
operation = "conditional"
condition = { field = "is_premium", equals = "true" }
if_true = "⭐ Premium"
if_false = "Standard"
default = "Guest"
"""
        layouts_content = """
[layouts.pricing]
name = "Pricing Display"

[[layouts.pricing.lines]]
field = "price_display"
index = 0
formatter = "text"

[[layouts.pricing.lines]]
field = "membership_badge"
index = 1
formatter = "text"
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
            layout = loader.get_layout("pricing")

            registry = RegistryBuilder.build_from_config(loader=loader)

            engine = LayoutEngine(field_registry=registry)

            context_usd = {
                "currency": "USD",
                "amount": "99.99",
                "is_premium": "true",
            }
            result_usd = engine.build_line_str(layout, context_usd)
            assert result_usd == ["$99.99", "⭐ Premium"]

            context_eur = {
                "currency": "EUR",
                "amount": "89.99",
                "is_premium": "false",
            }
            result_eur = engine.build_line_str(layout, context_eur)
            assert result_eur == ["89.99 EUR", "Standard"]

            context_missing = {"amount": "49.99", "is_premium": "true"}
            result_missing = engine.build_line_str(layout, context_missing)
            assert result_missing == ["N/A", "⭐ Premium"]
        finally:
            os.unlink(fields_path)
            os.unlink(layouts_path)

    def test_format_number_operation_integration(self):
        fields_content = """
[fields.formatted_comma]
operation = "format_number"
sources = ["value1"]
thousands_sep = ","
decimals_param = 0
default = "N/A"

[fields.formatted_european]
operation = "format_number"
sources = ["value2"]
thousands_sep = "."
decimal_sep = ","
decimals_param = 2
default = "N/A"

[fields.formatted_space]
operation = "format_number"
sources = ["value3"]
thousands_sep = " "
decimals_param = 0
default = "N/A"
"""
        layouts_content = """
[layouts.numbers]
name = "Number Display"

[[layouts.numbers.lines]]
field = "formatted_comma"
index = 0
formatter = "text"

[[layouts.numbers.lines]]
field = "formatted_european"
index = 1
formatter = "text"

[[layouts.numbers.lines]]
field = "formatted_space"
index = 2
formatter = "text"
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
            layout = loader.get_layout("numbers")

            registry = RegistryBuilder.build_from_config(loader=loader)

            engine = LayoutEngine(field_registry=registry)

            context = {"value1": 100000, "value2": 1234567.89, "value3": 9876543}
            result = engine.build_line_str(layout, context)
            assert result == ["100,000", "1.234.567,89", "9 876 543"]

            context_missing = {"value1": 50000}
            result_missing = engine.build_line_str(layout, context_missing)
            assert result_missing == ["50,000", "N/A", "N/A"]
        finally:
            os.unlink(fields_path)
            os.unlink(layouts_path)

    def test_python_function_field(self):
        from datetime import datetime

        fields_data = """
[fields.current_time]
python_module = "datetime"
python_function = "datetime.datetime.now().timestamp()"
transform = "int"
type = "int"
"""
        layouts_data = """
[layouts.test]
name = "Test Layout"

[[layouts.test.lines]]
field = "current_time"
index = 0
"""

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".toml", delete=False
        ) as fields_file:
            fields_file.write(fields_data)
            fields_path = fields_file.name

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".toml", delete=False
        ) as layouts_file:
            layouts_file.write(layouts_data)
            layouts_path = layouts_file.name

        try:
            loader = LayoutLoader(config_path=layouts_path, fields_path=fields_path)
            layout = loader.get_layout("test")
            registry = RegistryBuilder.build_from_config(loader=loader)
            engine = LayoutEngine(field_registry=registry)

            context: dict[str, Any] = {}
            result = engine.build_line_str(layout, context)

            current_timestamp = int(datetime.now().timestamp())
            result_timestamp = int(result[0])
            assert abs(result_timestamp - current_timestamp) < 2
        finally:
            os.unlink(fields_path)
            os.unlink(layouts_path)

    def test_python_function_caching(self):
        fields_data = """
[fields.random_value]
python_module = "random"
python_function = "random.random()"
type = "float"
"""
        layouts_data = """
[layouts.test]
name = "Test Layout"

[[layouts.test.lines]]
field = "random_value"
index = 0

[[layouts.test.lines]]
field = "random_value"
index = 1
"""

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".toml", delete=False
        ) as fields_file:
            fields_file.write(fields_data)
            fields_path = fields_file.name

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".toml", delete=False
        ) as layouts_file:
            layouts_file.write(layouts_data)
            layouts_path = layouts_file.name

        try:
            loader = LayoutLoader(config_path=layouts_path, fields_path=fields_path)
            layout = loader.get_layout("test")
            registry = RegistryBuilder.build_from_config(loader=loader)
            engine = LayoutEngine(field_registry=registry)

            context: dict[str, Any] = {}
            result = engine.build_line_str(layout, context)

            assert result[0] == result[1]
        finally:
            os.unlink(fields_path)
            os.unlink(layouts_path)


class TestFormatterPresets:
    def test_formatter_preset_in_layout(self):
        formatters_content = """
[formatters.usd_price]
type = "price"
symbol = "$"
decimals = 2
thousands_sep = ","
"""
        layouts_content = """
[layouts.product]
name = "Product"

[[layouts.product.lines]]
field = "price"
index = 0
formatter = "usd_price"
"""
        tmp_formatters = tempfile.NamedTemporaryFile(
            mode="w", suffix=".toml", delete=False, encoding="utf-8"
        )
        tmp_formatters.write(formatters_content)
        tmp_formatters.close()
        formatters_path = tmp_formatters.name

        tmp_layouts = tempfile.NamedTemporaryFile(
            mode="w", suffix=".toml", delete=False, encoding="utf-8"
        )
        tmp_layouts.write(layouts_content)
        tmp_layouts.close()
        layouts_path = tmp_layouts.name

        try:
            loader = LayoutLoader(
                config_path=layouts_path, formatters_path=formatters_path
            )
            layout = loader.get_layout("product")

            engine = LayoutEngine(field_registry=None, layout_loader=loader)
            context = {"price": 1234.567}

            result = engine.build_line_str(layout, context)

            assert result == ["$1,234.57"]
        finally:
            os.unlink(formatters_path)
            os.unlink(layouts_path)

    def test_formatter_preset_datetime(self):
        from datetime import datetime

        formatters_content = """
[formatters.time_hm]
type = "datetime"
format = "%H:%M"
"""
        layouts_content = """
[layouts.time_display]
name = "Time Display"

[[layouts.time_display.lines]]
field = "timestamp"
index = 0
formatter = "time_hm"
"""
        tmp_formatters = tempfile.NamedTemporaryFile(
            mode="w", suffix=".toml", delete=False, encoding="utf-8"
        )
        tmp_formatters.write(formatters_content)
        tmp_formatters.close()
        formatters_path = tmp_formatters.name

        tmp_layouts = tempfile.NamedTemporaryFile(
            mode="w", suffix=".toml", delete=False, encoding="utf-8"
        )
        tmp_layouts.write(layouts_content)
        tmp_layouts.close()
        layouts_path = tmp_layouts.name

        try:
            loader = LayoutLoader(
                config_path=layouts_path, formatters_path=formatters_path
            )
            layout = loader.get_layout("time_display")

            engine = LayoutEngine(field_registry=None, layout_loader=loader)
            timestamp = 1234567890
            expected = datetime.fromtimestamp(timestamp).strftime("%H:%M")
            context = {"timestamp": timestamp}

            result = engine.build_line_str(layout, context)

            assert result == [expected]
        finally:
            os.unlink(formatters_path)
            os.unlink(layouts_path)

    def test_formatter_preset_number(self):
        formatters_content = """
[formatters.minutes]
type = "number"
suffix = " MIN"
decimals = 0
"""
        layouts_content = """
[layouts.duration]
name = "Duration"

[[layouts.duration.lines]]
field = "elapsed"
index = 0
formatter = "minutes"
"""
        tmp_formatters = tempfile.NamedTemporaryFile(
            mode="w", suffix=".toml", delete=False, encoding="utf-8"
        )
        tmp_formatters.write(formatters_content)
        tmp_formatters.close()
        formatters_path = tmp_formatters.name

        tmp_layouts = tempfile.NamedTemporaryFile(
            mode="w", suffix=".toml", delete=False, encoding="utf-8"
        )
        tmp_layouts.write(layouts_content)
        tmp_layouts.close()
        layouts_path = tmp_layouts.name

        try:
            loader = LayoutLoader(
                config_path=layouts_path, formatters_path=formatters_path
            )
            layout = loader.get_layout("duration")

            engine = LayoutEngine(field_registry=None, layout_loader=loader)
            context = {"elapsed": 45.7}

            result = engine.build_line_str(layout, context)

            assert result == ["46 MIN"]
        finally:
            os.unlink(formatters_path)
            os.unlink(layouts_path)

    def test_formatter_preset_with_inline_params_uses_inline(self):
        formatters_content = """
[formatters.usd_price]
type = "price"
symbol = "$"
decimals = 2
"""
        layouts_content = """
[layouts.product]
name = "Product"

[[layouts.product.lines]]
field = "price"
index = 0
formatter = "price"

[layouts.product.lines.formatter_params]
symbol = "£"
decimals = 3
"""
        tmp_formatters = tempfile.NamedTemporaryFile(
            mode="w", suffix=".toml", delete=False, encoding="utf-8"
        )
        tmp_formatters.write(formatters_content)
        tmp_formatters.close()
        formatters_path = tmp_formatters.name

        tmp_layouts = tempfile.NamedTemporaryFile(
            mode="w", suffix=".toml", delete=False, encoding="utf-8"
        )
        tmp_layouts.write(layouts_content)
        tmp_layouts.close()
        layouts_path = tmp_layouts.name

        try:
            loader = LayoutLoader(
                config_path=layouts_path, formatters_path=formatters_path
            )
            layout = loader.get_layout("product")

            engine = LayoutEngine(field_registry=None, layout_loader=loader)
            context = {"price": 99.999}

            result = engine.build_line_str(layout, context)

            assert result == ["£99.999"]
        finally:
            os.unlink(formatters_path)
            os.unlink(layouts_path)

    def test_formatter_preset_nonexistent_falls_back_to_builtin(self):
        layouts_content = """
[layouts.test]
name = "Test"

[[layouts.test.lines]]
field = "value"
index = 0
formatter = "text"
"""
        tmp_layouts = tempfile.NamedTemporaryFile(
            mode="w", suffix=".toml", delete=False, encoding="utf-8"
        )
        tmp_layouts.write(layouts_content)
        tmp_layouts.close()
        layouts_path = tmp_layouts.name

        try:
            loader = LayoutLoader(config_path=layouts_path)
            layout = loader.get_layout("test")

            engine = LayoutEngine(field_registry=None, layout_loader=loader)
            context = {"value": "hello"}

            result = engine.build_line_str(layout, context)

            assert result == ["hello"]
        finally:
            os.unlink(layouts_path)

    def test_multiple_presets_in_same_layout(self):
        from datetime import datetime

        formatters_content = """
[formatters.usd_price]
type = "price"
symbol = "$"
decimals = 2

[formatters.time_hm]
type = "datetime"
format = "%H:%M"

[formatters.percent]
type = "number"
suffix = "%"
decimals = 1
"""
        layouts_content = """
[layouts.dashboard]
name = "Dashboard"

[[layouts.dashboard.lines]]
field = "price"
index = 0
formatter = "usd_price"

[[layouts.dashboard.lines]]
field = "timestamp"
index = 1
formatter = "time_hm"

[[layouts.dashboard.lines]]
field = "change"
index = 2
formatter = "percent"
"""
        tmp_formatters = tempfile.NamedTemporaryFile(
            mode="w", suffix=".toml", delete=False, encoding="utf-8"
        )
        tmp_formatters.write(formatters_content)
        tmp_formatters.close()
        formatters_path = tmp_formatters.name

        tmp_layouts = tempfile.NamedTemporaryFile(
            mode="w", suffix=".toml", delete=False, encoding="utf-8"
        )
        tmp_layouts.write(layouts_content)
        tmp_layouts.close()
        layouts_path = tmp_layouts.name

        try:
            loader = LayoutLoader(
                config_path=layouts_path, formatters_path=formatters_path
            )
            layout = loader.get_layout("dashboard")

            engine = LayoutEngine(field_registry=None, layout_loader=loader)
            timestamp = 1234567890
            expected_time = datetime.fromtimestamp(timestamp).strftime("%H:%M")
            context = {"price": 100.5, "timestamp": timestamp, "change": 2.345}

            result = engine.build_line_str(layout, context)

            assert result == ["$100.50", expected_time, "2.3%"]
        finally:
            os.unlink(formatters_path)
            os.unlink(layouts_path)

    def test_preset_without_layout_loader_falls_back(self):
        registry = BaseFieldRegistry()

        def price_getter(ctx):
            return ctx["price"]

        registry.register("price", price_getter)

        engine = LayoutEngine(field_registry=registry, layout_loader=None)
        layout_config = {
            "lines": [
                {
                    "field": "price",
                    "index": 0,
                    "formatter": "usd_price",
                    "formatter_params": {},
                },
            ]
        }
        context = {"price": 123.45}

        result = engine.build_line_str(layout_config, context)

        assert result == ["123.45"]
