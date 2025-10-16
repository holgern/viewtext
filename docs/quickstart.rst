Quickstart Guide
================

This guide will help you get started with ViewText quickly.

Installation
------------

Currently, ViewText is embedded within projects. In the future, it will be available as
a standalone PyPI package.

Basic Concepts
--------------

ViewText works with three main components:

1. **Field Registry**: Registers functions that extract data from context
2. **Layout Configuration**: TOML files that define how fields map to grid positions
3. **Layout Engine**: Builds formatted text output from layouts and context data

Simple Example
--------------

Step 1: Create a Field Registry
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    from viewtext import BaseFieldRegistry

    registry = BaseFieldRegistry()

    # Register simple field getters
    registry.register("temperature", lambda ctx: ctx["temp"])
    registry.register("humidity", lambda ctx: ctx["humidity"])
    registry.register("location", lambda ctx: ctx.get("city", "Unknown"))

Step 2: Create a Layout Configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Create a file named ``layouts.toml``:

.. code-block:: toml

    [layouts.weather]
    name = "Weather Display"

    [[layouts.weather.lines]]
    field = "location"
    index = 0
    formatter = "text_uppercase"

    [[layouts.weather.lines]]
    field = "temperature"
    index = 1
    formatter = "number"

    [layouts.weather.lines.formatter_params]
    suffix = "°F"
    decimals = 1

    [[layouts.weather.lines]]
    field = "humidity"
    index = 2
    formatter = "number"

    [layouts.weather.lines.formatter_params]
    suffix = "%"
    decimals = 0

Step 3: Build the Layout
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    from viewtext import LayoutEngine, LayoutLoader

    # Load the layout
    loader = LayoutLoader("layouts.toml")
    layout = loader.get_layout("weather")

    # Create the engine
    engine = LayoutEngine(field_registry=registry)

    # Build the output
    context = {
        "temp": 72.5,
        "humidity": 65,
        "city": "San Francisco"
    }

    lines = engine.build_line_str(layout, context)

    # Print the result
    for line in lines:
        print(line)

Output:

.. code-block:: text

    SAN FRANCISCO
    72.5°F
    65%

Using Built-in Formatters
--------------------------

ViewText includes several built-in formatters:

Text Formatters
~~~~~~~~~~~~~~~

.. code-block:: python

    # text - Basic text with prefix/suffix
    # text_uppercase - Uppercase text

Number Formatters
~~~~~~~~~~~~~~~~~

.. code-block:: python

    # number - Format numbers with decimals and separators
    # price - Format prices with currency symbols

Date/Time Formatters
~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    # datetime - Format timestamps and datetime objects
    # relative_time - Format as relative time (e.g., "5m ago")

Next Steps
----------

- Learn more about :doc:`user_guide`
- Explore :doc:`api_reference`
- See more :doc:`examples`
