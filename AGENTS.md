# Agent Instructions for viewtext

This document provides guidelines for AI agents working on this repository.

## Project Overview

Viewtext is a lightweight Python library for building dynamic text-based grid layouts.
It provides a simple, declarative way to map structured data to formatted text output
through a flexible registry and layout system.

Key features:

- **Field Registry**: Register data getters that extract values from context objects
- **Formatter System**: Built-in formatters for text, numbers, prices, dates, and
  relative times
- **Layout Engine**: TOML-based layout definitions that map fields to grid positions
- **Extensible**: Easy to add custom fields and formatters for domain-specific needs

Use cases include terminal/CLI dashboards, e-ink/LCD displays, text-based data
visualization, and any scenario requiring structured text layouts.

Instructions:

- Never use git commands, you must not commit code

## Installation

### For Development

```bash
pre-commit run --all-files
```

## Documentation

### Building Documentation

The project documentation is built using Sphinx and hosted on ReadTheDocs.

To build the documentation locally:

```bash
python doc/make
```

The generated documentation will be available in the `docs/_build/html` directory.

### API Documentation

When working on the code, please follow these documentation guidelines:

- Use docstrings for all public classes, methods, and functions
- Follow the NumPy docstring format
- Include type hints in function signatures
- Document parameters, return values, and raised exceptions

## Development

### Running Tests

Run all tests using `pytest`.

To run a specific test file: `pytest tests/test_registry.py`

To run a single test function:
`pytest tests/test_registry.py::TestBaseFieldRegistry::test_register_and_get_field`

To run tests with coverage: `pytest --cov=viewtext --cov-report=term`

### Linting and Formatting

This project uses `ruff` for linting and formatting, and `prettier` for other file
types. These are enforced by pre-commit hooks.

Run linting and formatting:
`ruff check --fix --exit-non-zero-on-fix --config=.ruff.toml`

### cli

Do not use `python -m viewtext` to run the cli but `viewtext` directly!

### pip

Do not use `pip install` but `uv pip install`! viewtext is install with `-e .` .

## Project Structure

The project is organized as follows:

```
viewtext/                   # Main package
  ├── __init__.py          # Package initialization and public API
  ├── _version.py          # Version information
  ├── engine.py            # LayoutEngine - builds grid layouts from config
  ├── formatters.py        # FormatterRegistry - text formatting functions
  ├── loader.py            # LayoutLoader - loads TOML layout configs
  ├── registry.py          # BaseFieldRegistry - field registration system
  ├── demo_field_registry.py  # Demo field registry example
  └── demo_generator.py    # Demo layout generator example

tests/                     # Test directory
  ├── __init__.py
  └── test_registry.py     # Tests for BaseFieldRegistry

docs/                      # Documentation
  ├── conf.py             # Sphinx configuration
  ├── make.py             # Documentation build script
  ├── Makefile            # Documentation makefile
  ├── make.bat            # Windows documentation build script
  └── requirements.txt    # Documentation dependencies

layouts.toml               # Example TOML layout configurations
pyproject.toml             # Project metadata and build configuration
setup.py                   # Setup script
requirements.txt           # Package dependencies
requirements-test.txt      # Test dependencies
.ruff.toml                 # Ruff linter/formatter configuration
.pre-commit-config.yaml    # Pre-commit hooks configuration
```

### Key Modules

- **`engine.py`**: Contains `LayoutEngine` class that builds line strings from layout
  configs and context data. It integrates the field registry and formatter registry.

- **`formatters.py`**: Contains `FormatterRegistry` with built-in formatters for text,
  numbers, prices, dates, and relative times. Formatters can be customized with
  parameters.

- **`loader.py`**: Contains `LayoutLoader` for loading and parsing TOML layout
  configuration files. Uses Pydantic models for validation.

- **`registry.py`**: Contains `BaseFieldRegistry` for registering field getter functions
  that extract values from context dictionaries.

## Code Style

- **Formatting**: Adhere to the `ruff` and `prettier` configurations. Maximum line
  length is 88 characters.
- **Imports**: Follow the `isort` configuration in `.ruff.toml`. Imports are grouped
  into `future`, `standard-library`, `third-party`, `first-party`, and `local-folder`.
- **Naming**: Use `snake_case` for functions and variables, and `PascalCase` for
  classes.
- **Types**: Add type hints for all new functions and methods.
- **Error Handling**: Use standard `try...except` blocks for error handling.

## Contribution Guidelines

### TOML Schema

The project includes a JSON Schema for TOML validation located at
`schemas/viewtext.json`.

When adding new fields or properties to TOML configurations:

1. Update the schema in `schemas/viewtext.json`
2. Add new properties, enums, or definitions as needed
3. Test with `taplo check examples/*.toml`
4. Update schema documentation in `schemas/README.md`

The schema provides:

- Validation for field definitions, formatters, and layouts
- Autocomplete in VS Code (with Even Better TOML extension)
- Type checking for TOML configuration files

### Common Issues

When working on the code, be aware of these common issues:

1. TOML configuration parsing: Ensure layout configurations follow the expected schema
   defined in `loader.py` Pydantic models and `.taplo/viewtext-schema.json`
2. Field registry resolution: Fields are resolved first from the field registry, then
   from the context dictionary
3. Formatter parameters: Formatters accept optional parameters that should be validated
   and have sensible defaults
4. Type hints: Ensure proper typing for all functions, especially for context
   dictionaries and layout configurations
5. Schema updates: When adding new operations, transforms, or validation types, update
   the JSON schema
