# Template References Example

This example demonstrates how to use `{{field_name}}` template references in computed
fields. Template references allow you to embed field values directly in strings with
custom formatting.

## Features Demonstrated

### Basic Field Substitution

```toml
[inputs.full_name]
operation = "concat"
sources = ["first_name", "last_name"]
separator = " "
```

### Conditional Templates

```toml
[inputs.price_display]
operation = "conditional"
condition = { input = "currency", equals = "USD" }
if_true = "${{price}}"
if_false = "{{price}} {{currency}}"
```

### Multiple Fields in One Template

```toml
[inputs.weather_summary]
operation = "conditional"
condition = { input = "condition", equals = "Sunny" }
if_true = "{{location}}: {{temperature}}°C and {{condition}}"
if_false = "{{location}}: {{temperature}}°C, {{condition}}"
```

### Prefix and Suffix

```toml
[inputs.humidity_display]
operation = "concat"
sources = ["humidity"]
separator = "Humidity: "
suffix = "%"
```

## Running the Example

```bash
python examples/template_references.py
```

## Output

The example demonstrates several use cases:

1. **User Profile Display** - Shows basic field concatenation and conditional formatting
2. **Product Information** - Demonstrates currency formatting and stock status
3. **Weather Report** - Shows conditional templates with multiple field references
4. **Order Status** - Demonstrates handling missing values and different statuses
5. **File System Display** - Shows computed operations combined with templates

## Key Concepts

- **Template References**: Use `{{field_name}}` to embed field values in strings
- **Conditional Logic**: Different templates based on field values
- **Computed Fields**: Combine template references with other operations
- **Default Values**: Handle missing fields gracefully
- **Type Conversion**: Automatic conversion between field types for comparisons

## Configuration Structure

The example uses these main sections:

- `[inputs.*]` - Computed field definitions
- `[formatters.*]` - Output formatting rules
- `[presenters.*]` - Reusable input+formatter combinations
- `[layouts.*]` - Layout definitions using presenters

Template references work in any computed field operation that accepts string templates,
making them a powerful tool for creating dynamic text output.
