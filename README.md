# ViewText

**Declarative text grid layouts from structured data**

ViewText is a lightweight Python library for building dynamic text-based grid layouts.
It provides a simple, declarative way to map structured data to formatted text output
through a flexible registry and layout system.

## Features

- **Field Registry**: Register data getters that extract values from context objects
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

## Installation

```bash
pip install viewtext
```

## Command Line Interface

Viewtext includes a CLI for inspecting and testing layouts:

```bash
# Show all available layouts
viewtext show-layouts

# Show specific layout configuration
viewtext show-layout weather

# Show field mappings from config
viewtext show-fields

# Render a layout with mock data
viewtext render weather

# Show all available formatters
viewtext show-formatters

# Show configuration info
viewtext info

# Use custom config file
viewtext show-layouts --config my_layouts.toml
```

### CLI Commands

- **show-layouts**: List all layouts in the configuration file
- **show-layout**: Display detailed configuration for a specific layout
- **show-fields**: Display all field mappings from the configuration file
- **render**: Render a layout with mock data
- **show-formatters**: List all available formatters and their descriptions
- **info**: Show configuration file information and global formatters

## License

See LICENSE file in the root directory.
