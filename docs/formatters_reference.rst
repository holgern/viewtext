Formatters Reference
====================

This document provides a complete reference for all formatters available in ViewText.

Overview
--------

Formatters are functions that transform values into formatted strings for display. They are used in layout definitions to control how field values appear in the output. Unlike computed field operations (which transform data), formatters only affect the presentation.

All formatters are registered in the ``FormatterRegistry`` and can be accessed by name in TOML layout configurations.

Common Usage
------------

Formatters are specified in layout line definitions:

.. code-block:: toml

    [[layouts.my_layout.lines]]
    field = "price"
    index = 0
    formatter = "number"

    [layouts.my_layout.lines.formatter_params]
    decimals = 2
    thousands_sep = ","
    prefix = "$"

Built-in Formatters
-------------------

text
~~~~

Basic text formatting with optional prefix and suffix.

**Parameters:**

- ``prefix`` - String to prepend (optional, default: empty string)
- ``suffix`` - String to append (optional, default: empty string)

**Examples:**

.. code-block:: toml

    [[layouts.demo.lines]]
    field = "name"
    index = 0
    formatter = "text"

    [layouts.demo.lines.formatter_params]
    prefix = "Name: "
    suffix = "."

.. code-block:: text

    Input: "Alice"
    Output: "Name: Alice."

.. code-block:: toml

    [[layouts.demo.lines]]
    field = "status"
    index = 1
    formatter = "text"

    [layouts.demo.lines.formatter_params]
    prefix = "["
    suffix = "]"

.. code-block:: text

    Input: "active"
    Output: "[active]"

text_uppercase
~~~~~~~~~~~~~~

Converts text to uppercase.

**Parameters:**

None

**Examples:**

.. code-block:: toml

    [[layouts.demo.lines]]
    field = "city"
    index = 0
    formatter = "text_uppercase"

.. code-block:: text

    Input: "san francisco"
    Output: "SAN FRANCISCO"

.. code-block:: toml

    [[layouts.demo.lines]]
    field = "code"
    index = 1
    formatter = "text_uppercase"

.. code-block:: text

    Input: "abc123"
    Output: "ABC123"

number
~~~~~~

Format numbers with precision, separators, and optional prefix/suffix.

**Parameters:**

- ``decimals`` - Number of decimal places (optional, default: 0)
- ``thousands_sep`` - Thousands separator character (optional, default: empty string)
- ``decimal_sep`` - Decimal separator character (optional, default: ".")
- ``prefix`` - String to prepend (optional, default: empty string)
- ``suffix`` - String to append (optional, default: empty string)

**Examples:**

.. code-block:: toml

    # Basic number formatting
    [[layouts.demo.lines]]
    field = "population"
    index = 0
    formatter = "number"

    [layouts.demo.lines.formatter_params]
    thousands_sep = ","

.. code-block:: text

    Input: 1234567
    Output: "1,234,567"

.. code-block:: toml

    # Temperature with suffix
    [[layouts.demo.lines]]
    field = "temperature"
    index = 1
    formatter = "number"

    [layouts.demo.lines.formatter_params]
    decimals = 1
    suffix = "°C"

.. code-block:: text

    Input: 23.456
    Output: "23.5°C"

.. code-block:: toml

    # European number format
    [[layouts.demo.lines]]
    field = "amount"
    index = 2
    formatter = "number"

    [layouts.demo.lines.formatter_params]
    decimals = 2
    thousands_sep = "."
    decimal_sep = ","

.. code-block:: text

    Input: 1234567.89
    Output: "1.234.567,89"

.. code-block:: toml

    # With prefix and suffix
    [[layouts.demo.lines]]
    field = "value"
    index = 3
    formatter = "number"

    [layouts.demo.lines.formatter_params]
    decimals = 2
    thousands_sep = ","
    prefix = "$"
    suffix = " USD"

.. code-block:: text

    Input: 1234.567
    Output: "$1,234.57 USD"

price
~~~~~

Specialized price formatting with currency symbol positioning.

**Parameters:**

- ``symbol`` - Currency symbol (optional, default: empty string)
- ``symbol_position`` - "prefix" or "suffix" (optional, default: "prefix")
- ``decimals`` - Number of decimal places (optional, default: 2)
- ``thousands_sep`` - Thousands separator character (optional, default: empty string)
- ``decimal_sep`` - Decimal separator character (optional, default: ".")

**Examples:**

.. code-block:: toml

    # US Dollar format
    [[layouts.demo.lines]]
    field = "price"
    index = 0
    formatter = "price"

    [layouts.demo.lines.formatter_params]
    symbol = "$"
    decimals = 2
    thousands_sep = ","

.. code-block:: text

    Input: 1234.50
    Output: "$1,234.50"

.. code-block:: toml

    # Euro with suffix
    [[layouts.demo.lines]]
    field = "price"
    index = 1
    formatter = "price"

    [layouts.demo.lines.formatter_params]
    symbol = "€"
    symbol_position = "suffix"
    decimals = 2

.. code-block:: text

    Input: 1234.56
    Output: "1234.56€"

.. code-block:: toml

    # European Euro format
    [[layouts.demo.lines]]
    field = "price"
    index = 2
    formatter = "price"

    [layouts.demo.lines.formatter_params]
    symbol = "€"
    decimals = 2
    thousands_sep = "."
    decimal_sep = ","

.. code-block:: text

    Input: 1234567.89
    Output: "€1.234.567,89"

.. code-block:: toml

    # Swiss Franc format
    [[layouts.demo.lines]]
    field = "amount"
    index = 3
    formatter = "price"

    [layouts.demo.lines.formatter_params]
    symbol = "CHF"
    symbol_position = "suffix"
    decimals = 2
    thousands_sep = "'"

.. code-block:: text

    Input: 1234567.89
    Output: "1'234'567.89CHF"

datetime
~~~~~~~~

Format timestamps and datetime objects using strftime format strings.

**Parameters:**

- ``format`` - strftime format string (optional, default: "%Y-%m-%d %H:%M:%S")

**Supported Input Types:**

- Python datetime objects
- Unix timestamps (int or float)
- String values (returned as-is)

**Examples:**

.. code-block:: toml

    # Full datetime
    [[layouts.demo.lines]]
    field = "timestamp"
    index = 0
    formatter = "datetime"

    [layouts.demo.lines.formatter_params]
    format = "%Y-%m-%d %H:%M:%S"

.. code-block:: text

    Input: 1234567890 (Unix timestamp)
    Output: "2009-02-13 23:31:30"

.. code-block:: toml

    # Date only
    [[layouts.demo.lines]]
    field = "date"
    index = 1
    formatter = "datetime"

    [layouts.demo.lines.formatter_params]
    format = "%Y-%m-%d"

.. code-block:: text

    Input: datetime(2023, 12, 25, 15, 30)
    Output: "2023-12-25"

.. code-block:: toml

    # Time only
    [[layouts.demo.lines]]
    field = "time"
    index = 2
    formatter = "datetime"

    [layouts.demo.lines.formatter_params]
    format = "%H:%M:%S"

.. code-block:: text

    Input: 1703516400
    Output: "15:00:00"

.. code-block:: toml

    # Custom format
    [[layouts.demo.lines]]
    field = "created_at"
    index = 3
    formatter = "datetime"

    [layouts.demo.lines.formatter_params]
    format = "%b %d, %Y at %I:%M %p"

.. code-block:: text

    Input: datetime(2023, 12, 25, 15, 30)
    Output: "Dec 25, 2023 at 03:30 PM"

**Common Format Codes:**

- ``%Y`` - Year with century (e.g., 2023)
- ``%m`` - Month as zero-padded number (01-12)
- ``%d`` - Day of month as zero-padded number (01-31)
- ``%H`` - Hour (24-hour clock) as zero-padded number (00-23)
- ``%M`` - Minute as zero-padded number (00-59)
- ``%S`` - Second as zero-padded number (00-59)
- ``%b`` - Abbreviated month name (Jan, Feb, etc.)
- ``%B`` - Full month name (January, February, etc.)
- ``%I`` - Hour (12-hour clock) as zero-padded number (01-12)
- ``%p`` - AM or PM

relative_time
~~~~~~~~~~~~~

Format time differences in human-readable relative format (e.g., "5m ago", "2d ago").

**Parameters:**

- ``format`` - "short" or "long" (optional, default: "short")

**Input:**

Time value in seconds (typically the number of seconds elapsed)

**Examples:**

.. code-block:: toml

    # Short format
    [[layouts.demo.lines]]
    field = "elapsed_seconds"
    index = 0
    formatter = "relative_time"

    [layouts.demo.lines.formatter_params]
    format = "short"

.. code-block:: text

    Input: 45 → Output: "45s ago"
    Input: 300 → Output: "5m ago"
    Input: 3600 → Output: "1h ago"
    Input: 86400 → Output: "1d ago"

.. code-block:: toml

    # Long format
    [[layouts.demo.lines]]
    field = "elapsed_seconds"
    index = 1
    formatter = "relative_time"

    [layouts.demo.lines.formatter_params]
    format = "long"

.. code-block:: text

    Input: 45 → Output: "45 seconds ago"
    Input: 300 → Output: "5 minutes ago"
    Input: 3600 → Output: "1 hours ago"
    Input: 86400 → Output: "1 days ago"

**Time Ranges:**

- Less than 60 seconds: shows seconds
- 60-3599 seconds: shows minutes
- 3600-86399 seconds: shows hours
- 86400+ seconds: shows days

template
~~~~~~~~

Combine multiple fields using a Python format string with field placeholders.

This is the most powerful formatter, allowing you to combine multiple fields with custom formatting specifications in a single template string.

**Parameters:**

- ``template`` - Template string with ``{field}`` placeholders (required)
- ``fields`` - List of field names/paths to extract from context (required)

**Template Features:**

- Python format specifications (e.g., ``.2f``, ``:>10``, ``:,``)
- Multiple fields in one template
- Nested field access via dot notation (e.g., ``current_price.usd``)
- All Python format mini-language features

**Examples:**

.. code-block:: toml

    # Basic field combination
    [[layouts.demo.lines]]
    field = "ticker"
    index = 0
    formatter = "template"

    [layouts.demo.lines.formatter_params]
    template = "{symbol} - ${price:.2f}"
    fields = ["symbol", "price"]

.. code-block:: text

    Input: {"symbol": "BTC", "price": 45234.567}
    Output: "BTC - $45234.57"

.. code-block:: toml

    # Multiple fields with formatting
    [[layouts.demo.lines]]
    field = "stock"
    index = 1
    formatter = "template"

    [layouts.demo.lines.formatter_params]
    template = "{symbol} - ${price:.2f} - {volume}/$"
    fields = ["symbol", "price", "volume"]

.. code-block:: text

    Input: {"symbol": "AAPL", "price": 172.43, "volume": "1.2M"}
    Output: "AAPL - $172.43 - 1.2M/$"

.. code-block:: toml

    # Nested field access
    [[layouts.demo.lines]]
    field = "crypto"
    index = 2
    formatter = "template"

    [layouts.demo.lines.formatter_params]
    template = "{name}: ${current_price_usd:.2f}"
    fields = ["name", "current_price.usd"]

.. code-block:: text

    Input: {"name": "Bitcoin", "current_price": {"usd": 45234.567}}
    Output: "Bitcoin: $45234.57"

.. code-block:: toml

    # Answer to user's question: format two floats
    [[layouts.demo.lines]]
    field = "coordinates"
    index = 3
    formatter = "template"

    [layouts.demo.lines.formatter_params]
    template = "{a:.1f} {b:.1f}"
    fields = ["a", "b"]

.. code-block:: text

    Input: {"a": 3.14159, "b": 2.71828}
    Output: "3.1 2.7"

.. code-block:: toml

    # Alignment and padding
    [[layouts.demo.lines]]
    field = "table_row"
    index = 4
    formatter = "template"

    [layouts.demo.lines.formatter_params]
    template = "{name:<20} {value:>10.2f} {status:^10}"
    fields = ["name", "value", "status"]

.. code-block:: text

    Input: {"name": "Temperature", "value": 23.456, "status": "OK"}
    Output: "Temperature              23.46     OK    "

.. code-block:: toml

    # Thousands separator
    [[layouts.demo.lines]]
    field = "stats"
    index = 5
    formatter = "template"

    [layouts.demo.lines.formatter_params]
    template = "Population: {count:,}"
    fields = ["count"]

.. code-block:: text

    Input: {"count": 1234567}
    Output: "Population: 1,234,567"

.. code-block:: toml

    # Percentage formatting
    [[layouts.demo.lines]]
    field = "progress"
    index = 6
    formatter = "template"

    [layouts.demo.lines.formatter_params]
    template = "Progress: {value:.1%}"
    fields = ["value"]

.. code-block:: text

    Input: {"value": 0.756}
    Output: "Progress: 75.6%"

**Python Format Specification Mini-Language:**

The template formatter supports all Python format specifications:

- ``:f`` - Fixed-point notation
- ``:.2f`` - Fixed-point with 2 decimal places
- ``:,`` - Thousands separator
- ``:.2%`` - Percentage with 2 decimals
- ``:>10`` - Right-align in 10 characters
- ``:<10`` - Left-align in 10 characters
- ``:^10`` - Center in 10 characters
- ``:0>5`` - Zero-pad to 5 characters

See Python's `Format Specification Mini-Language <https://docs.python.org/3/library/string.html#format-specification-mini-language>`_ for complete details.

**Error Handling:**

- Missing fields resolve to empty string
- Invalid template syntax returns "Template error: <error message>"
- Non-dict values are converted to string

Custom Formatters
-----------------

You can register custom formatters using the FormatterRegistry:

Basic Custom Formatter
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    from viewtext import get_formatter_registry

    def format_percentage(value, **kwargs):
        decimals = kwargs.get("decimals", 1)
        return f"{value:.{decimals}f}%"

    formatter_registry = get_formatter_registry()
    formatter_registry.register("percentage", format_percentage)

Then use it in your TOML:

.. code-block:: toml

    [[layouts.demo.lines]]
    field = "growth_rate"
    index = 0
    formatter = "percentage"

    [layouts.demo.lines.formatter_params]
    decimals = 2

Advanced Custom Formatter
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    from viewtext import get_formatter_registry

    def format_bytes(value, **kwargs):
        """Format byte count as human-readable size."""
        units = ["B", "KB", "MB", "GB", "TB"]
        unit_index = 0
        size = float(value)

        while size >= 1024 and unit_index < len(units) - 1:
            size /= 1024
            unit_index += 1

        decimals = kwargs.get("decimals", 1)
        return f"{size:.{decimals}f} {units[unit_index]}"

    formatter_registry = get_formatter_registry()
    formatter_registry.register("bytes", format_bytes)

Usage:

.. code-block:: toml

    [[layouts.demo.lines]]
    field = "file_size"
    index = 0
    formatter = "bytes"

    [layouts.demo.lines.formatter_params]
    decimals = 2

.. code-block:: text

    Input: 1536 → Output: "1.50 KB"
    Input: 1048576 → Output: "1.00 MB"

Formatter vs Computed Field Operation
--------------------------------------

It's important to understand the difference between formatters and computed field operations:

**Formatters:**

- Applied at display time
- Only affect presentation, not data
- Defined in layout line definitions
- Return formatted strings
- Cannot be chained or used as input to other fields
- Examples: number, price, datetime, template

**Computed Field Operations:**

- Applied at data processing time
- Transform the actual data
- Defined in the fields section
- Return processed values (can be any type)
- Can be chained (output of one is input to another)
- Examples: add, subtract, multiply, concat, conditional

**When to Use Each:**

Use **formatters** when you want to:

- Format numbers with thousands separators for display
- Add currency symbols to prices
- Format dates/times for display
- Combine multiple fields into one display string

Use **computed field operations** when you want to:

- Calculate derived values (e.g., subtotal * tax_rate)
- Perform unit conversions (e.g., Celsius to Fahrenheit)
- Transform data (e.g., concatenate first and last name)
- Create intermediate values for further processing

**Example showing both:**

.. code-block:: toml

    # Computed field: calculate total price
    [fields.total_price]
    operation = "multiply"
    sources = ["price", "quantity"]
    default = 0.0

    # Formatter: display total_price with currency symbol
    [[layouts.product.lines]]
    field = "total_price"
    index = 0
    formatter = "price"

    [layouts.product.lines.formatter_params]
    symbol = "$"
    decimals = 2
    thousands_sep = ","

Formatter Presets
-----------------

You can define reusable formatter configurations (presets) in your TOML files to promote
consistency and reduce duplication across your layouts.

Defining Presets
~~~~~~~~~~~~~~~~

Formatter presets are defined in the ``[formatters]`` section. Each preset has a ``type``
field that specifies the built-in formatter type, along with any parameters for that formatter:

.. code-block:: toml

    # Define formatter presets
    [formatters.usd_price]
    type = "price"
    symbol = "$"
    decimals = 2
    thousands_sep = ","

    [formatters.eur_price]
    type = "price"
    symbol = "€"
    decimals = 2
    thousands_sep = "."
    decimal_sep = ","

    [formatters.short_date]
    type = "datetime"
    format = "%Y-%m-%d"

    [formatters.time_only]
    type = "datetime"
    format = "%H:%M"

Using Presets in Layouts
~~~~~~~~~~~~~~~~~~~~~~~~~

Once defined, presets can be referenced by name in two ways:

**Method 1: Direct reference in layout line** (recommended for simplicity):

.. code-block:: toml

    [[layouts.product.lines]]
    field = "price"
    index = 0
    formatter = "usd_price"  # References the preset by name

    [[layouts.product.lines]]
    field = "created_at"
    index = 1
    formatter = "short_date"  # References the preset by name

**Method 2: Template field_formatters** (useful for template formatter):

.. code-block:: toml

    [[layouts.crypto.lines]]
    field = "ticker"
    index = 0
    formatter = "template"

    [layouts.crypto.lines.formatter_params]
    template = "{symbol} - {price}"
    fields = ["symbol", "price"]
    field_formatters = { "price": "usd_price" }  # Apply preset to specific field

Benefits of Using Presets
~~~~~~~~~~~~~~~~~~~~~~~~~~

1. **Consistency** - Define formatting rules once, use everywhere
2. **Maintainability** - Update formatting in one place, affects all usages
3. **Readability** - Layout definitions become more concise and expressive
4. **Reusability** - Share formatters across multiple layouts and files

Comparison: Inline vs Preset
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Without presets** (verbose, repeated configuration):

.. code-block:: toml

    [[layouts.product.lines]]
    field = "price"
    index = 0
    formatter = "price"

    [layouts.product.lines.formatter_params]
    symbol = "$"
    decimals = 2
    thousands_sep = ","

    [[layouts.invoice.lines]]
    field = "total"
    index = 5
    formatter = "price"

    [layouts.invoice.lines.formatter_params]
    symbol = "$"
    decimals = 2
    thousands_sep = ","

**With presets** (concise, reusable):

.. code-block:: toml

    [formatters.usd_price]
    type = "price"
    symbol = "$"
    decimals = 2
    thousands_sep = ","

    [[layouts.product.lines]]
    field = "price"
    index = 0
    formatter = "usd_price"

    [[layouts.invoice.lines]]
    field = "total"
    index = 5
    formatter = "usd_price"

Preset Resolution
~~~~~~~~~~~~~~~~~

When ViewText encounters a formatter name in a layout, it follows this resolution order:

1. Check if ``formatter_params`` is provided inline - use built-in formatter with those params
2. Check if a preset exists with that name - use preset configuration
3. Fall back to built-in formatter with default parameters

This means you can mix inline parameters and presets in the same layout:

.. code-block:: toml

    [formatters.standard_date]
    type = "datetime"
    format = "%Y-%m-%d"

    [[layouts.mixed.lines]]
    field = "created_at"
    index = 0
    formatter = "standard_date"  # Uses preset

    [[layouts.mixed.lines]]
    field = "price"
    index = 1
    formatter = "price"

    [layouts.mixed.lines.formatter_params]
    symbol = "$"
    decimals = 2  # Inline parameters

Organizing Presets in Separate Files
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For better organization, you can define formatter presets in a separate file:

``formatters.toml``:

.. code-block:: toml

    [formatters.usd_price]
    type = "price"
    symbol = "$"
    decimals = 2
    thousands_sep = ","

    [formatters.eur_price]
    type = "price"
    symbol = "€"
    decimals = 2
    thousands_sep = "."
    decimal_sep = ","

``layouts.toml``:

.. code-block:: toml

    [layouts.product]
    name = "Product Display"

    [[layouts.product.lines]]
    field = "price"
    index = 0
    formatter = "usd_price"

Load both files together:

.. code-block:: bash

    viewtext --config layouts.toml --formatters formatters.toml list

.. code-block:: python

    from viewtext import LayoutLoader

    loader = LayoutLoader(
        config_path="layouts.toml",
        formatters_path="formatters.toml"
    )

See :doc:`user_guide` for more information on split configuration files.

Best Practices
--------------

1. **Use appropriate formatters** - Choose the formatter that best matches your data type (price for currency, datetime for timestamps, etc.)

2. **Define global formatter configurations** - Create reusable formatter presets for consistency across layouts

3. **Use template formatter for complex formatting** - When you need to combine multiple fields or use advanced Python format specifications

4. **Consider localization** - Use thousands_sep and decimal_sep parameters to format numbers according to regional conventions

5. **Test with edge cases** - Verify formatter behavior with None values, very large/small numbers, and edge cases

6. **Document custom formatters** - Add docstrings and examples when creating custom formatters

7. **Keep formatters simple** - Formatters should focus on presentation. Use computed field operations for data transformation.

Examples by Use Case
--------------------

Financial Data
~~~~~~~~~~~~~~

.. code-block:: toml

    # US stock display
    [[layouts.stock.lines]]
    field = "ticker"
    index = 0
    formatter = "template"

    [layouts.stock.lines.formatter_params]
    template = "{symbol} ${price:.2f} {change:+.2f} ({change_pct:+.1f}%)"
    fields = ["symbol", "price", "change", "change_pct"]

    # European price formatting
    [[layouts.product_eu.lines]]
    field = "price"
    index = 1
    formatter = "price"

    [layouts.product_eu.lines.formatter_params]
    symbol = "€"
    decimals = 2
    thousands_sep = "."
    decimal_sep = ","

Temperature Display
~~~~~~~~~~~~~~~~~~~

.. code-block:: toml

    # Celsius with one decimal
    [[layouts.weather.lines]]
    field = "temp_celsius"
    index = 0
    formatter = "number"

    [layouts.weather.lines.formatter_params]
    decimals = 1
    suffix = "°C"

    # Both Celsius and Fahrenheit
    [[layouts.weather.lines]]
    field = "temperature"
    index = 1
    formatter = "template"

    [layouts.weather.lines.formatter_params]
    template = "{temp_c:.1f}°C / {temp_f:.1f}°F"
    fields = ["temp_c", "temp_f"]

Activity Timestamps
~~~~~~~~~~~~~~~~~~~

.. code-block:: toml

    # Last seen time
    [[layouts.user.lines]]
    field = "last_seen_seconds"
    index = 0
    formatter = "relative_time"

    [layouts.user.lines.formatter_params]
    format = "short"

    # Created date
    [[layouts.user.lines]]
    field = "created_at"
    index = 1
    formatter = "datetime"

    [layouts.user.lines.formatter_params]
    format = "%b %d, %Y"

Dashboard Layout
~~~~~~~~~~~~~~~~

.. code-block:: toml

    # System metrics dashboard
    [[layouts.dashboard.lines]]
    field = "cpu"
    index = 0
    formatter = "template"

    [layouts.dashboard.lines.formatter_params]
    template = "CPU: {usage:>5.1f}% [{cores} cores]"
    fields = ["usage", "cores"]

    [[layouts.dashboard.lines]]
    field = "memory"
    index = 1
    formatter = "template"

    [layouts.dashboard.lines.formatter_params]
    template = "MEM: {used:>6.1f}/{total:>6.1f} GB ({pct:>5.1f}%)"
    fields = ["used", "total", "pct"]

    [[layouts.dashboard.lines]]
    field = "uptime"
    index = 2
    formatter = "relative_time"

    [layouts.dashboard.lines.formatter_params]
    format = "short"

See Also
--------

- :doc:`computed_fields_reference` - Data transformation operations
- :doc:`user_guide` - General usage guide
- :doc:`examples` - Complete example configurations
