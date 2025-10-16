User Guide
==========

This guide covers the core concepts and features of ViewText in detail.

Field Registry
--------------

The Field Registry is the foundation of ViewText. It maps field names to getter functions
that extract values from context dictionaries.

Creating a Registry
~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    from viewtext import BaseFieldRegistry

    registry = BaseFieldRegistry()

Registering Fields
~~~~~~~~~~~~~~~~~~

Fields are registered with a name and a callable that takes a context dictionary:

.. code-block:: python

    # Simple field getter
    registry.register("username", lambda ctx: ctx["user"]["name"])

    # More complex getter with default values
    registry.register("status", lambda ctx: ctx.get("status", "offline"))

    # Computed fields
    registry.register("full_name", lambda ctx: f"{ctx['first']} {ctx['last']}")

Checking for Fields
~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    if registry.has_field("username"):
        getter = registry.get("username")
        value = getter(context)

Formatter System
----------------

Formatters transform raw values into formatted strings. ViewText includes several built-in
formatters and supports custom formatters.

Built-in Formatters
~~~~~~~~~~~~~~~~~~~

**text**

Basic text formatting with optional prefix and suffix:

.. code-block:: python

    formatter_params:
        prefix: "Value: "
        suffix: " units"

**text_uppercase**

Converts text to uppercase:

.. code-block:: text

    "hello" → "HELLO"

**number**

Format numbers with precision and separators:

.. code-block:: yaml

    formatter_params:
        decimals: 2
        thousands_sep: ","
        prefix: "$"
        suffix: " USD"

.. code-block:: text

    1234.567 → "$1,234.57 USD"

**price**

Specialized price formatting:

.. code-block:: yaml

    formatter_params:
        symbol: "$"
        symbol_position: "prefix"  # or "suffix"
        decimals: 2
        thousands_sep: ","

.. code-block:: text

    1234.50 → "$1,234.50"

**datetime**

Format timestamps and datetime objects:

.. code-block:: yaml

    formatter_params:
        format: "%Y-%m-%d %H:%M:%S"

.. code-block:: text

    1234567890 → "2009-02-13 23:31:30"

**relative_time**

Format time differences in human-readable format:

.. code-block:: yaml

    formatter_params:
        format: "short"  # or "long"

.. code-block:: text

    300 → "5m ago"  # short format
    300 → "5 minutes ago"  # long format

**template**

Combine multiple fields using a template string with Python format specifications:

.. code-block:: yaml

    formatter_params:
        template: "{symbol} - ${price:.2f} - {volume}/$"
        fields: ["symbol", "price", "volume"]

.. code-block:: text

    # With context: {"symbol": "BTC", "price": 45234.567, "volume": "1.2M"}
    "BTC - $45234.57 - 1.2M/$"

The template formatter supports:

- Nested field access via dot notation (e.g., ``current_price.usd``)
- Python format specifications (e.g., ``.2f`` for 2 decimal places)
- Multiple fields combined in a single line

Custom Formatters
~~~~~~~~~~~~~~~~~

You can register custom formatters with the FormatterRegistry:

.. code-block:: python

    from viewtext import get_formatter_registry

    def format_percentage(value, **kwargs):
        decimals = kwargs.get("decimals", 1)
        return f"{value:.{decimals}f}%"

    formatter_registry = get_formatter_registry()
    formatter_registry.register("percentage", format_percentage)

Layout Configuration
--------------------

Layouts are defined in TOML files and specify how fields map to output lines.

Basic Layout Structure
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: toml

    [layouts.my_layout]
    name = "My Layout"

    [[layouts.my_layout.lines]]
    field = "field_name"
    index = 0
    formatter = "text"

    [layouts.my_layout.lines.formatter_params]
    prefix = "Label: "

Multiple Layouts
~~~~~~~~~~~~~~~~

A single TOML file can contain multiple layouts:

.. code-block:: toml

    [layouts.compact]
    name = "Compact View"
    # ... lines ...

    [layouts.detailed]
    name = "Detailed View"
    # ... lines ...

Formatter Parameters
~~~~~~~~~~~~~~~~~~~~

Each line can have formatter-specific parameters:

.. code-block:: toml

    [[layouts.demo.lines]]
    field = "price"
    index = 0
    formatter = "price"

    [layouts.demo.lines.formatter_params]
    symbol = "$"
    decimals = 2
    thousands_sep = ","
    symbol_position = "prefix"

Global Formatter Configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Define reusable formatter configurations:

.. code-block:: toml

    [formatters.usd_price]
    type = "price"
    symbol = "$"
    decimals = 2
    thousands_sep = ","

    [layouts.product]
    name = "Product Display"

    [[layouts.product.lines]]
    field = "price"
    index = 0
    formatter = "usd_price"

Layout Engine
-------------

The Layout Engine combines field registries, formatters, and layout configurations to
generate formatted output.

Creating an Engine
~~~~~~~~~~~~~~~~~~

.. code-block:: python

    from viewtext import LayoutEngine

    # Without field registry (uses context directly)
    engine = LayoutEngine()

    # With field registry
    engine = LayoutEngine(field_registry=registry)

Building Output
~~~~~~~~~~~~~~~

.. code-block:: python

    context = {
        "temp": 72.5,
        "humidity": 65,
        "city": "San Francisco"
    }

    lines = engine.build_line_str(layout, context)

    # lines is a list of strings, one per line
    for i, line in enumerate(lines):
        print(f"Line {i}: {line}")

Field Resolution
~~~~~~~~~~~~~~~~

The engine resolves fields in this order:

1. Check field registry (if provided)
2. Check context dictionary directly
3. Return None if not found

This allows mixing registered fields with direct context values.

Computed Fields
---------------

Computed fields allow you to perform calculations on source data without writing Python code.
All operations are defined in TOML configuration files and are compiled at load time.

Available Operations
~~~~~~~~~~~~~~~~~~~~

**Temperature Conversions**

- ``celsius_to_fahrenheit`` - Convert Celsius to Fahrenheit
- ``fahrenheit_to_celsius`` - Convert Fahrenheit to Celsius

**Arithmetic Operations**

- ``multiply`` - Multiply two or more values
- ``divide`` - Divide two values (safe with divide-by-zero handling)
- ``add`` - Sum multiple values
- ``subtract`` - Subtract two values
- ``modulo`` - Modulo operation (remainder after division)

**Aggregate Operations**

- ``average`` - Calculate average of multiple values
- ``min`` - Find minimum of multiple values
- ``max`` - Find maximum of multiple values

**Mathematical Operations**

- ``abs`` - Absolute value
- ``round`` - Round to nearest integer (optionally specify decimals)
- ``ceil`` - Round up to nearest integer
- ``floor`` - Round down to nearest integer
- ``linear_transform`` - Apply formula: ``(value * multiply / divide) + add``

**String Operations**

- ``concat`` - Join multiple strings with a separator
- ``split`` - Split a string by separator and take a specific index
- ``substring`` - Extract substring from start to end position

**Conditional Operations**

- ``conditional`` - Return different values based on field equality condition (``condition``, ``if_true``, ``if_false``)

Defining Computed Fields
~~~~~~~~~~~~~~~~~~~~~~~~~

Computed fields are defined in the ``[fields]`` section of your TOML configuration:

.. code-block:: toml

    # Temperature conversion
    [fields.temp_f]
    operation = "celsius_to_fahrenheit"
    sources = ["temp_c"]
    default = 0.0

    # Price calculation
    [fields.total_price]
    operation = "multiply"
    sources = ["price", "quantity"]
    default = 0.0

    # Discount calculation
    [fields.discount_price]
    operation = "linear_transform"
    sources = ["price"]
    multiply = 0.8
    default = 0.0

    # Average score
    [fields.average_score]
    operation = "average"
    sources = ["score1", "score2", "score3"]
    default = 0.0

Operation Parameters
~~~~~~~~~~~~~~~~~~~~

Each computed field requires:

- ``operation`` - Name of the operation to perform
- ``sources`` - List of field names from context to use as inputs
- ``default`` - Value to return if operation fails or sources are missing

Some operations support additional parameters:

**Linear Transform Parameters**

- ``multiply`` - Multiplier for the value (default: 1)
- ``divide`` - Divisor for the value (default: 1)
- ``add`` - Addend for the value (default: 0)

Formula: ``(value * multiply / divide) + add``

.. code-block:: toml

    # Convert km/h to mph
    [fields.speed_mph]
    operation = "linear_transform"
    sources = ["speed_kmh"]
    multiply = 0.621371
    default = 0.0

    # Apply 20% discount and add $5 handling fee
    [fields.discounted_price]
    operation = "linear_transform"
    sources = ["price"]
    multiply = 0.8
    add = 5.0
    default = 0.0

**Round Operations**

.. code-block:: toml

    # Scale mempool size and round up
    [fields.vsize_scaled]
    operation = "linear_transform"
    context_key = "mempool.vsize"
    divide = 1000000
    default = 0

    [fields.vsize_mb]
    operation = "ceil"
    sources = ["vsize_scaled"]
    default = 0

**String Operations Parameters**

- ``separator`` - Separator for concat/split operations (default: empty string for concat, space for split)
- ``index`` - Index for split operation (which part to extract)
- ``start`` - Start position for substring operation
- ``end`` - End position for substring operation (optional)

.. code-block:: toml

    # Concatenate first and last name
    [fields.full_name]
    operation = "concat"
    sources = ["first_name", "last_name"]
    separator = " "
    default = ""

    # Extract domain from email
    [fields.domain]
    operation = "split"
    sources = ["email"]
    separator = "@"
    index = 1
    default = ""

    # Extract year from date string
    [fields.year]
    operation = "substring"
    sources = ["date"]
    start = 0
    end = 4
    default = ""

    # Get last 3 characters
    [fields.suffix]
    operation = "substring"
    sources = ["text"]
    start = -3
    default = ""

**Modulo Operation**

.. code-block:: toml

    # Check if number is even/odd (result will be 0 or 1)
    [fields.remainder]
    operation = "modulo"
    sources = ["number", "divisor"]
    default = 0

**Conditional Operations**

.. code-block:: toml

    # Display price with currency formatting
    [fields.price_display]
    operation = "conditional"
    condition = { field = "currency", equals = "USD" }
    if_true = "$~amount~"
    if_false = "~amount~ ~currency~"
    default = ""

The ``~field_name~`` syntax in ``if_true`` and ``if_false`` allows embedding other field values.

Error Handling
~~~~~~~~~~~~~~

Computed fields include automatic error handling:

- Missing source values return the default
- Non-numeric values return the default (for numeric operations)
- Division by zero returns the default
- Modulo by zero returns the default
- Out-of-bounds string indices return the default
- Invalid operations raise ``ValueError`` at configuration load time

Example Use Cases
~~~~~~~~~~~~~~~~~

**Unit Conversions**

.. code-block:: toml

    [fields.temp_f]
    operation = "celsius_to_fahrenheit"
    sources = ["temp_c"]
    default = 0.0

    [fields.meters_to_feet]
    operation = "linear_transform"
    sources = ["meters"]
    multiply = 3.28084
    default = 0.0

**E-commerce Calculations**

.. code-block:: toml

    # Line item total
    [fields.line_total]
    operation = "multiply"
    sources = ["price", "quantity"]
    default = 0.0

    # Discounted price
    [fields.sale_price]
    operation = "linear_transform"
    sources = ["price"]
    multiply = 0.85
    default = 0.0

**Data Aggregation**

.. code-block:: toml

    # Daily temperature range
    [fields.temp_min]
    operation = "min"
    sources = ["temp_morning", "temp_noon", "temp_evening"]
    default = 0.0

    [fields.temp_max]
    operation = "max"
    sources = ["temp_morning", "temp_noon", "temp_evening"]
    default = 0.0

    [fields.temp_avg]
    operation = "average"
    sources = ["temp_morning", "temp_noon", "temp_evening"]
    default = 0.0

Benefits
~~~~~~~~

1. **Declarative** - Define calculations in configuration, not code
2. **Reusable** - Same operations work across different layouts
3. **Safe** - Built-in error handling prevents crashes
4. **Maintainable** - Easy to understand and modify
5. **Fast** - Compiled at configuration load time

See ``examples/computed_fields.toml`` and ``examples/demo_computed_fields.py`` for complete examples.

Layout Loader
-------------

The LayoutLoader handles loading and parsing TOML configuration files.

Loading Layouts
~~~~~~~~~~~~~~~

.. code-block:: python

    from viewtext import LayoutLoader

    # Load from specific file
    loader = LayoutLoader("config/layouts.toml")

    # Load from default location (./layouts.toml)
    loader = LayoutLoader()

    # Get a specific layout
    layout = loader.get_layout("weather")

Split Configuration Files
~~~~~~~~~~~~~~~~~~~~~~~~~~

For large projects, you can split your configuration into separate files for better
organization and maintainability:

.. code-block:: python

    from viewtext import LayoutLoader

    # Method 1: Using constructor parameters
    loader = LayoutLoader(
        config_path="layouts.toml",
        formatters_path="formatters.toml",
        fields_path="fields.toml"
    )
    config = loader.load()

    # Method 2: Using static method
    config = LayoutLoader.load_from_files(
        layouts_path="layouts.toml",
        formatters_path="formatters.toml",
        fields_path="fields.toml"
    )

**Example: Separate Formatters File**

``formatters.toml``:

.. code-block:: toml

    [formatters.price_usd]
    type = "price"
    symbol = "$"
    decimals = 2

    [formatters.price_eur]
    type = "price"
    symbol = "€"
    decimals = 2

``layouts.toml``:

.. code-block:: toml

    [layouts.product]
    name = "Product Display"

    [[layouts.product.lines]]
    field = "price"
    index = 0
    formatter = "price_usd"

**Example: Separate Fields File**

``fields.toml``:

.. code-block:: toml

    [fields.temperature]
    context_key = "temp"
    default = 0

    [fields.city]
    context_key = "location.city"
    default = "Unknown"

**CLI Usage with Split Files**

.. code-block:: bash

    # Use --formatters and --fields flags
    viewtext --config layouts.toml \\
             --formatters formatters.toml \\
             --fields fields.toml \\
             list

    viewtext -c layouts.toml -f formatters.toml -F fields.toml render weather

**Benefits of Split Files**

1. **Modularity**: Separate concerns into different files
2. **Reusability**: Share formatters and fields across multiple layout files
3. **Team Collaboration**: Different team members can work on different files
4. **Maintainability**: Easier to find and update specific configurations

**Merging Behavior**

When multiple files are provided:

- Fields from ``fields.toml`` are merged into the base configuration
- Formatters from ``formatters.toml`` are merged into the base configuration
- If the same key exists in multiple files, values from separate files take precedence
- All separate files are optional

Getting Formatter Parameters
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    # Get global formatter configuration
    params = loader.get_formatter_params("usd_price")

Error Handling
--------------

ViewText raises specific exceptions for common errors:

.. code-block:: python

    from viewtext import LayoutLoader, BaseFieldRegistry

    # FileNotFoundError
    try:
        loader = LayoutLoader("missing.toml")
        loader.load()
    except FileNotFoundError as e:
        print(f"Config file not found: {e}")

    # ValueError for unknown layout
    try:
        layout = loader.get_layout("nonexistent")
    except ValueError as e:
        print(f"Layout error: {e}")

    # ValueError for unknown field
    registry = BaseFieldRegistry()
    try:
        getter = registry.get("unknown_field")
    except ValueError as e:
        print(f"Field error: {e}")

Best Practices
--------------

1. **Separate concerns**: Keep field logic in the registry, formatting in formatters,
   and layout structure in TOML files

2. **Use meaningful names**: Choose descriptive field and layout names

3. **Provide defaults**: Use `.get()` with defaults in field getters for optional data

4. **Validate data**: Formatters should handle None and invalid values gracefully

5. **Reuse formatters**: Define global formatter configurations for consistency

6. **Test layouts**: Verify layouts with sample data before deployment

Command Line Interface
----------------------

ViewText includes a CLI for inspecting and testing layouts.

Basic Commands
~~~~~~~~~~~~~~

.. code-block:: bash

    # List all available layouts
    viewtext list

    # Show specific layout configuration
    viewtext show weather

    # Show field mappings from config
    viewtext fields

    # Show all available formatters
    viewtext formatters

    # Show all template formatters in layouts
    viewtext templates

    # Render a layout with mock data
    viewtext render weather

    # Show configuration info
    viewtext info

Global Config Option
~~~~~~~~~~~~~~~~~~~~

Use the ``--config`` or ``-c`` option to specify a custom configuration file:

.. code-block:: bash

    # Global option can be placed before any command
    viewtext -c examples/layouts.toml list
    viewtext --config my_layouts.toml show weather
    viewtext -c custom.toml render crypto_ticker

The default config file is ``layouts.toml`` in the current directory.

CLI Output
~~~~~~~~~~

The CLI provides rich formatted output with tables and colors:

.. code-block:: bash

    $ viewtext list

    Configuration File: layouts.toml

    ┌────────────────┬─────────────────────┬───────┐
    │ Layout Name    │ Display Name        │ Lines │
    ├────────────────┼─────────────────────┼───────┤
    │ weather        │ Weather Display     │     6 │
    │ crypto_ticker  │ Crypto Ticker       │     5 │
    └────────────────┴─────────────────────┴───────┘

    Total layouts: 2

**Template Formatters Command**

The ``templates`` command shows all layouts using template formatters:

.. code-block:: bash

    $ viewtext -c examples/demo_template_formatter.toml templates

    Configuration File: examples/demo_template_formatter.toml

    ┌────────────────────────┬──────────────┬─────────────────────────┬──────────────┐
    │ Layout                 │ Field        │ Template                │ Fields Used  │
    ├────────────────────────┼──────────────┼─────────────────────────┼──────────────┤
    │ crypto_composite_price │ current_price│ {fiat} - ${usd} - {sat} │ price.fiat,  │
    │ (Crypto Price Display) │              │                         │ price.usd,   │
    │                        │              │                         │ price.sat    │
    └────────────────────────┴──────────────┴─────────────────────────┴──────────────┘

    Total template formatters: 1

Advanced Usage
--------------

Singleton Pattern
~~~~~~~~~~~~~~~~~

ViewText provides singleton accessors for global instances:

.. code-block:: python

    from viewtext import (
        get_layout_engine,
        get_formatter_registry,
        get_layout_loader
    )

    # These return global singleton instances
    engine = get_layout_engine(field_registry=registry)
    formatters = get_formatter_registry()
    loader = get_layout_loader("layouts.toml")

Dynamic Layouts
~~~~~~~~~~~~~~~

Build layouts dynamically from data:

.. code-block:: python

    def create_dynamic_layout(fields):
        layout = {
            "name": "Dynamic Layout",
            "lines": []
        }

        for i, field in enumerate(fields):
            layout["lines"].append({
                "field": field,
                "index": i,
                "formatter": "text"
            })

        return layout

    # Use the dynamic layout
    layout = create_dynamic_layout(["temp", "humidity", "pressure"])
    lines = engine.build_line_str(layout, context)

Context Factories
~~~~~~~~~~~~~~~~~

Create reusable context builders:

.. code-block:: python

    class WeatherContext:
        def __init__(self, api_data):
            self.data = api_data

        def to_context(self):
            return {
                "temp": self.data["main"]["temp"],
                "humidity": self.data["main"]["humidity"],
                "city": self.data["name"],
                "timestamp": self.data["dt"]
            }

    weather = WeatherContext(api_response)
    lines = engine.build_line_str(layout, weather.to_context())
