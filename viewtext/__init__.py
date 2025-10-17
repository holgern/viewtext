"""
ViewText - Declarative text grid layouts from structured data.

ViewText is a lightweight Python library for building dynamic text-based
grid layouts. It provides a simple, declarative way to map structured data
to formatted text output through a flexible registry and layout system.

Key Components
--------------
- BaseFieldRegistry: Register data getters that extract values from context
- FormatterRegistry: Built-in formatters for text, numbers, prices, dates
- LayoutEngine: Builds grid layouts from TOML configuration and context data
- LayoutLoader: Loads and parses TOML layout configuration files
- RegistryBuilder: Builds field registries from TOML configuration

Examples
--------
>>> from viewtext import LayoutEngine, LayoutLoader, BaseFieldRegistry
>>> registry = BaseFieldRegistry()
>>> registry.register("temperature", lambda ctx: ctx["temp"])
>>> loader = LayoutLoader("layouts.toml")
>>> layout = loader.get_layout("weather")
>>> engine = LayoutEngine(field_registry=registry)
>>> lines = engine.build_line_str(layout, {"temp": 72})
"""

from .engine import LayoutEngine, get_layout_engine
from .formatters import FormatterRegistry, get_formatter_registry
from .loader import LayoutLoader, get_layout_loader
from .registry import BaseFieldRegistry
from .registry_builder import RegistryBuilder, get_registry_from_config
from .validator import FieldValidator, ValidationError


__all__ = [
    "LayoutEngine",
    "get_layout_engine",
    "FormatterRegistry",
    "get_formatter_registry",
    "LayoutLoader",
    "get_layout_loader",
    "BaseFieldRegistry",
    "RegistryBuilder",
    "get_registry_from_config",
    "FieldValidator",
    "ValidationError",
]
