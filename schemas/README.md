# ViewText JSON Schema

This directory contains the JSON Schema for validating ViewText TOML configuration
files.

## What is this?

The `viewtext.json` file provides schema validation and autocomplete support for
ViewText TOML files in editors that support [Taplo](https://taplo.tamasfe.dev/).

## Supported Editors

- **VS Code**: Install the
  [Even Better TOML](https://marketplace.visualstudio.com/items?itemName=tamasfe.even-better-toml)
  extension
- **Neovim**: Use [taplo LSP](https://github.com/tamasfe/taplo)
- **Other editors**: Any editor with Taplo LSP support

## Features

### Validation

The schema validates:

- **Field definitions**: Ensures proper field structure with required properties

  - Context fields with `context_key`
  - Computed fields with `operation` and `sources`
  - Validation rules (type, constraints)

- **Formatter configurations**: Validates formatter types and parameters

  - Built-in formatters: `text`, `number`, `price`, `datetime`, `relative_time`,
    `template`
  - Formatter-specific parameters

- **Layout definitions**: Validates layout structure
  - Required `name` and `lines` properties
  - Line configurations with `field` and `index`
  - Optional `formatter` and `formatter_params`

### Autocomplete

The schema provides intelligent autocomplete for:

- Field property names
- Operation types (e.g., `celsius_to_fahrenheit`, `multiply`, `linear_transform`)
- Validation types (e.g., `str`, `int`, `float`, `bool`, `list`, `dict`)
- Error handling strategies (e.g., `use_default`, `raise`, `skip`, `coerce`)
- Formatter types
- Transform types (e.g., `upper`, `lower`, `title`)

### Hover Documentation

When hovering over properties in your TOML files, you'll see descriptions of:

- What each property does
- Expected value types
- Valid enum values

## Usage

The schema is automatically applied to TOML files matching the patterns in
`.taplo.toml`:

- `**/layouts*.toml` - Layout configuration files
- `**/fields.toml` - Field-only configuration files
- `**/formatters.toml` - Formatter-only configuration files
- `**/examples/**/*.toml` - Example files
- `**/validation_example.toml` - Validation examples
- `**/computed_fields.toml` - Computed fields examples

## Example

```toml
# The schema will validate this configuration and provide autocomplete

[fields.user_age]
context_key = "age"
type = "int"                    # Autocomplete: str, int, float, bool, list, dict, any
min_value = 0
max_value = 120
on_validation_error = "use_default"  # Autocomplete: use_default, raise, skip, coerce
default = 0

[fields.temp_f]
operation = "celsius_to_fahrenheit"  # Autocomplete: all available operations
sources = ["temp_c"]
default = 0.0

[formatters.price_usd]
type = "price"                  # Autocomplete: text, number, price, datetime, etc.
symbol = "$"
decimals = 2

[layouts.user_info]
name = "User Information"

[[layouts.user_info.lines]]
field = "user_age"
index = 0
formatter = "number"
```

## Schema Location

The schema is located at `.taplo/viewtext-schema.json` relative to the project root.
This location is configured in `.taplo.toml`.

## Updating the Schema

If you add new features to ViewText, update the schema:

1. Edit `.taplo/viewtext-schema.json`
2. Add new properties, enums, or definitions
3. Test with example TOML files
4. Commit the updated schema

## More Information

- [Taplo Documentation](https://taplo.tamasfe.dev/)
- [JSON Schema Specification](https://json-schema.org/)
- [ViewText Documentation](../docs/)
