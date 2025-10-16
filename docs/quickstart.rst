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

1. **Field Mappings**: Define how fields map to context data (can be in TOML or Python)
2. **Layout Configuration**: TOML files that define how fields map to grid positions
3. **Layout Engine**: Builds formatted text output from layouts and context data

Simple Example
--------------

Step 1: Create Field Mappings
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Create a file named ``fields.toml``:

.. code-block:: toml

    [fields.temperature]
    context_key = "temp"

    [fields.humidity]
    context_key = "humidity"

    [fields.location]
    context_key = "city"
    default = "Unknown"

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

    # Load the layout and field mappings
    loader = LayoutLoader("layouts.toml", fields_path="fields.toml")
    config = loader.load()
    layout = loader.get_layout("weather")

    # Create the engine with field mappings from config
    engine = LayoutEngine(field_mappings=config.fields)

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

Using Python Field Registry (Advanced)
---------------------------------------

For more complex field logic, you can use Python's ``BaseFieldRegistry`` instead of TOML:

.. code-block:: python

    from viewtext import BaseFieldRegistry

    registry = BaseFieldRegistry()

    # Register custom field getters with complex logic
    registry.register("temperature", lambda ctx: ctx["temp"])
    registry.register("status", lambda ctx: "Hot" if ctx["temp"] > 80 else "Cool")

    # Use the registry with the engine
    engine = LayoutEngine(field_registry=registry)

See the :doc:`user_guide` for more details on when to use each approach.

Next Steps
----------

- Learn more about :doc:`user_guide`
- Explore :doc:`api_reference`
- See more :doc:`examples`
