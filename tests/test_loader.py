import os
import tempfile

import pytest

from viewtext.loader import LayoutLoader


class TestLayoutLoader:
    def test_load_valid_config(self):
        config_content = """
[layouts.test_layout]
name = "Test Layout"

[[layouts.test_layout.lines]]
field = "temperature"
index = 0
formatter = "number"

[layouts.test_layout.lines.formatter_params]
decimals = 1
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".toml", delete=False) as tmp:
            tmp.write(config_content)
            tmp_path = tmp.name

        try:
            loader = LayoutLoader(config_path=tmp_path)
            config = loader.load()

            assert config is not None
            assert "test_layout" in config.layouts
            assert config.layouts["test_layout"].name == "Test Layout"
            assert len(config.layouts["test_layout"].lines) == 1
        finally:
            os.unlink(tmp_path)

    def test_load_nonexistent_config_raises_error(self):
        loader = LayoutLoader(config_path="/nonexistent/path.toml")

        with pytest.raises(FileNotFoundError, match="Layout config not found"):
            loader.load()

    def test_get_layout_returns_correct_layout(self):
        config_content = """
[layouts.test_layout]
name = "Test Layout"

[[layouts.test_layout.lines]]
field = "field1"
index = 0

[layouts.another_layout]
name = "Another Layout"

[[layouts.another_layout.lines]]
field = "field2"
index = 0
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".toml", delete=False) as tmp:
            tmp.write(config_content)
            tmp_path = tmp.name

        try:
            loader = LayoutLoader(config_path=tmp_path)
            layout = loader.get_layout("test_layout")

            assert layout["name"] == "Test Layout"
            assert len(layout["lines"]) == 1
            assert layout["lines"][0]["field"] == "field1"
        finally:
            os.unlink(tmp_path)

    def test_get_layout_unknown_raises_error(self):
        config_content = """
[layouts.test_layout]
name = "Test Layout"

[[layouts.test_layout.lines]]
field = "field1"
index = 0
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".toml", delete=False) as tmp:
            tmp.write(config_content)
            tmp_path = tmp.name

        try:
            loader = LayoutLoader(config_path=tmp_path)

            with pytest.raises(ValueError, match="Unknown layout: nonexistent"):
                loader.get_layout("nonexistent")
        finally:
            os.unlink(tmp_path)

    def test_get_formatter_params_returns_params(self):
        config_content = """
[layouts.test_layout]
name = "Test Layout"

[[layouts.test_layout.lines]]
field = "field1"
index = 0

[formatters.price_usd]
type = "price"
symbol = "$"
decimals = 2
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".toml", delete=False) as tmp:
            tmp.write(config_content)
            tmp_path = tmp.name

        try:
            loader = LayoutLoader(config_path=tmp_path)
            params = loader.get_formatter_params("price_usd")

            assert params["symbol"] == "$"
            assert params["decimals"] == 2
            assert "type" not in params
        finally:
            os.unlink(tmp_path)

    def test_get_formatter_params_nonexistent_returns_empty(self):
        config_content = """
[layouts.test_layout]
name = "Test Layout"

[[layouts.test_layout.lines]]
field = "field1"
index = 0
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".toml", delete=False) as tmp:
            tmp.write(config_content)
            tmp_path = tmp.name

        try:
            loader = LayoutLoader(config_path=tmp_path)
            params = loader.get_formatter_params("nonexistent")

            assert params == {}
        finally:
            os.unlink(tmp_path)

    def test_get_field_mappings_returns_mappings(self):
        config_content = """
[layouts.test_layout]
name = "Test Layout"

[[layouts.test_layout.lines]]
field = "field1"
index = 0

[fields.temperature]
context_key = "temp"
default = 0

[fields.humidity]
context_key = "humid"
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".toml", delete=False) as tmp:
            tmp.write(config_content)
            tmp_path = tmp.name

        try:
            loader = LayoutLoader(config_path=tmp_path)
            mappings = loader.get_field_mappings()

            assert "temperature" in mappings
            assert mappings["temperature"].context_key == "temp"
            assert mappings["temperature"].default == 0
            assert "humidity" in mappings
            assert mappings["humidity"].context_key == "humid"
        finally:
            os.unlink(tmp_path)

    def test_get_field_mappings_no_fields_returns_empty(self):
        config_content = """
[layouts.test_layout]
name = "Test Layout"

[[layouts.test_layout.lines]]
field = "field1"
index = 0
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".toml", delete=False) as tmp:
            tmp.write(config_content)
            tmp_path = tmp.name

        try:
            loader = LayoutLoader(config_path=tmp_path)
            mappings = loader.get_field_mappings()

            assert mappings == {}
        finally:
            os.unlink(tmp_path)

    def test_get_context_provider_returns_provider(self):
        config_content = """
context_provider = "my_provider"

[layouts.test_layout]
name = "Test Layout"

[[layouts.test_layout.lines]]
field = "field1"
index = 0
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".toml", delete=False) as tmp:
            tmp.write(config_content)
            tmp_path = tmp.name

        try:
            loader = LayoutLoader(config_path=tmp_path)
            provider = loader.get_context_provider()

            assert provider == "my_provider"
        finally:
            os.unlink(tmp_path)

    def test_get_context_provider_no_provider_returns_none(self):
        config_content = """
[layouts.test_layout]
name = "Test Layout"

[[layouts.test_layout.lines]]
field = "field1"
index = 0
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".toml", delete=False) as tmp:
            tmp.write(config_content)
            tmp_path = tmp.name

        try:
            loader = LayoutLoader(config_path=tmp_path)
            provider = loader.get_context_provider()

            assert provider is None
        finally:
            os.unlink(tmp_path)

    def test_load_config_with_multiple_layouts(self):
        config_content = """
[layouts.layout1]
name = "Layout 1"

[[layouts.layout1.lines]]
field = "field1"
index = 0

[[layouts.layout1.lines]]
field = "field2"
index = 1

[layouts.layout2]
name = "Layout 2"

[[layouts.layout2.lines]]
field = "field3"
index = 0
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".toml", delete=False) as tmp:
            tmp.write(config_content)
            tmp_path = tmp.name

        try:
            loader = LayoutLoader(config_path=tmp_path)
            config = loader.load()

            assert "layout1" in config.layouts
            assert "layout2" in config.layouts
            assert len(config.layouts["layout1"].lines) == 2
            assert len(config.layouts["layout2"].lines) == 1
        finally:
            os.unlink(tmp_path)

    def test_auto_loads_config_if_not_loaded(self):
        config_content = """
[layouts.test_layout]
name = "Test Layout"

[[layouts.test_layout.lines]]
field = "field1"
index = 0
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".toml", delete=False) as tmp:
            tmp.write(config_content)
            tmp_path = tmp.name

        try:
            loader = LayoutLoader(config_path=tmp_path)
            layout = loader.get_layout("test_layout")

            assert layout["name"] == "Test Layout"
        finally:
            os.unlink(tmp_path)

    def test_load_from_separate_formatters_file(self):
        layouts_content = """
[layouts.test_layout]
name = "Test Layout"

[[layouts.test_layout.lines]]
field = "field1"
index = 0
formatter = "price_usd"
"""
        formatters_content = """
[formatters.price_usd]
type = "price"
symbol = "$"
decimals = 2
"""
        tmp_layouts = tempfile.NamedTemporaryFile(
            mode="w", suffix=".toml", delete=False, encoding="utf-8"
        )
        tmp_layouts.write(layouts_content)
        tmp_layouts.close()
        layouts_path = tmp_layouts.name

        tmp_formatters = tempfile.NamedTemporaryFile(
            mode="w", suffix=".toml", delete=False, encoding="utf-8"
        )
        tmp_formatters.write(formatters_content)
        tmp_formatters.close()
        formatters_path = tmp_formatters.name

        try:
            loader = LayoutLoader(
                config_path=layouts_path, formatters_path=formatters_path
            )
            config = loader.load()

            assert config.formatters is not None
            assert "price_usd" in config.formatters
            assert config.formatters["price_usd"].symbol == "$"
        finally:
            os.unlink(layouts_path)
            os.unlink(formatters_path)

    def test_load_from_separate_fields_file(self):
        layouts_content = """
[layouts.test_layout]
name = "Test Layout"

[[layouts.test_layout.lines]]
field = "temperature"
index = 0
"""
        fields_content = """
[fields.temperature]
context_key = "temp"
default = 0
"""
        tmp_layouts = tempfile.NamedTemporaryFile(
            mode="w", suffix=".toml", delete=False, encoding="utf-8"
        )
        tmp_layouts.write(layouts_content)
        tmp_layouts.close()
        layouts_path = tmp_layouts.name

        tmp_fields = tempfile.NamedTemporaryFile(
            mode="w", suffix=".toml", delete=False, encoding="utf-8"
        )
        tmp_fields.write(fields_content)
        tmp_fields.close()
        fields_path = tmp_fields.name

        try:
            loader = LayoutLoader(config_path=layouts_path, fields_path=fields_path)
            config = loader.load()

            assert config.fields is not None
            assert "temperature" in config.fields
            assert config.fields["temperature"].context_key == "temp"
        finally:
            os.unlink(layouts_path)
            os.unlink(fields_path)

    def test_load_from_all_separate_files(self):
        layouts_content = """
[layouts.test_layout]
name = "Test Layout"

[[layouts.test_layout.lines]]
field = "temperature"
index = 0
formatter = "number_fmt"
"""
        formatters_content = """
[formatters.number_fmt]
type = "number"
decimals = 1
"""
        fields_content = """
[fields.temperature]
context_key = "temp"
default = 0
"""
        tmp_layouts = tempfile.NamedTemporaryFile(
            mode="w", suffix=".toml", delete=False, encoding="utf-8"
        )
        tmp_layouts.write(layouts_content)
        tmp_layouts.close()
        layouts_path = tmp_layouts.name

        tmp_formatters = tempfile.NamedTemporaryFile(
            mode="w", suffix=".toml", delete=False, encoding="utf-8"
        )
        tmp_formatters.write(formatters_content)
        tmp_formatters.close()
        formatters_path = tmp_formatters.name

        tmp_fields = tempfile.NamedTemporaryFile(
            mode="w", suffix=".toml", delete=False, encoding="utf-8"
        )
        tmp_fields.write(fields_content)
        tmp_fields.close()
        fields_path = tmp_fields.name

        try:
            loader = LayoutLoader(
                config_path=layouts_path,
                formatters_path=formatters_path,
                fields_path=fields_path,
            )
            config = loader.load()

            assert config.formatters is not None
            assert "number_fmt" in config.formatters
            assert config.fields is not None
            assert "temperature" in config.fields
            assert "test_layout" in config.layouts
        finally:
            os.unlink(layouts_path)
            os.unlink(formatters_path)
            os.unlink(fields_path)

    def test_load_from_files_static_method(self):
        layouts_content = """
[layouts.test_layout]
name = "Test Layout"

[[layouts.test_layout.lines]]
field = "field1"
index = 0
"""
        formatters_content = """
[formatters.price_usd]
type = "price"
symbol = "$"
"""
        tmp_layouts = tempfile.NamedTemporaryFile(
            mode="w", suffix=".toml", delete=False, encoding="utf-8"
        )
        tmp_layouts.write(layouts_content)
        tmp_layouts.close()
        layouts_path = tmp_layouts.name

        tmp_formatters = tempfile.NamedTemporaryFile(
            mode="w", suffix=".toml", delete=False, encoding="utf-8"
        )
        tmp_formatters.write(formatters_content)
        tmp_formatters.close()
        formatters_path = tmp_formatters.name

        try:
            config = LayoutLoader.load_from_files(
                layouts_path=layouts_path, formatters_path=formatters_path
            )

            assert "test_layout" in config.layouts
            assert config.formatters is not None
            assert "price_usd" in config.formatters
        finally:
            os.unlink(layouts_path)
            os.unlink(formatters_path)

    def test_separate_file_overrides_base_config(self):
        layouts_content = """
[formatters.price_usd]
type = "price"
symbol = "£"

[layouts.test_layout]
name = "Test Layout"

[[layouts.test_layout.lines]]
field = "field1"
index = 0
"""
        formatters_content = """
[formatters.price_usd]
type = "price"
symbol = "$"
decimals = 2
"""
        tmp_layouts = tempfile.NamedTemporaryFile(
            mode="w", suffix=".toml", delete=False, encoding="utf-8"
        )
        tmp_layouts.write(layouts_content)
        tmp_layouts.close()
        layouts_path = tmp_layouts.name

        tmp_formatters = tempfile.NamedTemporaryFile(
            mode="w", suffix=".toml", delete=False, encoding="utf-8"
        )
        tmp_formatters.write(formatters_content)
        tmp_formatters.close()
        formatters_path = tmp_formatters.name

        try:
            loader = LayoutLoader(
                config_path=layouts_path, formatters_path=formatters_path
            )
            config = loader.load()

            assert config.formatters is not None
            assert config.formatters["price_usd"].symbol == "$"
            assert config.formatters["price_usd"].decimals == 2
        finally:
            os.unlink(layouts_path)
            os.unlink(formatters_path)

    def test_load_computed_field_celsius_to_fahrenheit(self):
        config_content = """
[layouts.test]
name = "Test"

[[layouts.test.lines]]
field = "field1"
index = 0

[fields.temp_f]
operation = "celsius_to_fahrenheit"
sources = ["temp_c"]
default = 0.0
"""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".toml", delete=False, encoding="utf-8"
        ) as tmp:
            tmp.write(config_content)
            tmp_path = tmp.name

        try:
            loader = LayoutLoader(config_path=tmp_path)
            mappings = loader.get_field_mappings()

            assert "temp_f" in mappings
            assert mappings["temp_f"].operation == "celsius_to_fahrenheit"
            assert mappings["temp_f"].sources == ["temp_c"]
            assert mappings["temp_f"].default == 0.0
        finally:
            os.unlink(tmp_path)

    def test_load_computed_field_multiply(self):
        config_content = """
[layouts.test]
name = "Test"

[[layouts.test.lines]]
field = "field1"
index = 0

[fields.total_price]
operation = "multiply"
sources = ["price", "quantity"]
default = 0.0
"""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".toml", delete=False, encoding="utf-8"
        ) as tmp:
            tmp.write(config_content)
            tmp_path = tmp.name

        try:
            loader = LayoutLoader(config_path=tmp_path)
            mappings = loader.get_field_mappings()

            assert "total_price" in mappings
            assert mappings["total_price"].operation == "multiply"
            assert mappings["total_price"].sources == ["price", "quantity"]
        finally:
            os.unlink(tmp_path)

    def test_load_computed_field_average(self):
        config_content = """
[layouts.test]
name = "Test"

[[layouts.test.lines]]
field = "field1"
index = 0

[fields.avg_score]
operation = "average"
sources = ["score1", "score2", "score3"]
default = 0.0
"""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".toml", delete=False, encoding="utf-8"
        ) as tmp:
            tmp.write(config_content)
            tmp_path = tmp.name

        try:
            loader = LayoutLoader(config_path=tmp_path)
            mappings = loader.get_field_mappings()

            assert "avg_score" in mappings
            assert mappings["avg_score"].operation == "average"
            assert mappings["avg_score"].sources == ["score1", "score2", "score3"]
        finally:
            os.unlink(tmp_path)

    def test_load_computed_field_linear_transform(self):
        config_content = """
[layouts.test]
name = "Test"

[[layouts.test.lines]]
field = "field1"
index = 0

[fields.scaled_value]
operation = "linear_transform"
sources = ["value"]
multiply = 2.5
add = 10
default = 0.0
"""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".toml", delete=False, encoding="utf-8"
        ) as tmp:
            tmp.write(config_content)
            tmp_path = tmp.name

        try:
            loader = LayoutLoader(config_path=tmp_path)
            mappings = loader.get_field_mappings()

            assert "scaled_value" in mappings
            assert mappings["scaled_value"].operation == "linear_transform"
            assert mappings["scaled_value"].sources == ["value"]
            assert mappings["scaled_value"].multiply == 2.5
            assert mappings["scaled_value"].add == 10
        finally:
            os.unlink(tmp_path)
