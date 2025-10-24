Quickstart Guide
================

This guide walks through the fastest way to render your first ViewText layout using the latest input mapping system.

Installation
------------

ViewText is published on PyPI. Install it with your preferred package manager:

.. code-block:: bash

    uv pip install viewtext

    # or
    pip install viewtext

Basic Concepts
--------------

ViewText combines three core building blocks:

1. **Input mappings** describe how values are pulled from context data or computed.
2. **Layout configurations** assign inputs to line or dictionary positions with optional formatters and presenters.
3. **LayoutEngine** renders formatted output using the configured mappings and formatters.

Simple Example
--------------

Step 1: Define Inputs
~~~~~~~~~~~~~~~~~~~~~

Create ``inputs.toml`` with the inputs your layout will reference.

.. code-block:: toml

    [inputs.temperature]
    context_key = "temp"

    [inputs.humidity]
    context_key = "humidity"

    [inputs.location]
    context_key = "city"
    default = "Unknown"

Step 2: Define a Layout
~~~~~~~~~~~~~~~~~~~~~~~

Create ``layouts.toml`` that maps inputs to specific line positions.

.. code-block:: toml

    [layouts.weather]
    name = "Weather Display"

    [[layouts.weather.lines]]
    input = "location"
    index = 0
    formatter = "text_uppercase"

    [[layouts.weather.lines]]
    input = "temperature"
    index = 1
    formatter = "number"

    [layouts.weather.lines.formatter_params]
    suffix = "°F"
    decimals = 1

    [[layouts.weather.lines]]
    input = "humidity"
    index = 2
    formatter = "number"

    [layouts.weather.lines.formatter_params]
    suffix = "%"
    decimals = 0

Step 3: Render the Layout
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    from viewtext import LayoutEngine, LayoutLoader, RegistryBuilder

    loader = LayoutLoader(["layouts.toml", "inputs.toml"])
    layout = loader.get_layout("weather")

    registry = RegistryBuilder.build_from_config(loader=loader)
    engine = LayoutEngine(field_registry=registry, layout_loader=loader)

    context = {
        "temp": 72.5,
        "humidity": 65,
        "city": "San Francisco",
    }

    lines = engine.build_line_str(layout, context)

    for line in lines:
        print(line)

Output:

.. code-block:: text

    SAN FRANCISCO
    72.5°F
    65%

Computed Inputs
---------------

Inputs can perform calculations without Python code by using ``operation`` and ``sources`` parameters.

.. code-block:: toml

    [inputs.temperature_f]
    operation = "celsius_to_fahrenheit"
    sources = ["temp_c"]
    default = 32.0

    [inputs.total_price]
    operation = "multiply"
    sources = ["price", "quantity"]
    default = 0.0

Use them directly in layouts:

.. code-block:: toml

    [[layouts.weather.lines]]
    input = "temperature_f"
    index = 0
    formatter = "number"

    [layouts.weather.lines.formatter_params]
    decimals = 1
    suffix = "°F"

Formatting Output
-----------------

Add built-in formatters or presets to control presentation.

.. code-block:: toml

    [formatters.usd]
    type = "price"
    symbol = "$"
    decimals = 2

    [[layouts.product.lines]]
    input = "line_total"
    index = 0
    formatter = "usd"

See :doc:`formatters_reference` for a complete parameter list.

Advanced: Python Field Registry
-------------------------------

For dynamic logic that is easier to express in Python, register getters directly with ``BaseFieldRegistry`` and pass the registry to ``LayoutEngine``. Input mappings and the field registry can be mixed freely.

.. code-block:: python

    from viewtext import BaseFieldRegistry, LayoutEngine

    registry = BaseFieldRegistry()
    registry.register("temperature", lambda ctx: ctx["temp"])  # Python getter

    engine = LayoutEngine(field_registry=registry)
    layout = {"lines": [{"input": "temperature", "index": 0}]}
    print(engine.build_line_str(layout, {"temp": 21.5})[0])

Next Steps
----------

- Dive into :doc:`user_guide` for a deeper explanation of presenters, formatters, and validation.
- Browse :doc:`examples` to see real-world configurations.
- Explore :doc:`inputs_reference` and :doc:`computed_fields_reference` for exhaustive parameter details.
