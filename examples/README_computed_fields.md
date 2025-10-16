# Computed Fields Example

This example demonstrates how to use computed fields in viewtext to perform calculations
on your data without writing Python code.

## Overview

Computed fields allow you to define operations in TOML configuration that transform and
combine source data. This is useful for:

- Unit conversions (temperature, speed, distance, etc.)
- Mathematical operations (multiply, divide, add, subtract)
- Aggregations (min, max, average)
- Linear transformations (scaling and offsetting values)

## Files

- `computed_fields.toml` - Configuration file with field operations and layouts
- `demo_computed_fields.py` - Demo script showing computed fields in action

## Running the Example

```bash
python examples/demo_computed_fields.py
```

## Available Operations

### Temperature Conversions

- `celsius_to_fahrenheit` - Convert °C to °F
- `fahrenheit_to_celsius` - Convert °F to °C

### Arithmetic Operations

- `multiply` - Multiply two or more values
- `divide` - Divide two values (safe with divide-by-zero handling)
- `add` - Sum multiple values
- `subtract` - Subtract two values
- `modulo` - Modulo operation (remainder after division)

### Aggregate Operations

- `average` - Calculate average of multiple values
- `min` - Find minimum of multiple values
- `max` - Find maximum of multiple values

### Mathematical Operations

- `abs` - Absolute value
- `round` - Round to nearest integer (optionally specify decimals)
- `ceil` - Round up to nearest integer
- `floor` - Round down to nearest integer
- `linear_transform` - Apply formula: `(value * multiply / divide) + add`

### String Operations

- `concat` - Join multiple strings with a separator
- `split` - Split a string by separator and take a specific index
- `substring` - Extract substring from start to end position

### Conditional Operations

- `conditional` - Return different values based on field equality condition

## Example Usage

### Temperature Conversion

```toml
[fields.temp_f]
operation = "celsius_to_fahrenheit"
sources = ["temp_c"]
default = 0.0
```

This field converts a Celsius temperature to Fahrenheit automatically.

### Price Calculation

```toml
[fields.total_price]
operation = "multiply"
sources = ["price", "quantity"]
default = 0.0
```

This field multiplies price by quantity to get the total.

### Discount Calculation

```toml
[fields.discount_price]
operation = "linear_transform"
sources = ["price"]
multiply = 0.8
default = 0.0
```

This field applies a 20% discount by multiplying the price by 0.8.

### Average Score

```toml
[fields.average_score]
operation = "average"
sources = ["score1", "score2", "score3"]
default = 0.0
```

This field calculates the average of three scores.

### Speed Conversion

```toml
[fields.speed_mph]
operation = "linear_transform"
sources = ["speed_kmh"]
multiply = 0.621371
default = 0.0
```

This field converts kilometers per hour to miles per hour.

### Rounding Values

```toml
[fields.vsize_scaled]
operation = "linear_transform"
context_key = "mempool.vsize"
divide = 1000000
default = 0

[fields.vsize_mb]
operation = "ceil"
sources = ["vsize_scaled"]
default = 0
```

This field scales a value and then rounds up to the nearest integer using `ceil`.

### Modulo Operation

```toml
[fields.even_or_odd]
operation = "modulo"
sources = ["number", "divisor"]
default = 0
```

This field calculates the remainder when dividing `number` by `divisor` (e.g., for
checking odd/even).

### Concatenating Strings

```toml
[fields.full_name]
operation = "concat"
sources = ["first_name", "last_name"]
separator = " "
default = ""
```

This field joins first and last names with a space.

### Splitting Strings

```toml
[fields.domain]
operation = "split"
sources = ["email"]
separator = "@"
index = 1
default = ""
```

This field extracts the domain from an email address by splitting on "@" and taking
index 1.

### Extracting Substrings

```toml
[fields.year]
operation = "substring"
sources = ["date"]
start = 0
end = 4
default = ""
```

This field extracts the year from a date string like "2024-01-15" by taking characters
0-4.

### Conditional Logic

```toml
[fields.price_display]
operation = "conditional"
condition = { field = "currency", equals = "USD" }
if_true = "$~amount~"
if_false = "~amount~ ~currency~"
default = ""
```

This field checks if currency is "USD" and displays the price with "$" prefix if true,
otherwise shows the amount with currency code. The `~field_name~` syntax allows
embedding other field values in the output.

## Key Concepts

1. **Sources** - List of field names from the context to use as inputs
2. **Operation** - The operation to perform on the source values
3. **Default** - Value to return if the operation fails or sources are missing
4. **Parameters** - Additional parameters for operations:
   - `multiply` - Multiplier for linear transformations
   - `divide` - Divisor for linear transformations
   - `add` - Addend for linear transformations
   - `separator` - Separator for concat/split operations
   - `index` - Index for split operation
   - `start` - Start position for substring operation
   - `end` - End position for substring operation
   - `condition` - Dictionary with `field` and `equals` for conditional operations
   - `if_true` - Template string to return when condition matches
   - `if_false` - Template string to return when condition doesn't match

## Error Handling

Computed fields include automatic error handling:

- Missing source values return the default
- Non-numeric values return the default (for numeric operations)
- Division by zero returns the default
- Modulo by zero returns the default
- Out-of-bounds string indices return the default
- Invalid operations raise `ValueError` at configuration time

## Benefits

- **Declarative** - Define calculations in configuration, not code
- **Reusable** - Same operations work across different layouts
- **Safe** - Built-in error handling prevents crashes
- **Maintainable** - Easy to understand and modify
- **Fast** - Compiled at configuration load time
