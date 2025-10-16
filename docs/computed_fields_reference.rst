Computed Fields Reference
=========================

This document provides a complete reference for all computed field operations available in ViewText.

Overview
--------

Computed fields allow you to perform calculations and transformations on your data without writing Python code. All operations are defined declaratively in TOML configuration files and compiled at load time.

Common Parameters
-----------------

All computed field definitions share these parameters:

- **operation** (required) - Name of the operation to perform
- **sources** (required) - List of field names from context to use as inputs
- **default** (required) - Value to return if operation fails or sources are missing

Temperature Conversions
-----------------------

celsius_to_fahrenheit
~~~~~~~~~~~~~~~~~~~~~

Convert temperature from Celsius to Fahrenheit.

**Formula:** ``(celsius * 9/5) + 32``

**Parameters:**

- ``sources`` - Single source field containing Celsius temperature
- ``default`` - Value to return on error

**Example:**

.. code-block:: toml

    [fields.temp_f]
    operation = "celsius_to_fahrenheit"
    sources = ["temp_c"]
    default = 0.0

fahrenheit_to_celsius
~~~~~~~~~~~~~~~~~~~~~

Convert temperature from Fahrenheit to Celsius.

**Formula:** ``(fahrenheit - 32) * 5/9``

**Parameters:**

- ``sources`` - Single source field containing Fahrenheit temperature
- ``default`` - Value to return on error

**Example:**

.. code-block:: toml

    [fields.temp_c]
    operation = "fahrenheit_to_celsius"
    sources = ["temp_f"]
    default = 0.0

Arithmetic Operations
---------------------

add
~~~

Sum multiple values.

**Parameters:**

- ``sources`` - List of field names to sum
- ``default`` - Value to return on error

**Example:**

.. code-block:: toml

    [fields.total_score]
    operation = "add"
    sources = ["score1", "score2", "score3"]
    default = 0.0

subtract
~~~~~~~~

Subtract second value from first value.

**Parameters:**

- ``sources`` - List of exactly two field names ``[minuend, subtrahend]``
- ``default`` - Value to return on error

**Example:**

.. code-block:: toml

    [fields.profit]
    operation = "subtract"
    sources = ["revenue", "costs"]
    default = 0.0

multiply
~~~~~~~~

Multiply two or more values.

**Parameters:**

- ``sources`` - List of field names to multiply
- ``default`` - Value to return on error

**Example:**

.. code-block:: toml

    [fields.total_price]
    operation = "multiply"
    sources = ["price", "quantity"]
    default = 0.0

divide
~~~~~~

Divide first value by second value. Safely handles division by zero.

**Parameters:**

- ``sources`` - List of exactly two field names ``[dividend, divisor]``
- ``default`` - Value to return on error or division by zero

**Example:**

.. code-block:: toml

    [fields.average]
    operation = "divide"
    sources = ["total", "count"]
    default = 0.0

modulo
~~~~~~

Calculate remainder after division. Safely handles modulo by zero.

**Formula:** ``a % b``

**Parameters:**

- ``sources`` - List of exactly two field names ``[dividend, divisor]``
- ``default`` - Value to return on error or modulo by zero

**Example:**

.. code-block:: toml

    [fields.remainder]
    operation = "modulo"
    sources = ["number", "divisor"]
    default = 0

    # Check if number is even (remainder when divided by 2)
    [fields.is_odd]
    operation = "modulo"
    sources = ["number", "2"]
    default = 0

Aggregate Operations
--------------------

average
~~~~~~~

Calculate arithmetic mean of multiple values.

**Parameters:**

- ``sources`` - List of field names to average
- ``default`` - Value to return on error

**Example:**

.. code-block:: toml

    [fields.avg_temp]
    operation = "average"
    sources = ["temp_morning", "temp_noon", "temp_evening"]
    default = 0.0

min
~~~

Find minimum value among multiple values.

**Parameters:**

- ``sources`` - List of field names to compare
- ``default`` - Value to return on error

**Example:**

.. code-block:: toml

    [fields.lowest_price]
    operation = "min"
    sources = ["price_a", "price_b", "price_c"]
    default = 0.0

max
~~~

Find maximum value among multiple values.

**Parameters:**

- ``sources`` - List of field names to compare
- ``default`` - Value to return on error

**Example:**

.. code-block:: toml

    [fields.highest_score]
    operation = "max"
    sources = ["score1", "score2", "score3"]
    default = 0.0

Mathematical Operations
-----------------------

abs
~~~

Calculate absolute value.

**Parameters:**

- ``sources`` - Single source field
- ``default`` - Value to return on error

**Example:**

.. code-block:: toml

    [fields.price_change_abs]
    operation = "abs"
    sources = ["price_change"]
    default = 0.0

round
~~~~~

Round to nearest integer or specified decimal places.

**Parameters:**

- ``sources`` - Single source field
- ``decimals`` - Number of decimal places (optional, default: 0)
- ``default`` - Value to return on error

**Example:**

.. code-block:: toml

    # Round to integer
    [fields.price_rounded]
    operation = "round"
    sources = ["price"]
    default = 0.0

    # Round to 2 decimal places
    [fields.price_rounded_2]
    operation = "round"
    sources = ["price"]
    decimals = 2
    default = 0.0

ceil
~~~~

Round up to nearest integer.

**Parameters:**

- ``sources`` - Single source field
- ``default`` - Value to return on error

**Example:**

.. code-block:: toml

    [fields.pages_needed]
    operation = "ceil"
    sources = ["items_divided_by_page_size"]
    default = 0

floor
~~~~~

Round down to nearest integer.

**Parameters:**

- ``sources`` - Single source field
- ``default`` - Value to return on error

**Example:**

.. code-block:: toml

    [fields.complete_batches]
    operation = "floor"
    sources = ["items_divided_by_batch_size"]
    default = 0

linear_transform
~~~~~~~~~~~~~~~~

Apply linear transformation with multiplication, division, and addition.

**Formula:** ``(value * multiply / divide) + add``

**Parameters:**

- ``sources`` - Single source field
- ``multiply`` - Multiplication factor (optional, default: 1)
- ``divide`` - Division factor (optional, default: 1)
- ``add`` - Addition offset (optional, default: 0)
- ``default`` - Value to return on error or division by zero

**Examples:**

.. code-block:: toml

    # Convert km/h to mph
    [fields.speed_mph]
    operation = "linear_transform"
    sources = ["speed_kmh"]
    multiply = 0.621371
    default = 0.0

    # Apply 20% discount
    [fields.sale_price]
    operation = "linear_transform"
    sources = ["price"]
    multiply = 0.8
    default = 0.0

    # Convert meters to feet and add 5
    [fields.feet_plus_five]
    operation = "linear_transform"
    sources = ["meters"]
    multiply = 3.28084
    add = 5.0
    default = 0.0

    # Scale and offset (y = 2x/3 + 10)
    [fields.transformed]
    operation = "linear_transform"
    sources = ["value"]
    multiply = 2
    divide = 3
    add = 10
    default = 0.0

String Operations
-----------------

concat
~~~~~~

Join multiple strings with a separator.

**Parameters:**

- ``sources`` - List of field names containing strings to join
- ``separator`` - String to insert between values (optional, default: empty string)
- ``prefix`` - String to prepend to result (optional, default: empty string)
- ``suffix`` - String to append to result (optional, default: empty string)
- ``skip_empty`` - Skip None/missing sources instead of returning default (optional, default: false)
- ``default`` - Value to return on error

**Examples:**

.. code-block:: toml

    # Join with space
    [fields.full_name]
    operation = "concat"
    sources = ["first_name", "last_name"]
    separator = " "
    default = ""

    # Join with dash
    [fields.date]
    operation = "concat"
    sources = ["year", "month", "day"]
    separator = "-"
    default = ""

    # Join without separator
    [fields.code]
    operation = "concat"
    sources = ["prefix", "number", "suffix"]
    default = ""

    # Add prefix (e.g., currency symbol)
    [fields.display_price]
    operation = "concat"
    sources = ["price"]
    prefix = "$"
    default = "Unknown"

    # Add suffix (e.g., unit)
    [fields.display_temp]
    operation = "concat"
    sources = ["temp"]
    suffix = "°C"
    default = "Unknown"

    # Skip missing fields
    [fields.display_name]
    operation = "concat"
    sources = ["first_name", "middle_name", "last_name"]
    separator = " "
    skip_empty = true
    default = "Unknown"

    # Complete example with all parameters
    [fields.location]
    operation = "concat"
    sources = ["city", "state", "country"]
    separator = ", "
    prefix = "Location: "
    suffix = "."
    skip_empty = true
    default = "Unknown"

split
~~~~~

Split a string by separator and extract value at specific index.

**Parameters:**

- ``sources`` - Single source field containing string to split
- ``separator`` - String to split on (optional, default: space)
- ``index`` - Zero-based index of part to extract (required)
- ``default`` - Value to return on error or out-of-bounds index

**Examples:**

.. code-block:: toml

    # Extract domain from email
    [fields.domain]
    operation = "split"
    sources = ["email"]
    separator = "@"
    index = 1
    default = ""

    # Extract first word
    [fields.first_word]
    operation = "split"
    sources = ["sentence"]
    separator = " "
    index = 0
    default = ""

    # Extract file extension
    [fields.extension]
    operation = "split"
    sources = ["filename"]
    separator = "."
    index = -1
    default = ""

substring
~~~~~~~~~

Extract substring from start position to end position.

**Parameters:**

- ``sources`` - Single source field containing string
- ``start`` - Starting index (0-based, supports negative indexing)
- ``end`` - Ending index (optional, supports negative indexing)
- ``default`` - Value to return on error

**Examples:**

.. code-block:: toml

    # Extract year from date (YYYY-MM-DD)
    [fields.year]
    operation = "substring"
    sources = ["date"]
    start = 0
    end = 4
    default = ""

    # Extract last 3 characters
    [fields.suffix]
    operation = "substring"
    sources = ["code"]
    start = -3
    default = ""

    # Extract from position 5 to end
    [fields.tail]
    operation = "substring"
    sources = ["text"]
    start = 5
    default = ""

    # Extract month from date (YYYY-MM-DD)
    [fields.month]
    operation = "substring"
    sources = ["date"]
    start = 5
    end = 7
    default = ""

Conditional Operations
----------------------

conditional
~~~~~~~~~~~

Returns different values based on a condition. Supports template syntax with field references.

**Parameters:**

- ``condition`` - Dictionary with ``field`` (field name to check) and ``equals`` (value to compare)
- ``if_true`` - Template string to return if condition matches (supports ``~field_name~`` references)
- ``if_false`` - Template string to return if condition doesn't match (supports ``~field_name~`` references)
- ``default`` - Value to return if condition field is missing or referenced fields are missing

**Template Syntax:**

Both ``if_true`` and ``if_false`` support field references using ``~field_name~`` syntax. These references are resolved at runtime and replaced with the actual field values.

**Examples:**

.. code-block:: toml

    # Show currency symbol only for USD
    [fields.price_display]
    operation = "conditional"
    condition = { field = "currency", equals = "USD" }
    if_true = "$~amount~"
    if_false = "~amount~ ~currency~"
    default = ""

.. code-block:: toml

    # Premium badge
    [fields.user_badge]
    operation = "conditional"
    condition = { field = "membership", equals = "premium" }
    if_true = "⭐ Premium Member"
    if_false = "Standard Member"
    default = "Guest"

.. code-block:: toml

    # Mix text and field references
    [fields.greeting]
    operation = "conditional"
    condition = { field = "language", equals = "es" }
    if_true = "Hola, ~name~!"
    if_false = "Hello, ~name~!"
    default = "Hello!"

**Notes:**

- Condition performs exact string equality match
- Field references in templates resolve to empty string if field is missing and default is None
- If the condition field itself is missing, returns the default value
- Multiple field references can be used in a single template

format_number
~~~~~~~~~~~~~

Formats a numeric value with custom thousands and decimal separators.

**Parameters:**

- ``sources`` or ``context_key`` - Field(s) to format
- ``thousands_sep`` - Thousands separator character (e.g., ``,``, ``.``, ``" "``, ``"'"``)
- ``decimal_sep`` - Decimal separator character (default: ``"."``)
- ``decimals_param`` - Number of decimal places (default: 0)
- ``default`` - Value to return if source is missing or invalid

**Examples:**

.. code-block:: toml

    # Format with comma separator (US/UK style)
    [fields.formatted_comma]
    operation = "format_number"
    sources = ["population"]
    thousands_sep = ","
    decimals_param = 0
    default = "N/A"
    # Input: 100000 → Output: "100,000"

.. code-block:: toml

    # Format European style (dot thousands, comma decimal)
    [fields.formatted_european]
    operation = "format_number"
    sources = ["price"]
    thousands_sep = "."
    decimal_sep = ","
    decimals_param = 2
    default = "N/A"
    # Input: 1234567.89 → Output: "1.234.567,89"

.. code-block:: toml

    # Format with space separator (international style)
    [fields.formatted_space]
    operation = "format_number"
    sources = ["distance"]
    thousands_sep = " "
    decimal_sep = ","
    decimals_param = 2
    default = ""
    # Input: 9876543.21 → Output: "9 876 543,21"

.. code-block:: toml

    # Swiss style (apostrophe thousands, dot decimal)
    [fields.formatted_swiss]
    operation = "format_number"
    sources = ["amount"]
    thousands_sep = "'"
    decimal_sep = "."
    decimals_param = 2
    default = "0.00"
    # Input: 1234567.89 → Output: "1'234'567.89"

.. code-block:: toml

    # No separator (just decimal formatting)
    [fields.formatted_plain]
    operation = "format_number"
    context_key = "value"
    thousands_sep = ""
    decimals_param = 2
    default = "0.00"
    # Input: 1234.567 → Output: "1234.57"

**Notes:**

- Returns the formatted number as a string
- Non-numeric values return the default
- Thousands separator can be any string (commonly ``,``, ``.``, ``" "``, or ``'``)
- Decimal separator can be any string (commonly ``.`` or ``,``)
- Default decimal separator is ``.`` (if not specified)
- Different from formatters (which are for display), this operation transforms the data itself

Error Handling
--------------

All computed field operations include automatic error handling:

**Numeric Operations** (add, subtract, multiply, divide, modulo, average, min, max, abs, round, ceil, floor, linear_transform, celsius_to_fahrenheit, fahrenheit_to_celsius):

- Missing source values return the default
- Non-numeric source values return the default
- Division by zero returns the default (divide, linear_transform)
- Modulo by zero returns the default (modulo)

**String Operations** (concat, split, substring):

- Missing source values return the default
- Out-of-bounds indices return the default (split, substring)
- Non-string values are converted to strings (concat, split, substring)

**Conditional Operations** (conditional):

- Missing condition field returns the default
- Missing referenced fields in templates resolve to empty string (if default is None) or default value
- Condition performs exact string equality match

**Formatting Operations** (format_number):

- Missing source values return the default
- Non-numeric source values return the default
- Invalid format parameters use safe defaults

**Configuration Errors:**

- Invalid operation names raise ``ValueError`` at configuration load time
- Missing required parameters raise ``ValueError`` at configuration load time

Best Practices
--------------

1. **Always provide meaningful defaults** - Choose defaults that make sense for your use case and won't cause confusion if the operation fails

2. **Use descriptive field names** - Computed field names should clearly indicate what they represent (e.g., ``temp_f`` not ``t1``)

3. **Chain operations when needed** - Create intermediate computed fields for complex transformations:

   .. code-block:: toml

       # Step 1: Scale value
       [fields.scaled_value]
       operation = "divide"
       sources = ["raw_value", "scale_factor"]
       default = 0.0

       # Step 2: Round result
       [fields.display_value]
       operation = "ceil"
       sources = ["scaled_value"]
       default = 0

4. **Document units and expectations** - Add comments in your TOML to explain what units are expected and produced

5. **Test edge cases** - Verify behavior with missing data, zero values, and boundary conditions

6. **Prefer linear_transform for unit conversions** - More efficient than chaining multiply/divide/add operations

Examples by Use Case
--------------------

Unit Conversions
~~~~~~~~~~~~~~~~

.. code-block:: toml

    # Temperature
    [fields.temp_f]
    operation = "celsius_to_fahrenheit"
    sources = ["temp_c"]
    default = 0.0

    # Distance
    [fields.miles]
    operation = "linear_transform"
    sources = ["kilometers"]
    multiply = 0.621371
    default = 0.0

    # Weight
    [fields.pounds]
    operation = "linear_transform"
    sources = ["kilograms"]
    multiply = 2.20462
    default = 0.0

E-commerce
~~~~~~~~~~

.. code-block:: toml

    # Line total
    [fields.line_total]
    operation = "multiply"
    sources = ["price", "quantity"]
    default = 0.0

    # Discount price (15% off)
    [fields.sale_price]
    operation = "linear_transform"
    sources = ["price"]
    multiply = 0.85
    default = 0.0

    # Tax amount (8% tax)
    [fields.tax]
    operation = "linear_transform"
    sources = ["subtotal"]
    multiply = 0.08
    default = 0.0

    # Grand total
    [fields.total]
    operation = "add"
    sources = ["subtotal", "tax", "shipping"]
    default = 0.0

Data Analysis
~~~~~~~~~~~~~

.. code-block:: toml

    # Average
    [fields.mean]
    operation = "average"
    sources = ["value1", "value2", "value3"]
    default = 0.0

    # Range
    [fields.min_value]
    operation = "min"
    sources = ["value1", "value2", "value3"]
    default = 0.0

    [fields.max_value]
    operation = "max"
    sources = ["value1", "value2", "value3"]
    default = 0.0

    [fields.range]
    operation = "subtract"
    sources = ["max_value", "min_value"]
    default = 0.0

Text Processing
~~~~~~~~~~~~~~~

.. code-block:: toml

    # Parse email
    [fields.username]
    operation = "split"
    sources = ["email"]
    separator = "@"
    index = 0
    default = ""

    [fields.domain]
    operation = "split"
    sources = ["email"]
    separator = "@"
    index = 1
    default = ""

    # Build display name
    [fields.display_name]
    operation = "concat"
    sources = ["first_name", "last_name"]
    separator = " "
    default = "Unknown"

    # Extract initials (first characters)
    [fields.first_initial]
    operation = "substring"
    sources = ["first_name"]
    start = 0
    end = 1
    default = ""

    [fields.last_initial]
    operation = "substring"
    sources = ["last_name"]
    start = 0
    end = 1
    default = ""

    [fields.initials]
    operation = "concat"
    sources = ["first_initial", "last_initial"]
    separator = ""
    default = ""

Conditional Logic
~~~~~~~~~~~~~~~~~

.. code-block:: toml

    # Display different field based on condition
    [fields.display_currency]
    operation = "conditional"
    condition = { field = "currency", equals = "USD" }
    if_true = "$~amount~"
    if_false = "~amount~ ~currency~"
    default = ""

    # Show premium vs standard badge
    [fields.badge]
    operation = "conditional"
    condition = { field = "is_premium", equals = "true" }
    if_true = "⭐ Premium"
    if_false = "Standard"
    default = "Unknown"
