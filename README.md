[![codecov](https://codecov.io/gh/holgern/viewtext/graph/badge.svg?token=AtcFpVooWk)](https://codecov.io/gh/holgern/viewtext)

# ViewText

**Declarative text grid layouts from structured data**

ViewText is a lightweight Python library for building dynamic text-based grid layouts.
It provides a simple, declarative way to map structured data to formatted text output
through a flexible registry and layout system.

## Features

- **Field Registry**: Register data getters that extract values from context objects
- **Computed Fields**: Perform calculations on data (unit conversions, arithmetic,
  aggregates)
- **Formatter System**: Built-in formatters for text, numbers, prices, dates, and
  relative times
- **Layout Engine**: TOML-based layout definitions that map fields to grid positions
- **Extensible**: Easy to add custom fields and formatters for domain-specific needs

## Use Cases

- Terminal/CLI dashboards
- E-ink/LCD displays
- Text-based data visualization
- Any scenario requiring structured text layouts

## Quick Example

```python
from viewtext import LayoutEngine, LayoutLoader, FieldRegistry

# Define your field registry
registry = FieldRegistry()
registry.register("temperature", lambda ctx: ctx["temp"])

# Load layout from TOML
loader = LayoutLoader("layouts.toml")
layout = loader.get_layout("weather")

# Build grid output
engine = LayoutEngine()
lines = engine.build_line_str(layout, {"temp": 72})
```

### Computed Fields

Perform calculations on your data directly in TOML configuration:

```toml
[fields.temperature_f]
operation = "celsius_to_fahrenheit"
sources = ["temp_c"]
default = 0.0

[fields.total_price]
operation = "multiply"
sources = ["price", "quantity"]
default = 0.0

[fields.average_score]
operation = "average"
sources = ["score1", "score2", "score3"]
```

Available operations: `celsius_to_fahrenheit`, `fahrenheit_to_celsius`, `multiply`,
`divide`, `add`, `subtract`, `average`, `min`, `max`, `abs`, `round`, `linear_transform`

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

# Show field mappings from config
viewtext fields

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
- **fields**: Display all field mappings from the configuration file
- **render**: Render a layout with mock data
- **formatters**: List all available formatters and their descriptions
- **templates**: List all template formatters used in layouts
- **info**: Show configuration file information and global formatters

### Global Options

- **--config, -c**: Path to layouts.toml file (can be placed before any command)

## License

See LICENSE file in the root directory.
