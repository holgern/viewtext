ViewText Documentation
======================

**Declarative text grid layouts from structured data**

ViewText is a lightweight Python library for building dynamic text-based grid layouts.
It provides a simple, declarative way to map structured data to formatted text output
through a flexible registry and layout system.

Features
--------

- **Field Registry**: Register data getters that extract values from context objects
- **Formatter System**: Built-in formatters for text, numbers, prices, dates, and relative times
- **Layout Engine**: TOML-based layout definitions that map fields to grid positions
- **Extensible**: Easy to add custom fields and formatters for domain-specific needs

Use Cases
---------

- Terminal/CLI dashboards
- E-ink/LCD displays
- Text-based data visualization
- Any scenario requiring structured text layouts

Quick Example
-------------

.. code-block:: python

    from viewtext import LayoutEngine, LayoutLoader, BaseFieldRegistry

    # Define your field registry
    registry = BaseFieldRegistry()
    registry.register("temperature", lambda ctx: ctx["temp"])

    # Load layout from TOML
    loader = LayoutLoader("layouts.toml")
    layout = loader.get_layout("weather")

    # Build grid output
    engine = LayoutEngine(field_registry=registry)
    lines = engine.build_line_str(layout, {"temp": 72})

Installation
------------

This library is currently embedded in projects. Future: standalone PyPI package.

Contents
--------

.. toctree::
   :maxdepth: 2

   quickstart
   user_guide
   fields_reference
   validation_reference
   computed_fields_reference
   formatters_reference
   testing
   api_reference
   examples

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
