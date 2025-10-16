Testing Guide
=============

This guide explains how to write tests for your viewtext use cases using pytest.

Testing with TOML Configurations
---------------------------------

There are two main approaches for testing viewtext with TOML configurations:

Approach 1: Temporary TOML Files
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This approach is recommended for isolated unit tests. Create temporary TOML files
within your test functions:

.. code-block:: python

    import os
    import tempfile
    import pytest
    from viewtext.loader import LayoutLoader
    from viewtext.engine import LayoutEngine
    from viewtext.registry import BaseFieldRegistry

    def test_my_use_case():
        # 1. Create TOML content as a string
        config_content = """
    [layouts.my_layout]
    name = "My Use Case Layout"

    [[layouts.my_layout.lines]]
    field = "temperature"
    index = 0
    formatter = "number"

    [layouts.my_layout.lines.formatter_params]
    decimals = 1
    suffix = "°C"
    """

        # 2. Write to temporary file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".toml", delete=False) as tmp:
            tmp.write(config_content)
            tmp_path = tmp.name

        try:
            # 3. Load and test
            loader = LayoutLoader(config_path=tmp_path)
            layout = loader.get_layout("my_layout")

            # Create registry and engine
            registry = BaseFieldRegistry()
            engine = LayoutEngine(field_registry=registry)

            # Create test context
            context = {"temperature": 23.456}

            # Build and assert
            result = engine.build_line_str(layout, context)
            assert result == ["23.5°C"]

        finally:
            # 4. Cleanup
            os.unlink(tmp_path)

Approach 2: Existing TOML Files
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This approach is better for integration tests that use actual configuration files:

.. code-block:: python

    from viewtext.loader import LayoutLoader
    from viewtext.engine import LayoutEngine
    from viewtext.registry import BaseFieldRegistry

    def test_with_existing_toml():
        # Point to actual TOML file in your project
        loader = LayoutLoader(config_path="examples/layouts.toml")
        layout = loader.get_layout("demo")

        registry = BaseFieldRegistry()
        engine = LayoutEngine(field_registry=registry)

        context = {
            "demo1": "Line 1",
            "demo2": "Line 2",
            "demo3": "Line 3",
            "demo4": "Line 4"
        }

        result = engine.build_line_str(layout, context)
        assert len(result) == 4
        assert result[0] == "Line 1"

Complete Test Example
---------------------

Here's a complete example testing a weather display use case:

.. code-block:: python

    class TestWeatherDisplay:
        def test_temperature_and_humidity_display(self):
            config_content = """
    [fields.temp]
    context_key = "temperature"

    [fields.humidity]
    context_key = "humidity"

    [formatters.temp_fmt]
    type = "number"
    decimals = 1
    suffix = "°C"

    [formatters.humidity_fmt]
    type = "number"
    decimals = 0
    suffix = "%"

    [layouts.weather]
    name = "Weather Display"

    [[layouts.weather.lines]]
    field = "temp"
    index = 0
    formatter = "temp_fmt"

    [[layouts.weather.lines]]
    field = "humidity"
    index = 1
    formatter = "humidity_fmt"
    """

            with tempfile.NamedTemporaryFile(mode="w", suffix=".toml", delete=False) as tmp:
                tmp.write(config_content)
                tmp_path = tmp.name

            try:
                loader = LayoutLoader(config_path=tmp_path)
                layout = loader.get_layout("weather")

                registry = BaseFieldRegistry()
                engine = LayoutEngine(field_registry=registry)

                context = {"temperature": 23.456, "humidity": 65.7}
                result = engine.build_line_str(layout, context)

                assert result[0] == "23.5°C"
                assert result[1] == "66%"

            finally:
                os.unlink(tmp_path)

Key Testing Patterns
--------------------

When testing viewtext applications, consider these common patterns:

Layout Validation
~~~~~~~~~~~~~~~~~

Test that layouts load correctly from TOML:

.. code-block:: python

    def test_layout_loads_correctly():
        loader = LayoutLoader(config_path="my_config.toml")
        config = loader.load()

        assert "my_layout" in config.layouts
        assert config.layouts["my_layout"].name == "My Layout"
        assert len(config.layouts["my_layout"].lines) == 3

Field Mapping
~~~~~~~~~~~~~

Test that fields resolve correctly from context:

.. code-block:: python

    def test_field_resolution():
        registry = BaseFieldRegistry()

        def temp_getter(ctx):
            return ctx["temperature"]

        registry.register("temp", temp_getter)
        engine = LayoutEngine(field_registry=registry)

        layout_config = {
            "lines": [{"field": "temp", "index": 0}]
        }
        context = {"temperature": 25}

        result = engine.build_line_str(layout_config, context)
        assert result == ["25"]

Formatter Application
~~~~~~~~~~~~~~~~~~~~~

Test that formatters work correctly with parameters from TOML:

.. code-block:: python

    def test_formatter_with_params():
        registry = BaseFieldRegistry()

        def price_getter(ctx):
            return ctx["price"]

        registry.register("price", price_getter)
        engine = LayoutEngine(field_registry=registry)

        layout_config = {
            "lines": [{
                "field": "price",
                "index": 0,
                "formatter": "price",
                "formatter_params": {"symbol": "$", "decimals": 2}
            }]
        }
        context = {"price": 123.45}

        result = engine.build_line_str(layout_config, context)
        assert result == ["$123.45"]

Template Formatter Testing
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Test template formatters that combine multiple fields:

.. code-block:: python

    def test_template_formatter():
        config_content = """
    [fields.first_name]
    context_key = "first_name"

    [fields.last_name]
    context_key = "last_name"

    [fields.age]
    context_key = "age"

    [layouts.profile]
    name = "User Profile"

    [[layouts.profile.lines]]
    field = "full_name"
    index = 0
    formatter = "template"

    [layouts.profile.lines.formatter_params]
    template = "{first_name} {last_name}"

    [[layouts.profile.lines]]
    field = "info"
    index = 1
    formatter = "template"

    [layouts.profile.lines.formatter_params]
    template = "Age: {age}"
    """

        with tempfile.NamedTemporaryFile(mode="w", suffix=".toml", delete=False) as tmp:
            tmp.write(config_content)
            tmp_path = tmp.name

        try:
            loader = LayoutLoader(config_path=tmp_path)
            layout = loader.get_layout("profile")

            registry = BaseFieldRegistry()
            engine = LayoutEngine(field_registry=registry)

            context = {
                "first_name": "John",
                "last_name": "Doe",
                "age": 30
            }

            result = engine.build_line_str(layout, context)

            assert result[0] == "John Doe"
            assert result[1] == "Age: 30"

        finally:
            os.unlink(tmp_path)

    def test_template_with_missing_field():
        """Test that template formatter handles missing fields gracefully."""
        config_content = """
    [layouts.test]
    name = "Test Layout"

    [[layouts.test.lines]]
    field = "greeting"
    index = 0
    formatter = "template"

    [layouts.test.lines.formatter_params]
    template = "Hello, {name}!"
    """

        with tempfile.NamedTemporaryFile(mode="w", suffix=".toml", delete=False) as tmp:
            tmp.write(config_content)
            tmp_path = tmp.name

        try:
            loader = LayoutLoader(config_path=tmp_path)
            layout = loader.get_layout("test")

            registry = BaseFieldRegistry()
            engine = LayoutEngine(field_registry=registry)

            # Context missing the 'name' field
            context = {}

            result = engine.build_line_str(layout, context)

            # Should handle missing field gracefully
            assert "Hello" in result[0]

        finally:
            os.unlink(tmp_path)

    def test_complex_template():
        """Test template with multiple fields and formatting."""
        config_content = """
    [fields.temp]
    context_key = "temperature"

    [fields.humidity]
    context_key = "humidity"

    [fields.location]
    context_key = "location"

    [layouts.weather_report]
    name = "Weather Report"

    [[layouts.weather_report.lines]]
    field = "summary"
    index = 0
    formatter = "template"

    [layouts.weather_report.lines.formatter_params]
    template = "{location}: {temp}°C, {humidity}% humidity"
    """

        with tempfile.NamedTemporaryFile(mode="w", suffix=".toml", delete=False) as tmp:
            tmp.write(config_content)
            tmp_path = tmp.name

        try:
            loader = LayoutLoader(config_path=tmp_path)
            layout = loader.get_layout("weather_report")

            registry = BaseFieldRegistry()
            engine = LayoutEngine(field_registry=registry)

            context = {
                "location": "Berlin",
                "temperature": 22,
                "humidity": 65
            }

            result = engine.build_line_str(layout, context)

            assert result[0] == "Berlin: 22°C, 65% humidity"

        finally:
            os.unlink(tmp_path)

Edge Cases
~~~~~~~~~~

Test edge cases like missing fields, invalid formatters, and empty contexts:

.. code-block:: python

    def test_missing_field_returns_empty():
        registry = BaseFieldRegistry()
        engine = LayoutEngine(field_registry=registry)

        layout_config = {
            "lines": [{"field": "nonexistent", "index": 0}]
        }
        context = {}

        result = engine.build_line_str(layout_config, context)
        assert result == [""]

    def test_unknown_formatter_falls_back_to_text():
        registry = BaseFieldRegistry()

        def value_getter(ctx):
            return ctx["value"]

        registry.register("value", value_getter)
        engine = LayoutEngine(field_registry=registry)

        layout_config = {
            "lines": [{
                "field": "value",
                "index": 0,
                "formatter": "unknown_formatter"
            }]
        }
        context = {"value": "test"}

        result = engine.build_line_str(layout_config, context)
        assert result == ["test"]

Integration Tests
~~~~~~~~~~~~~~~~~

Test the full flow from LayoutLoader → LayoutEngine → output:

.. code-block:: python

    def test_full_integration():
        config_content = """
    [layouts.integration_test]
    name = "Integration Test"

    [[layouts.integration_test.lines]]
    field = "value1"
    index = 0
    formatter = "text"

    [layouts.integration_test.lines.formatter_params]
    prefix = "Value: "

    [[layouts.integration_test.lines]]
    field = "value2"
    index = 1
    formatter = "number"

    [layouts.integration_test.lines.formatter_params]
    thousands_sep = ","
    """

        with tempfile.NamedTemporaryFile(mode="w", suffix=".toml", delete=False) as tmp:
            tmp.write(config_content)
            tmp_path = tmp.name

        try:
            loader = LayoutLoader(config_path=tmp_path)
            layout = loader.get_layout("integration_test")

            registry = BaseFieldRegistry()
            engine = LayoutEngine(field_registry=registry)

            context = {"value1": "test", "value2": 1234567}
            result = engine.build_line_str(layout, context)

            assert result[0] == "Value: test"
            assert result[1] == "1,234,567"

        finally:
            os.unlink(tmp_path)

Running Tests
-------------

To run all tests::

    pytest

To run a specific test file::

    pytest tests/test_my_use_case.py

To run a single test function::

    pytest tests/test_my_use_case.py::TestMyUseCase::test_temperature_display

To run tests with coverage::

    pytest --cov=viewtext --cov-report=term

Best Practices
--------------

1. **Use descriptive test names** that explain what is being tested
2. **Test one thing per test function** to make failures easy to diagnose
3. **Use temporary files for unit tests** to avoid dependencies on external files
4. **Use existing TOML files for integration tests** to test real-world configurations
5. **Clean up temporary files** in the ``finally`` block to avoid leaving artifacts
6. **Test both success and failure cases** including edge cases and error conditions
7. **Use pytest fixtures** for common setup code that's shared across multiple tests

Pytest Fixtures Example
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    import pytest

    @pytest.fixture
    def temp_config_file():
        """Fixture that creates and cleans up a temporary config file."""
        config_content = """
    [layouts.test]
    name = "Test Layout"

    [[layouts.test.lines]]
    field = "value"
    index = 0
    """

        with tempfile.NamedTemporaryFile(mode="w", suffix=".toml", delete=False) as tmp:
            tmp.write(config_content)
            tmp_path = tmp.name

        yield tmp_path

        os.unlink(tmp_path)

    def test_with_fixture(temp_config_file):
        loader = LayoutLoader(config_path=temp_config_file)
        layout = loader.get_layout("test")
        assert layout["name"] == "Test Layout"
