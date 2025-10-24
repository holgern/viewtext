Inputs Reference
================

This document provides a complete reference for input definitions in ViewText.

Overview
--------

Inputs are the foundation of ViewText layouts. They define how data is extracted from context dictionaries and can include:

- **Context Key Mapping** - Map input names to context dictionary keys
- **Validation Rules** - Enforce type checking and constraints
- **Computed Operations** - Perform calculations without writing code
- **Default Values** - Provide fallbacks for missing data
- **Transformations** - Apply simple text transformations

Input Definition Structure
--------------------------

Inputs are defined in the ``[inputs]`` section of TOML configuration files:

.. code-block:: toml

    [inputs.field_name]
    # Required: How to get the value
    context_key = "path.to.value"  # OR operation = "..." for computed inputs

    # Optional: Validation
    type = "str"
    min_value = 0
    max_value = 100
    on_validation_error = "use_default"

    # Optional: Default value
    default = "fallback"

    # Optional: Text transformation
    transform = "upper"

Input Mapping Types
-----------

There are five types of input definitions:

1. **Context Inputs** - Extract values directly from context
2. **Computed Inputs** - Perform calculations on source data
3. **Constant Inputs** - Return static values
4. **Python Function Inputs** - Execute Python code to generate values
5. **Validated Inputs** - Include type checking and constraints

Context Inputs
~~~~~~~~~~~~~~

Map input names to keys in the context dictionary.

**Basic Example:**

.. code-block:: toml

    [inputs.temperature]
    context_key = "temp"
    default = 0

**Nested Context Keys:**

.. code-block:: toml

    [inputs.city_name]
    context_key = "location.city"
    default = "Unknown"

**Method Calls:**

.. code-block:: toml

    [inputs.upper_name]
    context_key = "name.upper()"
    default = ""

**Attribute Access:**

.. code-block:: toml

    [inputs.first_item]
    context_key = "items.0"
    default = None

Computed Inputs
~~~~~~~~~~~~~~~

Perform operations on source data. See :doc:`computed_fields_reference` for complete documentation.

**Example:**

.. code-block:: toml

    [inputs.total_price]
    operation = "multiply"
    sources = ["price", "quantity"]
    default = 0.0

    [inputs.temp_fahrenheit]
    operation = "celsius_to_fahrenheit"
    sources = ["temp_celsius"]
    default = 0.0

Constant Inputs
~~~~~~~~~~~~~~~

Return static values without requiring context data. Useful for constants like currency symbols, fixed numbers, or configuration values.

**Key features:**

- No context data required
- Type validation applied to constant value
- More explicit than using ``python_function``
- Better performance than python functions

**Example:**

.. code-block:: toml

    # String constants
    [inputs.currency_symbol]
    constant = "€"
    type = "str"

    [inputs.app_name]
    constant = "ViewText"
    type = "str"

    # Numeric constants
    [inputs.vat_rate]
    constant = 0.19
    type = "float"

    [inputs.max_retries]
    constant = 3
    type = "int"

    # Boolean constants
    [inputs.debug_mode]
    constant = false
    type = "bool"

Python Function Inputs
~~~~~~~~~~~~~~~~~~~~~~

Execute Python code to generate dynamic values. Useful for timestamps, UUIDs, random values, or any Python expression.

**Key features:**

- Execute arbitrary Python expressions
- Import standard library modules
- Values are cached per render (same value across multiple uses)
- Transform and validation applied after execution
- Errors return default value

**Example:**

.. code-block:: toml

    # Current timestamp
    [inputs.current_time]
    python_module = "datetime"
    python_function = "datetime.datetime.now().timestamp()"
    transform = "int"
    type = "int"
    default = 0

    # Generate UUID
    [inputs.request_id]
    python_module = "uuid"
    python_function = "str(uuid.uuid4())"
    type = "str"
    default = ""

    # Random number
    [inputs.random_value]
    python_module = "random"
    python_function = "random.randint(1, 100)"
    type = "int"
    default = 0

    # Simple math (no module needed)
    [inputs.constant]
    python_function = "2 + 2"
    default = 0

.. warning::
   Python function inputs execute arbitrary Python code. Only use trusted configuration files.

Validated Inputs
~~~~~~~~~~~~~~~~

Include validation rules for type checking and constraints. See :doc:`validation_reference` for complete documentation.

**Example:**

.. code-block:: toml

    [inputs.username]
    context_key = "username"
    type = "str"
    min_length = 3
    max_length = 20
    on_validation_error = "raise"

    [inputs.age]
    context_key = "age"
    type = "int"
    min_value = 0
    max_value = 120
    on_validation_error = "use_default"
    default = 0

Common Parameters
-----------------

These parameters are available for all field types:

context_key
~~~~~~~~~~~

**Type:** ``str``

**Required:** Yes (unless ``operation`` is specified)

The key path to extract from the context dictionary. Supports:

- Simple keys: ``"temperature"``
- Nested dictionary keys: ``"location.city"``
- Attribute access: ``"user.name"``
- Method calls: ``"text.upper()"``
- Array indexing: ``"items.0"`` (lists and tuples only)
- Nested arrays: ``"matrix.0.1"``
- Array with dicts: ``"users.0.name"``
- Chained operations: ``"text.strip().lower()"``

**Examples:**

.. code-block:: toml

    # Simple key
    [inputs.status]
    context_key = "status"

    # Nested dictionary key
    [inputs.city]
    context_key = "location.city"

    # Method call
    [inputs.upper_text]
    context_key = "text.upper()"

    # Array index
    [inputs.first_tag]
    context_key = "tags.0"

    # Nested array
    [inputs.matrix_value]
    context_key = "matrix.0.1"

    # Array with dictionary
    [inputs.first_user_email]
    context_key = "users.0.email"

default
~~~~~~~

**Type:** Any

**Required:** No (but recommended)

Value to return when the field cannot be retrieved or validation fails.

**Examples:**

.. code-block:: toml

    [inputs.temperature]
    context_key = "temp"
    default = 0

    [inputs.username]
    context_key = "user.name"
    default = "Guest"

    [inputs.tags]
    context_key = "tags"
    default = []

transform
~~~~~~~~~

**Type:** ``str``

**Required:** No

**Available transforms:**

- ``upper`` - Convert to uppercase
- ``lower`` - Convert to lowercase

Simple text transformations applied after retrieving the value.

**Examples:**

.. code-block:: toml

    [inputs.uppercase_name]
    context_key = "name"
    transform = "upper"
    default = ""

    [inputs.lowercase_email]
    context_key = "email"
    transform = "lower"
    default = ""

python_module
~~~~~~~~~~~~~

**Type:** ``str``

**Required:** No (for Python function inputs)

Name of the Python standard library module to import before executing ``python_function``.

**Examples:**

.. code-block:: toml

    [inputs.current_time]
    python_module = "datetime"
    python_function = "datetime.datetime.now().timestamp()"
    default = 0

    [inputs.uuid]
    python_module = "uuid"
    python_function = "str(uuid.uuid4())"
    default = ""

    [inputs.random_value]
    python_module = "random"
    python_function = "random.randint(1, 100)"
    default = 0

python_function
~~~~~~~~~~~~~~~

**Type:** ``str``

**Required:** Yes (for Python function inputs)

Python expression to evaluate. The expression has access to any modules imported via ``python_module``.

Results are cached per render using ``__python_function_cache_{field_name}`` to ensure consistent values across multiple field uses.

**Execution order:** eval → transform → validate

**Examples:**

.. code-block:: toml

    # With module import
    [inputs.timestamp]
    python_module = "datetime"
    python_function = "datetime.datetime.now().timestamp()"
    transform = "int"
    type = "int"
    default = 0

    # Generate UUID
    [inputs.request_id]
    python_module = "uuid"
    python_function = "str(uuid.uuid4())"
    type = "str"
    default = ""

.. warning::
   Python function inputs execute arbitrary code. Only use trusted configuration files.

.. note::
   For static constant values, use the ``constant`` parameter instead of ``python_function``.

constant
~~~~~~~~

**Type:** Any (string, number, boolean, etc.)

**Required:** Yes (for constant inputs)

Static value to return for this field. Unlike ``default``, which is only used as a fallback, ``constant`` is the primary value.

**Examples:**

.. code-block:: toml

    # String constant
    [inputs.currency_symbol]
    constant = "€"
    type = "str"

    # Numeric constant
    [inputs.seconds_per_minute]
    constant = 60
    type = "int"

    # Float constant
    [inputs.pi]
    constant = 3.14159
    type = "float"

    # Boolean constant
    [inputs.feature_enabled]
    constant = true
    type = "bool"

**When to use:**

- Currency symbols and units
- Mathematical or physical constants
- Configuration values that don't change per render
- Default text values like "N/A" or "Unknown"

**Constant vs Python Function:**

.. code-block:: toml

    # Preferred: Use constant for static values
    [inputs.euro]
    constant = "€"
    type = "str"

    # Avoid: Using python_function for constants
    [inputs.euro]
    python_function = "'€'"
    type = "str"

Validation Parameters
---------------------

See :doc:`validation_reference` for complete validation documentation.

type
~~~~

**Type:** ``str``

**Valid values:** ``str``, ``int``, ``float``, ``bool``, ``list``, ``dict``, ``any``

Specifies the expected data type.

**Example:**

.. code-block:: toml

    [inputs.age]
    context_key = "age"
    type = "int"
    default = 0

on_validation_error
~~~~~~~~~~~~~~~~~~~

**Type:** ``str``

**Valid values:** ``use_default``, ``raise``, ``skip``, ``coerce``

**Default:** ``use_default``

Controls behavior when validation fails.

**Example:**

.. code-block:: toml

    [inputs.username]
    context_key = "username"
    type = "str"
    on_validation_error = "raise"

Numeric Constraints
~~~~~~~~~~~~~~~~~~~

min_value
^^^^^^^^^

**Type:** ``float``

**Applies to:** ``int``, ``float``

Minimum allowed value (inclusive).

**Example:**

.. code-block:: toml

    [inputs.age]
    type = "int"
    min_value = 0
    default = 0

max_value
^^^^^^^^^

**Type:** ``float``

**Applies to:** ``int``, ``float``

Maximum allowed value (inclusive).

**Example:**

.. code-block:: toml

    [inputs.percentage]
    type = "float"
    max_value = 100.0
    default = 0.0

String Constraints
~~~~~~~~~~~~~~~~~~

min_length
^^^^^^^^^^

**Type:** ``int``

**Applies to:** ``str``

Minimum string length.

**Example:**

.. code-block:: toml

    [inputs.username]
    type = "str"
    min_length = 3
    default = "guest"

max_length
^^^^^^^^^^

**Type:** ``int``

**Applies to:** ``str``

Maximum string length.

**Example:**

.. code-block:: toml

    [inputs.bio]
    type = "str"
    max_length = 200
    default = ""

pattern
^^^^^^^

**Type:** ``str`` (regex)

**Applies to:** ``str``

Regular expression pattern for validation.

**Example:**

.. code-block:: toml

    [inputs.email]
    type = "str"
    pattern = "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$"
    on_validation_error = "skip"

Enumeration Constraints
~~~~~~~~~~~~~~~~~~~~~~~

allowed_values
^^^^^^^^^^^^^^

**Type:** ``list``

**Applies to:** All types

List of allowed values.

**Example:**

.. code-block:: toml

    [inputs.status]
    type = "str"
    allowed_values = ["active", "pending", "inactive"]
    default = "pending"

List Constraints
~~~~~~~~~~~~~~~~

min_items
^^^^^^^^^

**Type:** ``int``

**Applies to:** ``list``

Minimum number of items.

**Example:**

.. code-block:: toml

    [inputs.tags]
    type = "list"
    min_items = 1
    default = ["general"]

max_items
^^^^^^^^^

**Type:** ``int``

**Applies to:** ``list``

Maximum number of items.

**Example:**

.. code-block:: toml

    [inputs.tags]
    type = "list"
    max_items = 5
    default = []

Computed Field Parameters
-------------------------

See :doc:`computed_fields_reference` for complete documentation.

operation
~~~~~~~~~

**Type:** ``str``

**Required:** Yes (for computed inputs)

The operation to perform. Available operations:

**Temperature:**
- ``celsius_to_fahrenheit``
- ``fahrenheit_to_celsius``

**Arithmetic:**
- ``add``, ``subtract``, ``multiply``, ``divide``, ``modulo``

**Aggregate:**
- ``average``, ``min``, ``max``

**Mathematical:**
- ``abs``, ``round``, ``ceil``, ``floor``, ``linear_transform``

**String:**
- ``concat``, ``split``, ``substring``

**Conditional:**
- ``conditional``

**Formatting:**
- ``format_number``

sources
~~~~~~~

**Type:** ``list[str]``

**Required:** Yes (for most computed operations)

List of source input names to use as inputs.

**Example:**

.. code-block:: toml

    [inputs.total]
    operation = "add"
    sources = ["price", "tax", "shipping"]
    default = 0.0

Operation-Specific Parameters
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Different operations support additional parameters:

**linear_transform:**

.. code-block:: toml

    [inputs.scaled]
    operation = "linear_transform"
    sources = ["value"]
    multiply = 2
    divide = 3
    add = 10
    default = 0.0

**concat:**

.. code-block:: toml

    [inputs.full_name]
    operation = "concat"
    sources = ["first_name", "last_name"]
    separator = " "
    prefix = "Mr. "
    suffix = ", Esq."
    skip_empty = true
    default = ""

**split:**

.. code-block:: toml

    [inputs.domain]
    operation = "split"
    sources = ["email"]
    separator = "@"
    index = 1
    default = ""

**substring:**

.. code-block:: toml

    [inputs.year]
    operation = "substring"
    sources = ["date"]
    start = 0
    end = 4
    default = ""

**conditional:**

.. code-block:: toml

    [inputs.price_display]
    operation = "conditional"
    condition = { input = "currency", equals = "USD" }
    if_true = "$~amount~"
    if_false = "~amount~ ~currency~"
    default = ""

**format_number:**

.. code-block:: toml

    [inputs.formatted_price]
    operation = "format_number"
    sources = ["price"]
    thousands_sep = ","
    decimal_sep = "."
    decimals_param = 2
    default = "0.00"

Context Key Resolution
----------------------

ViewText supports flexible context key resolution:

Simple Keys
~~~~~~~~~~~

.. code-block:: toml

    [inputs.name]
    context_key = "name"

**Context:**

.. code-block:: python

    {"name": "Alice"}

**Result:** ``"Alice"``

Nested Keys
~~~~~~~~~~~

Use dot notation for nested dictionaries:

.. code-block:: toml

    [inputs.city]
    context_key = "location.city"

**Context:**

.. code-block:: python

    {"location": {"city": "San Francisco", "state": "CA"}}

**Result:** ``"San Francisco"``

Method Calls
~~~~~~~~~~~~

Call methods on context values:

.. code-block:: toml

    [inputs.upper_name]
    context_key = "name.upper()"

**Context:**

.. code-block:: python

    {"name": "alice"}

**Result:** ``"ALICE"``

**With Arguments:**

.. code-block:: toml

    [inputs.formatted]
    context_key = "text.replace('foo', 'bar')"

Attribute Access
~~~~~~~~~~~~~~~~

Access object attributes:

.. code-block:: toml

    [inputs.length]
    context_key = "items.__len__()"

**Context:**

.. code-block:: python

    {"items": [1, 2, 3, 4, 5]}

**Result:** ``5``

Array Indexing
~~~~~~~~~~~~~~

Access list and tuple items by numeric index using dot notation:

.. code-block:: toml

    [inputs.first_tag]
    context_key = "tags.0"

**Context:**

.. code-block:: python

    {"tags": ["python", "viewtext", "cli"]}

**Result:** ``"python"``

**Nested array access:**

You can access nested arrays by chaining numeric indices:

.. code-block:: toml

    [inputs.matrix_value]
    context_key = "matrix.0.1"

**Context:**

.. code-block:: python

    {"matrix": [[1, 2, 3], [4, 5, 6], [7, 8, 9]]}

**Result:** ``2``

**Array with dictionary elements:**

Combine array indexing with dictionary key access:

.. code-block:: toml

    [inputs.first_user_name]
    context_key = "users.0.name"

**Context:**

.. code-block:: python

    {
        "users": [
            {"name": "Alice", "age": 30},
            {"name": "Bob", "age": 25}
        ]
    }

**Result:** ``"Alice"``

**Complex nested structures:**

Access deeply nested data structures:

.. code-block:: toml

    [inputs.median_fee]
    context_key = "mempool_blocks.0.fees.median"

**Context:**

.. code-block:: python

    {
        "mempool_blocks": [
            {"fees": {"median": 0.75, "average": 0.82}},
            {"fees": {"median": 0.69, "average": 0.71}}
        ]
    }

**Result:** ``0.75``

.. note::

   - Array indexing only works with ``list`` and ``tuple`` types
   - Out of bounds indices return the field's default value
   - String indexing is not supported (e.g., ``"text.0"`` will return default)
   - Numeric indices must be non-negative integers (negative indexing not currently supported)

Chained Operations
~~~~~~~~~~~~~~~~~~

Chain multiple operations:

.. code-block:: toml

    [inputs.clean_text]
    context_key = "text.strip().lower()"

**Context:**

.. code-block:: python

    {"text": "  HELLO WORLD  "}

**Result:** ``"hello world"``

Complete Examples
-----------------

Simple Weather Display
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: toml

    [inputs.temperature]
    context_key = "temp"
    type = "float"
    default = 0.0

    [inputs.city]
    context_key = "city"
    type = "str"
    default = "Unknown"

    [inputs.humidity]
    context_key = "humidity"
    type = "int"
    min_value = 0
    max_value = 100
    default = 0

User Profile
~~~~~~~~~~~~

.. code-block:: toml

    [inputs.username]
    context_key = "username"
    type = "str"
    min_length = 3
    max_length = 20
    pattern = "^[a-zA-Z0-9_]+$"
    on_validation_error = "raise"

    [inputs.email]
    context_key = "email"
    type = "str"
    pattern = "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$"
    on_validation_error = "skip"

    [inputs.age]
    context_key = "age"
    type = "int"
    min_value = 13
    max_value = 120
    on_validation_error = "use_default"
    default = 0

    [inputs.membership]
    context_key = "membership"
    type = "str"
    allowed_values = ["free", "premium", "enterprise"]
    on_validation_error = "use_default"
    default = "free"

    [inputs.display_name]
    operation = "concat"
    sources = ["first_name", "last_name"]
    separator = " "
    default = "Anonymous"

E-commerce Product
~~~~~~~~~~~~~~~~~~

.. code-block:: toml

    [inputs.product_name]
    context_key = "name"
    type = "str"
    max_length = 100
    default = ""

    [inputs.price]
    context_key = "price"
    type = "float"
    min_value = 0.0
    on_validation_error = "use_default"
    default = 0.0

    [inputs.quantity]
    context_key = "quantity"
    type = "int"
    min_value = 1
    on_validation_error = "use_default"
    default = 1

    [inputs.line_total]
    operation = "multiply"
    sources = ["price", "quantity"]
    default = 0.0

    [inputs.sale_price]
    operation = "linear_transform"
    sources = ["price"]
    multiply = 0.85
    default = 0.0

    [inputs.formatted_price]
    operation = "format_number"
    sources = ["price"]
    thousands_sep = ","
    decimal_sep = "."
    decimals_param = 2
    default = "0.00"

Best Practices
--------------

1. **Always provide default values**

   .. code-block:: toml

       [inputs.optional_field]
       context_key = "optional"
       default = ""  # Always specify a default

2. **Use validation for critical inputs**

   .. code-block:: toml

       [inputs.user_id]
       context_key = "id"
       type = "int"
       on_validation_error = "raise"

3. **Choose appropriate error handling**

   - ``use_default`` for optional/display inputs
   - ``raise`` for required inputs
   - ``skip`` for truly optional inputs
   - ``coerce`` for flexible input

4. **Use descriptive input names**

   .. code-block:: toml

       # Good
       [inputs.temperature_fahrenheit]
       [inputs.user_email_address]

       # Avoid
       [inputs.temp]
       [inputs.email]

5. **Combine validation with computed inputs**

   .. code-block:: toml

       # Step 1: Validate input
       [inputs.price_validated]
       context_key = "price"
       type = "float"
       min_value = 0.0
       on_validation_error = "use_default"
       default = 0.0

       # Step 2: Compute with validated value
       [inputs.price_with_tax]
       operation = "linear_transform"
       sources = ["price_validated"]
       multiply = 1.08
       default = 0.0

6. **Test your input definitions**

   .. code-block:: bash

       # Test individual inputs
       viewtext -c config.toml test field_name key=value

       # Validate configuration
       viewtext -c config.toml check

       # List all inputs
       viewtext -c config.toml inputs

7. **Document complex field logic**

   Use comments in your TOML:

   .. code-block:: toml

       # User age with strict validation
       # Must be between 13-120 for COPPA compliance
       [inputs.user_age]
       context_key = "age"
       type = "int"
       min_value = 13
       max_value = 120
       on_validation_error = "raise"

Common Patterns
---------------

Graceful Fallbacks
~~~~~~~~~~~~~~~~~~

.. code-block:: toml

    [inputs.display_name]
    operation = "conditional"
    condition = { input = "username", equals = "" }
    if_true = "Guest"
    if_false = "~username~"
    default = "Guest"

Optional Inputs with Filtering
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: toml

    [inputs.optional_email]
    context_key = "email"
    type = "str"
    pattern = "^[a-zA-Z0-9._%+-]+@.*"
    on_validation_error = "skip"

Flexible Type Handling
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: toml

    [inputs.count]
    context_key = "count"
    type = "int"
    min_value = 0
    on_validation_error = "coerce"
    default = 0

Chaining Computed Inputs
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: toml

    # Step 1: Calculate subtotal
    [inputs.subtotal]
    operation = "multiply"
    sources = ["price", "quantity"]
    default = 0.0

    # Step 2: Calculate tax
    [inputs.tax]
    operation = "linear_transform"
    sources = ["subtotal"]
    multiply = 0.08
    default = 0.0

    # Step 3: Calculate total
    [inputs.total]
    operation = "add"
    sources = ["subtotal", "tax"]
    default = 0.0

CLI Commands for Inputs
-----------------------

List All Inputs
~~~~~~~~~~~~~~~

.. code-block:: bash

    viewtext -c config.toml inputs

Test a Field
~~~~~~~~~~~~

.. code-block:: bash

    viewtext -c config.toml test field_name key1=value1 key2=value2

Validate Configuration
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

    viewtext -c config.toml check

See Also
--------

- :doc:`computed_fields_reference` - Computed field operations
- :doc:`validation_reference` - Field validation details
- :doc:`user_guide` - Using inputs in layouts
- :doc:`formatters_reference` - Formatting field values for display
- ``examples/inputs.toml`` - Example field configurations
- ``examples/validation_example.toml`` - Validation examples
- ``examples/computed_fields.toml`` - Computed field examples
