Presenters Reference
====================

Presenters provide reusable display definitions that bundle an input with a formatter
configuration. They allow layouts to reference the same formatting logic from multiple
lines or items without duplicating parameters.

Presenter Structure
-------------------

Presenters are defined in the ``[presenters]`` section of your TOML configuration.
Each presenter specifies the input it renders, an optional formatter, and any formatter
parameters.

.. code-block:: toml

    [presenters.price_display]
    input = "line_total"
    formatter = "price"
    formatter_params = { symbol = "$", decimals = 2, thousands_sep = "," }

    [presenters.status_badge]
    input = "status"
    formatter = "template"

    [presenters.status_badge.formatter_params]
    template = "{status_icon} {status_text}"
    fields = ["status_icon", "status_text"]

Using Presenters in Layouts
---------------------------

Specify the presenter name on a line or item. If the layout also specifies an input or
formatter, the presenter configuration acts as the default and can be overridden.

.. code-block:: toml

    [[layouts.invoice.lines]]
    presenter = "price_display"
    index = 0

    [[layouts.dashboard.items]]
    key = "status"
    presenter = "status_badge"

Benefits
--------

- **Reuse**: Define formatter parameters once and reference them anywhere.
- **Consistency**: Ensure identical formatting across multiple layouts.
- **Overrides**: Individual layout entries may still override specific settings when
  needed (e.g., change the formatter or input for a special case).

Combination with Inputs and Formatters
--------------------------------------

Presenters work with both global formatter presets and inline formatter parameters. The
resolution order is:

1. Layout-specified formatter parameters
2. Presenter formatter parameters
3. Formatter preset (if referenced by name)

Example Workflow
----------------

1. Define inputs in ``inputs.toml``.
2. Define reusable presenter configurations in the same file or another TOML file.
3. Reference presenters from layouts to keep the layout definitions concise.

See Also
--------

- :doc:`inputs_reference` – complete reference for configuring inputs
- :doc:`formatters_reference` – formatter parameters and examples
- :doc:`user_guide` – walkthrough of layouts, presenters, and CLI usage
