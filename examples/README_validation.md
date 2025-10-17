# Field Validation Example

This example demonstrates viewtext's field validation features, which allow you to
enforce type checking and constraints on field values.

## Features Demonstrated

### Type Validation

Fields can specify an expected type that will be validated and optionally coerced:

```toml
[fields.user_age]
context_key = "age"
type = "int"  # Validates that age is an integer
```

Supported types: `str`, `int`, `float`, `bool`, `list`, `dict`, `any`

### Value Constraints

#### Numeric Constraints

```toml
[fields.user_age]
type = "int"
min_value = 0      # Must be >= 0
max_value = 120    # Must be <= 120
```

#### String Constraints

```toml
[fields.username]
type = "str"
min_length = 3     # Must be at least 3 characters
max_length = 20    # Must be at most 20 characters
```

#### Pattern Matching

```toml
[fields.email]
type = "str"
pattern = "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$"
```

#### Allowed Values

```toml
[fields.membership]
type = "str"
allowed_values = ["free", "premium", "enterprise"]
```

#### List Constraints

```toml
[fields.tags]
type = "list"
min_items = 1      # Must have at least 1 item
max_items = 5      # Must have at most 5 items
```

### Error Handling Strategies

Control what happens when validation fails using `on_validation_error`:

#### `use_default` - Use a fallback value

```toml
[fields.user_age]
min_value = 0
max_value = 120
on_validation_error = "use_default"
default = 0  # Returns 0 if validation fails
```

#### `raise` - Raise an exception

```toml
[fields.username]
min_length = 3
on_validation_error = "raise"  # Throws ValidationError if invalid
```

#### `skip` - Return None

```toml
[fields.email]
pattern = "^[a-zA-Z0-9._%+-]+@.*"
on_validation_error = "skip"  # Returns None if validation fails
```

#### `coerce` - Try to convert the value

```toml
[fields.score]
type = "float"
on_validation_error = "coerce"  # Converts "3.14" to 3.14
default = 0.0
```

## Running This Example

### Check configuration validity

```bash
viewtext -c examples/validation_example.toml check
```

### List fields with validation rules

```bash
viewtext -c examples/validation_example.toml fields
```

### Test a field with validation

```bash
# Valid value
viewtext -c examples/validation_example.toml test username username=alice

# Invalid value (too short) - will raise error
viewtext -c examples/validation_example.toml test username username=ab

# Invalid age - will use default value
viewtext -c examples/validation_example.toml test user_age age=150
```

## Validation Check Output

The `check` command validates your configuration including:

- Valid type declarations
- Valid validation strategies
- Appropriate constraint types for each field type
- Valid regex patterns
- Presence of default values when using `use_default` strategy

Example output:

```
✓ TOML syntax is valid
✓ Field registry built successfully
✓ All checks passed! Configuration is valid.
```

If there are issues, you'll see errors and warnings:

```
Errors (1):
  ✗ Field 'age': unknown type 'integer'

Warnings (1):
  ⚠ Field 'score': on_validation_error='use_default' but no default value is specified
```
