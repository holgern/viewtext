# Split Configuration Example

This directory demonstrates how to split viewtext configuration into multiple files for
better organization in large projects.

## Files

- **layouts.toml** - Contains only layout definitions
- **formatters.toml** - Contains formatter configurations
- **fields.toml** - Contains field mappings

## Usage

### With CLI

```bash
# Load configuration from split files
viewtext --config examples/split/layouts.toml \
         --formatters examples/split/formatters.toml \
         --fields examples/split/fields.toml \
         list

# Render a layout
viewtext --config examples/split/layouts.toml \
         --formatters examples/split/formatters.toml \
         --fields examples/split/fields.toml \
         render advanced
```

### In Python Code

```python
from viewtext import LayoutLoader

# Method 1: Using constructor parameters
loader = LayoutLoader(
    config_path="examples/split/layouts.toml",
    formatters_path="examples/split/formatters.toml",
    fields_path="examples/split/fields.toml"
)
config = loader.load()

# Method 2: Using static method
config = LayoutLoader.load_from_files(
    layouts_path="examples/split/layouts.toml",
    formatters_path="examples/split/formatters.toml",
    fields_path="examples/split/fields.toml"
)
```

## Benefits

1. **Modularity** - Separate concerns into different files
2. **Reusability** - Share formatters and fields across multiple layout files
3. **Team Collaboration** - Different team members can work on different files
4. **Maintainability** - Easier to find and update specific configurations

## Merging Behavior

When multiple files are provided:

- Fields from `fields.toml` are merged into the base configuration
- Formatters from `formatters.toml` are merged into the base configuration
- If the same key exists in multiple files, the value from the separate file takes
  precedence
- All three files are optional - you can split only the parts you need
