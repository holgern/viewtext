Quickstart Guide
================

This guide will help you get started with ViewText quickly.

Installation
------------

ViewText is available as a standalone PyPI package called ``viewtext``:

.. code-block:: bash

    pip install viewtext

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

Computed Fields
---------------

You can perform calculations on your data directly in TOML configuration:

.. code-block:: toml

    [fields.temperature_f]
    operation = "celsius_to_fahrenheit"
    sources = ["temp_c"]
    default = 0.0

    [fields.total_price]
    operation = "multiply"
    sources = ["price", "quantity"]
    default = 0.0

    [fields.average_score]
    operation = "average"
    sources = ["score1", "score2", "score3"]

Available Operations
~~~~~~~~~~~~~~~~~~~~

- **Temperature**: ``celsius_to_fahrenheit``, ``fahrenheit_to_celsius``
- **Arithmetic**: ``multiply``, ``divide``, ``add``, ``subtract``
- **Aggregates**: ``average``, ``min``, ``max``
- **Transforms**: ``abs``, ``round``, ``linear_transform``

Example with Layout
~~~~~~~~~~~~~~~~~~~

.. code-block:: toml

    # fields.toml
    [fields.temp_f]
    operation = "celsius_to_fahrenheit"
    sources = ["temp_c"]
    default = 32.0

    # layouts.toml
    [layouts.weather]
    name = "Weather"

    [[layouts.weather.lines]]
    field = "temp_f"
    index = 0
    formatter = "number"

    [layouts.weather.lines.formatter_params]
    decimals = 1
    suffix = "°F"

.. code-block:: python

    from viewtext import LayoutEngine, LayoutLoader, RegistryBuilder

    loader = LayoutLoader("layouts.toml", fields_path="fields.toml")
    layout = loader.get_layout("weather")

    registry = RegistryBuilder.build_from_config(loader=loader)
    engine = LayoutEngine(field_registry=registry)

    lines = engine.build_line_str(layout, {"temp_c": 25})
    print(lines[0])

Output: ``77.0°F``

See ``examples/computed_fields.toml`` and ``examples/README_computed_fields.md`` for more examples.

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
