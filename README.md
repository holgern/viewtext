[![PyPI - Version](https://img.shields.io/pypi/v/viewtext)](https://pypi.org/project/viewtext/)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/viewtext)
![PyPI - Downloads](https://img.shields.io/pypi/dm/viewtext)
[![codecov](https://codecov.io/gh/holgern/viewtext/graph/badge.svg?token=AtcFpVooWk)](https://codecov.io/gh/holgern/viewtext)

# ViewText

**Declarative text grid layouts from structured data**

ViewText is a lightweight Python library for building dynamic text-based grid layouts.
It provides a simple, declarative way to map structured data to formatted text output
through a flexible registry and layout system.

## Features

- **Input Mapping**: Declaratively describe how inputs pull values from context data or
  computed operations
- **Computed Inputs**: Perform calculations on data (unit conversions, arithmetic,
  aggregates) without writing Python code
- **Field Registry**: Register bespoke Python getters for advanced or dynamic data
  extraction needs
- **Formatter System**: Built-in formatters for text, numbers, prices, dates, and
  relative times
- **Layout Engine**: TOML-based layout definitions that map inputs to grid positions
- **Extensible**: Easy to add custom inputs, presenters, and formatters for
  domain-specific needs

## Use Cases

- Terminal/CLI dashboards
- E-ink/LCD displays
- Text-based data visualization
- Any scenario requiring structured text layouts

## Quick Example

```python
from viewtext import LayoutEngine, LayoutLoader, BaseFieldRegistry

# Define your input registry
registry = BaseFieldRegistry()
registry.register("temperature", lambda ctx: ctx["temp"])

# Load layout from TOML (e.g., layouts.toml referencing the "temperature" input)
loader = LayoutLoader("layouts.toml")
layout = loader.get_layout("weather")

# Build grid output using the registered input getter
engine = LayoutEngine(field_registry=registry)
lines = engine.build_line_str(layout, {"temp": 72})
```

### Python Function Inputs

Execute Python code to generate dynamic input values (timestamps, UUIDs, random
numbers):

```toml
# Current timestamp
[inputs.current_time]
python_module = "datetime"
python_function = "datetime.datetime.now().timestamp()"
transform = "int"
default = 0

# Generate UUID
[inputs.request_id]
python_module = "uuid"
python_function = "str(uuid.uuid4())"
default = ""

# Random number
[inputs.random_value]
python_module = "random"
python_function = "random.randint(1, 100)"
default = 0
```

See `examples/time_diff_example.toml` and `examples/README_time_diff.md` for more
details.

### Computed Inputs

Perform calculations on your data directly in TOML configuration:

```toml
[inputs.temperature_f]
operation = "celsius_to_fahrenheit"
sources = ["temp_c"]
default = 0.0

[inputs.total_price]
operation = "multiply"
sources = ["price", "quantity"]
default = 0.0

[inputs.average_score]
operation = "average"
sources = ["score1", "score2", "score3"]
```

### Available Operations

**Temperature Conversions:**

- `celsius_to_fahrenheit` - Convert Celsius to Fahrenheit
- `fahrenheit_to_celsius` - Convert Fahrenheit to Celsius

**Arithmetic Operations:**

- `multiply` - Multiply values
- `divide` - Divide values
- `add` - Add values
- `subtract` - Subtract values
- `modulo` - Modulo operation

**Aggregate Operations:**

- `average` - Calculate average of values
- `min` - Find minimum value
- `max` - Find maximum value

**Math Operations:**

- `abs` - Absolute value
- `round` - Round to specified decimals
- `floor` - Round down to nearest integer
- `ceil` - Round up to nearest integer

**String Operations:**

- `concat` - Concatenate strings with separator, prefix, suffix, and skip_empty options
- `split` - Split string by separator and get index
- `substring` - Extract substring with start/end indices

**Formatting Operations:**

- `format_number` - Format numbers with thousands/decimal separators

**Transform Operations:**

- `linear_transform` - Apply linear transformation (multiply, divide, add)

**Conditional Operations:**

- `conditional` - If/else logic with input references

See `examples/computed_fields.toml` and `examples/README_computed_fields.md` for more
details.

## Installation

```bash
pip install viewtext
```

## Command Line Interface

Viewtext includes a CLI for inspecting and testing layouts:

```bash
# Show all available layouts
viewtext list

# Show specific layout configuration
viewtext show weather

# Show input mappings from config
viewtext inputs

# Evaluate inputs (works with input-only configs)
viewtext render-inputs

# Render a layout with mock data
viewtext render weather

# Show all available formatters
viewtext formatters

# Show all template formatters in config
viewtext templates

# Show configuration info
viewtext info

# Use custom config file (global option)
viewtext -c my_layouts.toml list
viewtext --config examples/layouts.toml show weather
```

### CLI Commands

- **list**: List all layouts in the configuration file
- **show**: Display detailed configuration for a specific layout
- **inputs**: Display all input mappings from the configuration file
- **render**: Render a layout with mock data
- **render-inputs**: Evaluate configured inputs (works even when no layouts are defined)
- **formatters**: List all available formatters and their descriptions
- **templates**: List all template formatters used in layouts
- **test**: Test individual inputs with custom context values and formatters
- **info**: Show configuration file information and global formatters
- **generate-inputs**: Auto-generate input definitions from JSON data

### Testing Inputs

The `test` command allows you to test individual inputs with custom values:

```bash
# Test a computed input
viewtext test total_price price=19.99 quantity=3

# Test with a formatter
viewtext test temp_f temp_c=25 --formatter temperature

# Test template formatters (requires --layout option)
viewtext test current_price \
  'current_price={"fiat": "€1.234", "usd": 1.15, "sat_usd": 115000}' \
  --formatter template --layout crypto_composite_price
```

### JSON Pipeline Support

Pipe JSON data from external sources directly to ViewText:

```bash
# From API
curl -s https://api.example.com/data | viewtext render layout --json

# From Python
python3 -c "import json; print(json.dumps({'input': 'value'}))" | viewtext render layout --json

# From file with jq
cat data.json | jq '.users[0]' | viewtext render layout --json

# Live dashboard
watch -n 5 'curl -s API_URL | viewtext -c config.toml render layout --json'
```

See `examples/json_pipeline_example.md` for detailed examples and use cases.

### Auto-Generating Input Definitions

ViewText can automatically generate input definitions from JSON data:

```bash
# Generate inputs from API response
curl -s https://api.example.com/data | viewtext generate-inputs

# Save to file
echo '{"name": "John", "age": 30}' | viewtext generate-inputs -o inputs.toml

# Add prefix to input names
curl -s https://api.example.com/user | viewtext generate-inputs --prefix "api_"

# Nested JSON objects are flattened
echo '{"user": {"name": "Alice", "age": 25}}' | viewtext generate-inputs
# Creates: user_name with context_key="user.name"
```

The command automatically infers types (`str`, `int`, `float`, `bool`, `list`, `dict`,
`any`) and creates properly formatted TOML input definitions.

### Global Options

- **--config, -c**: Path to layouts.toml file (can be placed before any command)

## Editor Support

ViewText provides a JSON Schema for TOML validation and autocomplete. Install the
[Even Better TOML](https://marketplace.visualstudio.com/items?itemName=tamasfe.even-better-toml)
extension in VS Code or use Taplo LSP in other editors for:

- **Validation**: Catch errors in input definitions, formatters, and layouts
- **Autocomplete**: Get intelligent suggestions for property names and values
- **Hover Documentation**: View descriptions of all configuration options

The schema is automatically configured in `.taplo.toml` for all layout files.

## Documentation

Full documentation is available at [Read the Docs](https://viewtext.readthedocs.io/):

- [Quick Start Guide](https://viewtext.readthedocs.io/en/latest/quickstart.html) - Get
  started quickly
- [User Guide](https://viewtext.readthedocs.io/en/latest/user_guide.html) - Core
  concepts and features
- [Inputs Reference](https://viewtext.readthedocs.io/en/latest/inputs_reference.html) -
  Complete input definition reference
- [Validation Reference](https://viewtext.readthedocs.io/en/latest/validation_reference.html) -
  Field validation and type checking
- [Computed Inputs Reference](https://viewtext.readthedocs.io/en/latest/computed_fields_reference.html) -
  Complete list of data transformation operations
- [Formatters Reference](https://viewtext.readthedocs.io/en/latest/formatters_reference.html) -
  Complete list of display formatters with examples
- [API Reference](https://viewtext.readthedocs.io/en/latest/api_reference.html) - Python
  API documentation
- [Examples](https://viewtext.readthedocs.io/en/latest/examples.html) - Real-world
  examples and use cases

## License

See LICENSE file in the root directory.
