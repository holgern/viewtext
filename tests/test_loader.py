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
