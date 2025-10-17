Field Validation Reference
==========================

ViewText provides comprehensive field validation capabilities to ensure data quality and type safety. Validation rules are defined declaratively in TOML configuration files.

Overview
--------

Field validation allows you to:

- **Type Checking**: Ensure values are the correct type (str, int, float, bool, list, dict)
- **Constraint Validation**: Enforce numeric ranges, string lengths, patterns, and allowed values
- **Error Handling**: Control what happens when validation fails
- **Type Coercion**: Automatically convert compatible types

Validation is applied when field values are retrieved from context data using the field registry.

Validation Parameters
---------------------

All validation parameters are optional and can be added to field definitions in the ``[fields]`` section:

Basic Parameters
~~~~~~~~~~~~~~~~

type
^^^^

Specifies the expected data type for the field value.

**Supported Types:**

- ``str`` (or ``string``) - String values
- ``int`` (or ``integer``) - Integer numbers
- ``float`` - Floating point numbers
- ``bool`` (or ``boolean``) - Boolean true/false
- ``list`` (or ``array``) - List/array values
- ``dict`` (or ``object``) - Dictionary/object values
- ``any`` - Accept any type (no validation)

**Example:**

.. code-block:: toml

    [fields.user_age]
    context_key = "age"
    type = "int"
    default = 0

on_validation_error
^^^^^^^^^^^^^^^^^^^

Controls what happens when validation fails.

**Available Strategies:**

- ``use_default`` - Return the default value (default strategy)
- ``raise`` - Raise a ``ValidationError`` exception
- ``skip`` - Return ``None``
- ``coerce`` - Attempt to convert the value to the expected type

**Example:**

.. code-block:: toml

    [fields.username]
    context_key = "username"
    type = "str"
    on_validation_error = "raise"

    [fields.score]
    context_key = "score"
    type = "float"
    on_validation_error = "coerce"
    default = 0.0

Numeric Constraints
~~~~~~~~~~~~~~~~~~~

These constraints apply to numeric types (``int``, ``float``):

min_value
^^^^^^^^^

Minimum allowed value (inclusive).

**Example:**

.. code-block:: toml

    [fields.user_age]
    type = "int"
    min_value = 0
    default = 0

max_value
^^^^^^^^^

Maximum allowed value (inclusive).

**Example:**

.. code-block:: toml

    [fields.percentage]
    type = "float"
    max_value = 100.0
    default = 0.0

**Combined Example:**

.. code-block:: toml

    [fields.temperature]
    context_key = "temp"
    type = "float"
    min_value = -50.0
    max_value = 50.0
    on_validation_error = "use_default"
    default = 0.0

String Constraints
~~~~~~~~~~~~~~~~~~

These constraints apply to string types (``str``):

min_length
^^^^^^^^^^

Minimum allowed string length.

**Example:**

.. code-block:: toml

    [fields.username]
    type = "str"
    min_length = 3
    default = "guest"

max_length
^^^^^^^^^^

Maximum allowed string length.

**Example:**

.. code-block:: toml

    [fields.bio]
    type = "str"
    max_length = 200
    default = ""

**Combined Example:**

.. code-block:: toml

    [fields.username]
    context_key = "username"
    type = "str"
    min_length = 3
    max_length = 20
    on_validation_error = "raise"

pattern
^^^^^^^

Regular expression pattern that the string must match.

**Example:**

.. code-block:: toml

    # Email validation
    [fields.email]
    context_key = "email"
    type = "str"
    pattern = "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$"
    on_validation_error = "skip"

    # Phone number validation
    [fields.phone]
    type = "str"
    pattern = "^\\d{3}-\\d{3}-\\d{4}$"
    default = "000-000-0000"

    # Alphanumeric code
    [fields.product_code]
    type = "str"
    pattern = "^[A-Z]{3}\\d{4}$"
    default = ""

**Notes:**

- Use double backslashes (``\\``) in TOML for regex escape sequences
- Invalid regex patterns are detected by the ``check`` command
- Patterns are compiled once at configuration load time for performance

Enumeration Constraints
~~~~~~~~~~~~~~~~~~~~~~~

allowed_values
^^^^^^^^^^^^^^

List of allowed values (enumeration validation). Works with any type.

**Example:**

.. code-block:: toml

    # String enumeration
    [fields.membership]
    context_key = "membership"
    type = "str"
    allowed_values = ["free", "premium", "enterprise"]
    default = "free"

    # Integer enumeration
    [fields.priority]
    type = "int"
    allowed_values = [1, 2, 3, 4, 5]
    default = 3

    # Status codes
    [fields.status]
    type = "str"
    allowed_values = ["active", "pending", "inactive", "suspended"]
    on_validation_error = "use_default"
    default = "pending"

List Constraints
~~~~~~~~~~~~~~~~

These constraints apply to list/array types (``list``):

min_items
^^^^^^^^^

Minimum number of items in the list.

**Example:**

.. code-block:: toml

    [fields.tags]
    type = "list"
    min_items = 1
    default = ["general"]

max_items
^^^^^^^^^

Maximum number of items in the list.

**Example:**

.. code-block:: toml

    [fields.recent_items]
    type = "list"
    max_items = 10
    default = []

**Combined Example:**

.. code-block:: toml

    [fields.tags]
    context_key = "tags"
    type = "list"
    min_items = 1
    max_items = 5
    on_validation_error = "use_default"
    default = []

Error Handling Strategies
--------------------------

use_default
~~~~~~~~~~~

Returns the ``default`` value when validation fails. This is the default strategy.

**When to use:**

- You want graceful degradation with fallback values
- Missing or invalid data should not break the application
- You have sensible default values

**Requirements:**

- Must specify a ``default`` value
- The configuration checker warns if default is missing

**Example:**

.. code-block:: toml

    [fields.user_age]
    context_key = "age"
    type = "int"
    min_value = 0
    max_value = 120
    on_validation_error = "use_default"
    default = 0

**Behavior:**

- Invalid type: returns default
- Out of range: returns default
- Pattern mismatch: returns default
- Missing value: returns default

raise
~~~~~

Raises a ``ValidationError`` exception when validation fails.

**When to use:**

- Invalid data should stop execution
- You want to catch and handle validation errors explicitly
- Data integrity is critical

**Example:**

.. code-block:: toml

    [fields.username]
    context_key = "username"
    type = "str"
    min_length = 3
    max_length = 20
    on_validation_error = "raise"

**Python usage:**

.. code-block:: python

    from viewtext import ValidationError, RegistryBuilder

    try:
        registry = RegistryBuilder.build_from_config(config)
        value = registry.get("username")({"username": "ab"})
    except ValidationError as e:
        print(f"Validation failed: {e}")

skip
~~~~

Returns ``None`` when validation fails.

**When to use:**

- Optional fields that should be omitted if invalid
- You want to filter out invalid data
- Downstream code handles None appropriately

**Example:**

.. code-block:: toml

    [fields.email]
    context_key = "email"
    type = "str"
    pattern = "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$"
    on_validation_error = "skip"

**Behavior:**

Returns ``None`` for any validation failure, allowing you to check for and handle missing values.

coerce
~~~~~~

Attempts to convert the value to the expected type before validation.

**When to use:**

- Source data might be in different formats
- You want automatic type conversion
- Data comes from untyped sources (JSON, user input)

**Example:**

.. code-block:: toml

    [fields.score]
    context_key = "score"
    type = "float"
    min_value = 0.0
    max_value = 100.0
    on_validation_error = "coerce"
    default = 0.0

**Coercion Behavior:**

**For ``str``:**

- Any value is converted to string using ``str()``

**For ``int``:**

- ``str`` → ``int``: "123" → 123
- ``float`` → ``int``: 3.14 → 3 (truncates)
- ``bool`` → ``int``: True → 1, False → 0

**For ``float``:**

- ``str`` → ``float``: "3.14" → 3.14
- ``int`` → ``float``: 42 → 42.0
- ``bool`` → ``float``: True → 1.0, False → 0.0

**For ``bool``:**

- Truthy values → True
- Falsy values → False

If coercion fails, falls back to the default value.

Type Validation Details
-----------------------

String Validation
~~~~~~~~~~~~~~~~~

.. code-block:: toml

    [fields.username]
    type = "str"
    min_length = 3
    max_length = 20
    pattern = "^[a-zA-Z0-9_]+$"
    on_validation_error = "raise"

**Checks performed (in order):**

1. Type is string (or coerce to string)
2. Length >= min_length
3. Length <= max_length
4. Matches regex pattern

Integer Validation
~~~~~~~~~~~~~~~~~~

.. code-block:: toml

    [fields.age]
    type = "int"
    min_value = 0
    max_value = 120
    on_validation_error = "use_default"
    default = 0

**Checks performed (in order):**

1. Type is int (or coerce to int)
2. Value >= min_value
3. Value <= max_value

Float Validation
~~~~~~~~~~~~~~~~

.. code-block:: toml

    [fields.temperature]
    type = "float"
    min_value = -273.15
    max_value = 1000.0
    on_validation_error = "use_default"
    default = 0.0

**Checks performed (in order):**

1. Type is float or int (or coerce to float)
2. Value >= min_value
3. Value <= max_value

Boolean Validation
~~~~~~~~~~~~~~~~~~

.. code-block:: toml

    [fields.is_active]
    type = "bool"
    on_validation_error = "coerce"
    default = false

**Coercion rules:**

- Truthy values → True: non-zero numbers, non-empty strings, True
- Falsy values → False: zero, empty string, None, False

List Validation
~~~~~~~~~~~~~~~

.. code-block:: toml

    [fields.tags]
    type = "list"
    min_items = 1
    max_items = 5
    on_validation_error = "use_default"
    default = []

**Checks performed (in order):**

1. Type is list
2. Number of items >= min_items
3. Number of items <= max_items

Dictionary Validation
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: toml

    [fields.metadata]
    type = "dict"
    on_validation_error = "use_default"
    default = {}

**Checks performed:**

1. Type is dictionary

Examples
--------

User Profile Validation
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: toml

    [fields.username]
    context_key = "username"
    type = "str"
    min_length = 3
    max_length = 20
    pattern = "^[a-zA-Z0-9_]+$"
    on_validation_error = "raise"

    [fields.email]
    context_key = "email"
    type = "str"
    pattern = "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$"
    on_validation_error = "skip"

    [fields.age]
    context_key = "age"
    type = "int"
    min_value = 13
    max_value = 120
    on_validation_error = "use_default"
    default = 0

    [fields.membership]
    context_key = "membership"
    type = "str"
    allowed_values = ["free", "premium", "enterprise"]
    on_validation_error = "use_default"
    default = "free"

API Response Validation
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: toml

    [fields.status_code]
    context_key = "status"
    type = "int"
    min_value = 100
    max_value = 599
    on_validation_error = "use_default"
    default = 500

    [fields.response_time]
    context_key = "response_ms"
    type = "float"
    min_value = 0.0
    on_validation_error = "coerce"
    default = 0.0

    [fields.success]
    context_key = "success"
    type = "bool"
    on_validation_error = "coerce"
    default = false

Configuration Validation
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: toml

    [fields.log_level]
    context_key = "log_level"
    type = "str"
    allowed_values = ["debug", "info", "warning", "error", "critical"]
    on_validation_error = "use_default"
    default = "info"

    [fields.max_workers]
    context_key = "workers"
    type = "int"
    min_value = 1
    max_value = 32
    on_validation_error = "use_default"
    default = 4

    [fields.timeout]
    context_key = "timeout"
    type = "float"
    min_value = 0.1
    max_value = 300.0
    on_validation_error = "use_default"
    default = 30.0

Validating Configuration
------------------------

Use the CLI ``check`` command to validate your configuration:

.. code-block:: bash

    viewtext -c config.toml check

The check command validates:

- TOML syntax
- Valid type names
- Valid error handling strategies
- Appropriate constraints for field types
- Valid regex patterns
- Default values when using ``use_default`` strategy
- Field references in layouts

**Example output:**

.. code-block:: text

    ✓ TOML syntax is valid
    ✓ Field registry built successfully

    Checking validation rules...

    Errors (2):
      ✗ Field 'age': unknown type 'integer' (valid types: str, int, float, bool, list, dict, any)
      ✗ Field 'email': invalid regex pattern '^[+$': unterminated character set at position 2

    Warnings (1):
      ⚠ Field 'score': on_validation_error='use_default' but no default value specified

    ✗ Validation failed with 2 error(s)

Testing Field Validation
-------------------------

Use the CLI ``test`` command to test field validation:

.. code-block:: bash

    # Test with valid value
    viewtext -c config.toml test username username=alice

    # Test with invalid value
    viewtext -c config.toml test username username=ab

**Example output:**

.. code-block:: text

    Testing field: username
    Context: {'username': 'ab'}

    Error: Validation failed
    ValidationError: Field 'username' must be at least 3 characters long

Best Practices
--------------

1. **Always specify defaults for optional fields**

   .. code-block:: toml

       [fields.optional_field]
       type = "str"
       on_validation_error = "use_default"
       default = ""

2. **Use raise for critical fields**

   .. code-block:: toml

       [fields.user_id]
       type = "int"
       on_validation_error = "raise"

3. **Use skip for truly optional fields**

   .. code-block:: toml

       [fields.middle_name]
       type = "str"
       on_validation_error = "skip"

4. **Use coerce for flexible input**

   .. code-block:: toml

       [fields.count]
       type = "int"
       on_validation_error = "coerce"
       default = 0

5. **Combine validation with computed fields**

   .. code-block:: toml

       # First validate the input
       [fields.price_validated]
       context_key = "price"
       type = "float"
       min_value = 0.0
       on_validation_error = "use_default"
       default = 0.0

       # Then compute with validated value
       [fields.price_with_tax]
       operation = "linear_transform"
       sources = ["price_validated"]
       multiply = 1.08
       default = 0.0

6. **Test your validation rules**

   Use the ``test`` command to verify validation behavior with sample data.

7. **Run check regularly**

   Add ``viewtext check`` to your CI/CD pipeline to catch configuration errors early.

Common Patterns
---------------

Graceful Degradation
~~~~~~~~~~~~~~~~~~~~

.. code-block:: toml

    [fields.premium_feature]
    context_key = "premium.enabled"
    type = "bool"
    on_validation_error = "use_default"
    default = false

Strict Validation
~~~~~~~~~~~~~~~~~

.. code-block:: toml

    [fields.api_key]
    context_key = "api_key"
    type = "str"
    pattern = "^[A-Za-z0-9]{32}$"
    on_validation_error = "raise"

Optional with Filtering
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: toml

    [fields.optional_email]
    context_key = "email"
    type = "str"
    pattern = "^[a-zA-Z0-9._%+-]+@.*"
    on_validation_error = "skip"

Flexible Input
~~~~~~~~~~~~~~

.. code-block:: toml

    [fields.count]
    context_key = "count"
    type = "int"
    min_value = 0
    on_validation_error = "coerce"
    default = 0

See Also
--------

- :doc:`user_guide` - Field Registry and Configuration
- :doc:`computed_fields_reference` - Computed Field Operations
- :doc:`api_reference` - API Documentation
- ``examples/validation_example.toml`` - Complete validation example
- ``examples/README_validation.md`` - Validation example walkthrough
