#!/usr/bin/env python3

import importlib
import json
import re
import sys
from pathlib import Path
from typing import Any, Optional

import typer
from rich.console import Console
from rich.table import Table

from .engine import LayoutEngine
from .formatters import get_formatter_registry
from .loader import LayoutLoader
from .registry_builder import get_registry_from_config

app = typer.Typer(help="ViewText CLI - Text grid layout generator")
console = Console()

config_path: str = "layouts.toml"


@app.callback()
def main_callback(
    ctx: typer.Context,
    config: str = typer.Option(
        "layouts.toml", "--config", "-c", help="Path to layouts.toml file"
    ),
    formatters: Optional[str] = typer.Option(
        None, "--formatters", "-f", help="Path to formatters.toml file"
    ),
    fields: Optional[str] = typer.Option(
        None, "--fields", "-F", help="Path to fields.toml file"
    ),
) -> None:
    global config_path
    config_path = config
    ctx.obj = {"config": config, "formatters": formatters, "fields": fields}


def create_mock_context() -> dict[str, Any]:
    return {
        "demo1": "Hello",
        "demo2": "World",
        "demo3": "Viewtext",
        "demo4": "Demo",
        "text_value": "Sample Text",
        "number_value": 12345.67,
        "price_value": 99.99,
        "timestamp": 1729012345,
    }


@app.command(name="list")
def list_layouts(ctx: typer.Context) -> None:
    config = config_path
    formatters_path = ctx.obj.get("formatters")
    fields_path = ctx.obj.get("fields")
    try:
        loader = LayoutLoader(config, formatters_path, fields_path)
        layouts_config = loader.load()

        console.print(f"\n[bold green]Configuration File:[/bold green] {config}\n")
        if formatters_path:
            console.print(
                f"[bold green]Formatters File:[/bold green] {formatters_path}"
            )
        if fields_path:
            console.print(f"[bold green]Fields File:[/bold green] {fields_path}")
        console.print()

        if not layouts_config.layouts:
            console.print("[yellow]No layouts found in configuration file[/yellow]")
            return

        table = Table(title="Available Layouts", show_header=True, header_style="bold")
        table.add_column("Layout Name", style="cyan", width=30)
        table.add_column("Display Name", style="green", width=40)
        table.add_column("Lines", justify="right", style="magenta")

        for layout_name, layout_config in sorted(layouts_config.layouts.items()):
            display_name = layout_config.name
            num_lines = len(layout_config.lines)
            table.add_row(layout_name, display_name, str(num_lines))

        console.print(table)
        console.print(f"\n[bold]Total layouts:[/bold] {len(layouts_config.layouts)}\n")

    except FileNotFoundError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(code=1) from None
    except Exception as e:
        console.print(f"[red]Error loading layouts:[/red] {e}")
        raise typer.Exit(code=1) from None


@app.command(name="show")
def show_layout(
    ctx: typer.Context,
    layout_name: str = typer.Argument(..., help="Name of the layout to display"),
) -> None:
    config = config_path
    formatters_path = ctx.obj.get("formatters")
    fields_path = ctx.obj.get("fields")
    try:
        loader = LayoutLoader(config, formatters_path, fields_path)
        layout = loader.get_layout(layout_name)

        console.print(
            f"\n[bold green]Layout:[/bold green] {layout_name} - {layout['name']}\n"
        )

        table = Table(show_header=True, header_style="bold")
        table.add_column("Index", justify="right", style="cyan", width=8)
        table.add_column("Field", style="green", width=25)
        table.add_column("Formatter", style="yellow", width=20)
        table.add_column("Parameters", style="magenta")

        for line in layout.get("lines", []):
            index = str(line.get("index", ""))
            field = line.get("field", "")
            formatter = line.get("formatter", "")
            params = line.get("formatter_params", {})
            params_str = str(params) if params else ""

            table.add_row(index, field, formatter, params_str)

        console.print(table)
        console.print(f"\n[bold]Total lines:[/bold] {len(layout.get('lines', []))}\n")

    except ValueError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(code=1) from None
    except FileNotFoundError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(code=1) from None
    except Exception as e:
        console.print(f"[red]Error displaying layout:[/red] {e}")
        raise typer.Exit(code=1) from None


@app.command()
def render(
    ctx: typer.Context,
    layout_name: str = typer.Argument(..., help="Name of the layout to render"),
    field_registry: Optional[str] = typer.Option(
        None, "--registry", "-r", help="Custom field registry module path"
    ),
    json_output: bool = typer.Option(
        False, "--json", "-j", help="Output rendered lines as JSON"
    ),
) -> None:
    config = config_path
    formatters_path = ctx.obj.get("formatters")
    fields_path = ctx.obj.get("fields")
    try:
        loader = LayoutLoader(config, formatters_path, fields_path)
        layout = loader.get_layout(layout_name)

        if field_registry:
            console.print(
                "[yellow]Custom registry support not yet implemented[/yellow]"
            )
            registry = None
        else:
            registry = get_registry_from_config(loader=loader)

        engine = LayoutEngine(field_registry=registry, layout_loader=loader)

        has_stdin_data = not sys.stdin.isatty()

        if has_stdin_data:
            try:
                json_data = sys.stdin.read()
                if json_data.strip():
                    context = json.loads(json_data)
                else:
                    raise ValueError("Empty stdin")
            except (json.JSONDecodeError, ValueError):
                context_provider_path = loader.get_context_provider()
                if context_provider_path:
                    try:
                        module_name, func_name = context_provider_path.rsplit(".", 1)
                        module = importlib.import_module(module_name)
                        context_func = getattr(module, func_name)
                        context = context_func()
                    except (ValueError, ImportError, AttributeError) as e:
                        msg = (
                            f"Error loading context provider '{context_provider_path}'"
                        )
                        console.print(f"[red]{msg}:[/red] {e}")
                        raise typer.Exit(code=1) from None
                    except Exception as e:
                        msg = (
                            f"Error calling context provider '{context_provider_path}'"
                        )
                        console.print(f"[red]{msg}:[/red] {e}")
                        raise typer.Exit(code=1) from None
                else:
                    context = create_mock_context()
        else:
            context_provider_path = loader.get_context_provider()
            if context_provider_path:
                try:
                    module_name, func_name = context_provider_path.rsplit(".", 1)
                    module = importlib.import_module(module_name)
                    context_func = getattr(module, func_name)
                    context = context_func()
                except (ValueError, ImportError, AttributeError) as e:
                    msg = f"Error loading context provider '{context_provider_path}'"
                    console.print(f"[red]{msg}:[/red] {e}")
                    raise typer.Exit(code=1) from None
                except Exception as e:
                    msg = f"Error calling context provider '{context_provider_path}'"
                    console.print(f"[red]{msg}:[/red] {e}")
                    raise typer.Exit(code=1) from None
            else:
                context = create_mock_context()

        lines = engine.build_line_str(layout, context)

        if json_output:
            print(json.dumps(lines, indent=2))
        else:
            console.print(
                f"\n[bold green]Rendered Output:[/bold green] {layout_name}\n"
            )
            console.print("[dim]" + "─" * 80 + "[/dim]")

            for i, line in enumerate(lines):
                console.print(f"[cyan]{i}:[/cyan] {line}")

            console.print("[dim]" + "─" * 80 + "[/dim]\n")

    except ValueError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(code=1) from None
    except FileNotFoundError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(code=1) from None
    except Exception as e:
        console.print(f"[red]Error rendering layout:[/red] {e}")
        raise typer.Exit(code=1) from None


@app.command(name="fields")
def list_fields(ctx: typer.Context) -> None:
    config = config_path
    formatters_path = ctx.obj.get("formatters")
    fields_path = ctx.obj.get("fields")
    try:
        loader = LayoutLoader(config, formatters_path, fields_path)
        field_mappings = loader.get_field_mappings()

        console.print(f"\n[bold green]Configuration File:[/bold green] {config}\n")
        if fields_path:
            console.print(f"[bold green]Fields File:[/bold green] {fields_path}\n")

        if not field_mappings:
            console.print(
                "[yellow]No field mappings found in configuration file[/yellow]"
            )
            return

        table = Table(title="Field Mappings", show_header=True, header_style="bold")
        table.add_column("Field Name", style="cyan", overflow="fold")
        table.add_column("Context Key", style="green", overflow="fold")
        table.add_column("Operation", style="blue", overflow="fold")
        table.add_column("Parameters", style="magenta", overflow="fold")
        table.add_column("Default", style="yellow", overflow="fold")
        table.add_column("Transform", style="magenta", overflow="fold")

        for field_name, mapping in sorted(field_mappings.items()):
            context_key = mapping.context_key if mapping.context_key else ""
            operation = mapping.operation if mapping.operation else ""
            default = str(mapping.default) if mapping.default is not None else ""
            transform = mapping.transform if mapping.transform else ""

            params_parts = []
            if mapping.sources:
                params_parts.append(f"sources={mapping.sources}")
            if mapping.multiply is not None:
                params_parts.append(f"multiply={mapping.multiply}")
            if mapping.add is not None:
                params_parts.append(f"add={mapping.add}")
            if mapping.divide is not None:
                params_parts.append(f"divide={mapping.divide}")
            if mapping.separator is not None:
                params_parts.append(f"separator={repr(mapping.separator)}")
            if mapping.prefix is not None:
                params_parts.append(f"prefix={repr(mapping.prefix)}")
            if mapping.suffix is not None:
                params_parts.append(f"suffix={repr(mapping.suffix)}")
            if mapping.start is not None:
                params_parts.append(f"start={mapping.start}")
            if mapping.end is not None:
                params_parts.append(f"end={mapping.end}")
            if mapping.index is not None:
                params_parts.append(f"index={mapping.index}")
            if mapping.skip_empty is not None:
                params_parts.append(f"skip_empty={mapping.skip_empty}")
            if mapping.condition is not None:
                params_parts.append(f"condition={mapping.condition}")
            if mapping.if_true is not None:
                params_parts.append(f"if_true={repr(mapping.if_true)}")
            if mapping.if_false is not None:
                params_parts.append(f"if_false={repr(mapping.if_false)}")
            if mapping.decimals_param is not None:
                params_parts.append(f"decimals={mapping.decimals_param}")
            if mapping.thousands_sep is not None:
                params_parts.append(f"thousands_sep={repr(mapping.thousands_sep)}")
            if mapping.decimal_sep is not None:
                params_parts.append(f"decimal_sep={repr(mapping.decimal_sep)}")

            params_str = ", ".join(params_parts)

            table.add_row(
                field_name, context_key, operation, params_str, default, transform
            )

        console.print(table)
        console.print(f"\n[bold]Total fields:[/bold] {len(field_mappings)}\n")

    except FileNotFoundError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(code=1) from None
    except Exception as e:
        console.print(f"[red]Error loading field mappings:[/red] {e}")
        raise typer.Exit(code=1) from None


@app.command(name="formatters")
def list_formatters() -> None:
    get_formatter_registry()

    console.print("\n[bold]Available Formatters[/bold]\n")

    table = Table(show_header=True, header_style="bold")
    table.add_column("Formatter", style="cyan", width=20)
    table.add_column("Description", style="green")

    formatters = {
        "text": "Simple text formatter with optional prefix/suffix",
        "text_uppercase": "Converts text to uppercase",
        "price": "Formats numeric values as prices with symbol and decimals",
        "number": "Formats numbers with optional prefix/suffix and decimals",
        "datetime": "Formats datetime objects or timestamps",
        "relative_time": 'Formats time intervals as relative time (e.g., "5m ago")',
        "template": "Combines multiple fields using a template string",
    }

    for formatter_name in sorted(formatters.keys()):
        description = formatters[formatter_name]
        table.add_row(formatter_name, description)

    console.print(table)
    console.print(f"\n[bold]Total formatters:[/bold] {len(formatters)}\n")


@app.command(name="templates")
def list_templates(ctx: typer.Context) -> None:
    config = config_path
    formatters_path = ctx.obj.get("formatters")
    fields_path = ctx.obj.get("fields")
    try:
        loader = LayoutLoader(config, formatters_path, fields_path)
        layouts_config = loader.load()

        console.print(f"\n[bold green]Configuration File:[/bold green] {config}\n")

        template_lines = []
        for layout_name, layout_config in layouts_config.layouts.items():
            for line in layout_config.lines:
                if line.formatter == "template":
                    template_lines.append(
                        {
                            "layout": layout_name,
                            "layout_name": layout_config.name,
                            "field": line.field,
                            "index": line.index,
                            "template": line.formatter_params.get("template", ""),
                            "fields": line.formatter_params.get("fields", []),
                        }
                    )

        if not template_lines:
            console.print(
                "[yellow]No template formatters found in configuration file[/yellow]"
            )
            return

        table = Table(
            title="Template Formatters", show_header=True, header_style="bold"
        )
        table.add_column("Layout", style="cyan", overflow="fold")
        table.add_column("Field", style="green", overflow="fold")
        table.add_column("Template", style="yellow", overflow="fold", width=40)
        table.add_column("Fields Used", style="magenta", overflow="fold")

        for item in template_lines:
            fields_str = ", ".join(item["fields"])
            table.add_row(
                f"{item['layout']}\n({item['layout_name']})",
                item["field"],
                item["template"],
                fields_str,
            )

        console.print(table)
        console.print(
            f"\n[bold]Total template formatters:[/bold] {len(template_lines)}\n"
        )

    except FileNotFoundError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(code=1) from None
    except Exception as e:
        console.print(f"[red]Error loading templates:[/red] {e}")
        raise typer.Exit(code=1) from None


@app.command(name="test")
def test_field(
    ctx: typer.Context,
    field_name: str = typer.Argument(..., help="Name of the field to test"),
    context_values: list[str] = typer.Argument(
        None, help="Context values in format key=value (e.g., membership=premium)"
    ),
    formatter: Optional[str] = typer.Option(
        None, "--formatter", "-F", help="Formatter to apply to the result"
    ),
    layout: Optional[str] = typer.Option(
        None,
        "--layout",
        "-l",
        help="Layout name to use for formatter parameters "
        "(e.g., for template formatters)",
    ),
) -> None:
    config = config_path
    formatters_path = ctx.obj.get("formatters")
    fields_path = ctx.obj.get("fields")
    try:
        loader = LayoutLoader(config, formatters_path, fields_path)
        field_mappings = loader.get_field_mappings()

        if field_name not in field_mappings:
            console.print(f"[red]Error:[/red] Field '{field_name}' not found")
            available = ", ".join(sorted(field_mappings.keys()))
            console.print(f"\n[yellow]Available fields:[/yellow] {available}")
            raise typer.Exit(code=1) from None

        context = {}
        if context_values:
            for value_str in context_values:
                if "=" not in value_str:
                    console.print(
                        f"[red]Error:[/red] Invalid context value '{value_str}'. "
                        f"Expected format: key=value"
                    )
                    raise typer.Exit(code=1) from None
                key, value = value_str.split("=", 1)
                try:
                    import ast

                    context[key] = ast.literal_eval(value)
                except (ValueError, SyntaxError):
                    context[key] = value

        registry = get_registry_from_config(loader=loader)

        console.print(f"\n[bold green]Testing Field:[/bold green] {field_name}\n")

        mapping = field_mappings[field_name]
        console.print(f"[bold]Operation:[/bold] {mapping.operation or 'None'}")
        if mapping.sources:
            console.print(f"[bold]Sources:[/bold] {', '.join(mapping.sources)}")
        console.print(f"[bold]Default:[/bold] {mapping.default}")
        if formatter:
            console.print(f"[bold]Formatter:[/bold] {formatter}")
        if layout:
            console.print(f"[bold]Layout:[/bold] {layout}")
        console.print()

        console.print("[bold]Context:[/bold]")
        if context:
            for key, value in context.items():
                console.print(f"  {key} = {repr(value)}")
        else:
            console.print("  [dim](empty)[/dim]")

        if registry and registry.has_field(field_name):
            getter = registry.get(field_name)
            result = getter(context)
        elif field_name in context:
            result = context[field_name]
        else:
            result = mapping.default
        console.print(f"\n[bold green]Result:[/bold green] {repr(result)}")

        if formatter:
            formatter_registry = get_formatter_registry()
            layouts_config = loader.load()
            formatter_type = formatter
            formatter_params = {}

            if layout:
                if layout not in layouts_config.layouts:
                    console.print(f"[red]Error:[/red] Layout '{layout}' not found")
                    available = ", ".join(sorted(layouts_config.layouts.keys()))
                    console.print(f"\n[yellow]Available layouts:[/yellow] {available}")
                    raise typer.Exit(code=1) from None

                layout_config = layouts_config.layouts[layout]
                matching_line = None
                for line in layout_config.lines:
                    if line.field == field_name and line.formatter == formatter:
                        matching_line = line
                        break

                if matching_line and matching_line.formatter_params:
                    formatter_params = matching_line.formatter_params
                    console.print("\n[bold]Formatter Parameters:[/bold]")
                    if "template" in formatter_params:
                        console.print(f"  template: {formatter_params['template']}")
                    if "fields" in formatter_params:
                        console.print(
                            f"  fields: {', '.join(formatter_params['fields'])}"
                        )
                    if formatter_params.keys() - {"template", "fields"}:
                        for key, val in formatter_params.items():
                            if key not in ["template", "fields"]:
                                console.print(f"  {key}: {val}")
                    console.print()
                elif not matching_line:
                    console.print(
                        f"[yellow]Warning:[/yellow] Field '{field_name}' with "
                        f"formatter '{formatter}' not found in layout "
                        f"'{layout}'\n"
                    )
            elif layouts_config.formatters and formatter in layouts_config.formatters:
                formatter_config = layouts_config.formatters[formatter]
                formatter_type = formatter_config.type
                formatter_params = formatter_config.model_dump(exclude_none=True)
                formatter_params.pop("type", None)

            if formatter_type == "template" and not formatter_params.get("template"):
                console.print(
                    "[yellow]Hint:[/yellow] Template formatter requires "
                    "'template' and 'fields' parameters.\n"
                    "       Use --layout option to specify a layout that "
                    "uses this formatter.\n"
                    f"       Example: viewtext test {field_name} "
                    f"--formatter {formatter} --layout <layout_name>\n"
                )

            try:
                formatter_func = formatter_registry.get(formatter_type)
                format_value = result

                if (
                    formatter_type == "template"
                    and "fields" in formatter_params
                    and isinstance(result, dict)
                ):
                    fields_list = formatter_params.get("fields", [])
                    if fields_list and "." in fields_list[0]:
                        common_prefix = fields_list[0].split(".")[0]
                        if all(f.startswith(common_prefix + ".") for f in fields_list):
                            if common_prefix not in result or not isinstance(
                                result.get(common_prefix), dict
                            ):
                                format_value = {common_prefix: result}

                formatted_result = formatter_func(format_value, **formatter_params)
                console.print(
                    f"[bold green]Formatted:[/bold green] {repr(formatted_result)}"
                )
            except ValueError:
                console.print(f"[red]Error:[/red] Unknown formatter '{formatter_type}'")
                raise typer.Exit(code=1) from None
            except Exception as e:
                console.print(f"[red]Error:[/red] {e}")
                raise typer.Exit(code=1) from None

    except typer.Exit:
        raise
    except FileNotFoundError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(code=1) from None
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(code=1) from None


@app.command()
def check(ctx: typer.Context) -> None:
    config = config_path
    formatters_path = ctx.obj.get("formatters")
    fields_path = ctx.obj.get("fields")

    errors = []
    warnings = []
    registry = None

    try:
        config_file = Path(config)

        console.print("\n[bold]ViewText Configuration Validation[/bold]\n")
        console.print(f"[bold]Config File:[/bold] {config_file.absolute()}")
        if formatters_path:
            console.print(f"[bold]Formatters File:[/bold] {formatters_path}")
        if fields_path:
            console.print(f"[bold]Fields File:[/bold] {fields_path}")
        console.print()

        if not config_file.exists():
            console.print(f"[red]✗ Config file not found:[/red] {config_file}\n")
            raise typer.Exit(code=1) from None

        try:
            loader = LayoutLoader(str(config_file), formatters_path, fields_path)
            layouts_config = loader.load()
            console.print("[green]✓ TOML syntax is valid[/green]")
        except Exception as e:
            console.print(f"[red]✗ TOML syntax error:[/red] {e}\n")
            raise typer.Exit(code=1) from None

        try:
            registry = get_registry_from_config(loader=loader)
            console.print("[green]✓ Field registry built successfully[/green]")
        except Exception as e:
            errors.append(f"Failed to build field registry: {e}")
            console.print(f"[red]✗ Field registry error:[/red] {e}")

        formatter_registry = get_formatter_registry()
        builtin_formatters = {
            "text",
            "text_uppercase",
            "price",
            "number",
            "datetime",
            "relative_time",
            "template",
        }

        defined_fields = (
            set(layouts_config.fields.keys()) if layouts_config.fields else set()
        )
        defined_formatters = (
            set(layouts_config.formatters.keys())
            if layouts_config.formatters
            else set()
        )
        all_formatters = builtin_formatters | defined_formatters

        for layout_name, layout_config in layouts_config.layouts.items():
            for line_idx, line in enumerate(layout_config.lines):
                field_name = line.field

                if registry and not registry.has_field(field_name):
                    if field_name not in defined_fields:
                        warnings.append(
                            f"Layout '{layout_name}', line {line_idx}: "
                            f"field '{field_name}' not defined in field registry"
                        )

                if line.formatter:
                    if line.formatter not in all_formatters:
                        errors.append(
                            f"Layout '{layout_name}', line {line_idx}: "
                            f"unknown formatter '{line.formatter}'"
                        )
                    else:
                        try:
                            formatter_registry.get(line.formatter)
                        except ValueError:
                            if (
                                line.formatter in defined_formatters
                                and layouts_config.formatters
                            ):
                                formatter_config = layouts_config.formatters[
                                    line.formatter
                                ]
                                formatter_type = formatter_config.type
                                try:
                                    formatter_registry.get(formatter_type)
                                except ValueError:
                                    errors.append(
                                        f"Layout '{layout_name}', line {line_idx}: "
                                        f"formatter '{line.formatter}' has unknown "
                                        f"type '{formatter_type}'"
                                    )

                    if line.formatter == "template" or (
                        line.formatter in defined_formatters
                        and layouts_config.formatters
                        and layouts_config.formatters[line.formatter].type == "template"
                    ):
                        if not line.formatter_params.get("template"):
                            errors.append(
                                f"Layout '{layout_name}', line {line_idx}: "
                                f"template formatter missing 'template' parameter"
                            )
                        if not line.formatter_params.get("fields"):
                            errors.append(
                                f"Layout '{layout_name}', line {line_idx}: "
                                f"template formatter missing 'fields' parameter"
                            )
                        else:
                            template_fields = line.formatter_params.get("fields", [])
                            for tf in template_fields:
                                base_field = tf.split(".")[0]
                                if (
                                    base_field != field_name
                                    and base_field not in defined_fields
                                ):
                                    warnings.append(
                                        f"Layout '{layout_name}', line {line_idx}: "
                                        f"template references undefined field "
                                        f"'{base_field}'"
                                    )

        if layouts_config.fields:
            for field_name, field_mapping in layouts_config.fields.items():
                if field_mapping.type:
                    valid_types = {"str", "int", "float", "bool", "list", "dict", "any"}
                    if field_mapping.type not in valid_types:
                        errors.append(
                            f"Field '{field_name}': unknown type '{field_mapping.type}'"
                        )

                if field_mapping.on_validation_error:
                    valid_strategies = {"raise", "skip", "use_default", "coerce"}
                    if field_mapping.on_validation_error not in valid_strategies:
                        errors.append(
                            f"Field '{field_name}': unknown on_validation_error "
                            f"strategy '{field_mapping.on_validation_error}'"
                        )

                if (
                    field_mapping.min_value is not None
                    or field_mapping.max_value is not None
                ):
                    if field_mapping.type and field_mapping.type not in {
                        "int",
                        "float",
                        "any",
                    }:
                        warnings.append(
                            f"Field '{field_name}': min_value/max_value constraints "
                            f"are typically used with numeric types (int/float), "
                            f"but field has type '{field_mapping.type}'"
                        )

                if (
                    field_mapping.min_length is not None
                    or field_mapping.max_length is not None
                ):
                    if field_mapping.type and field_mapping.type not in {"str", "any"}:
                        warnings.append(
                            f"Field '{field_name}': min_length/max_length constraints "
                            f"are typically used with string types, "
                            f"but field has type '{field_mapping.type}'"
                        )

                if (
                    field_mapping.min_items is not None
                    or field_mapping.max_items is not None
                ):
                    if field_mapping.type and field_mapping.type not in {"list", "any"}:
                        warnings.append(
                            f"Field '{field_name}': min_items/max_items constraints "
                            f"are typically used with list types, "
                            f"but field has type '{field_mapping.type}'"
                        )

                if field_mapping.pattern is not None:
                    if field_mapping.type and field_mapping.type not in {"str", "any"}:
                        warnings.append(
                            f"Field '{field_name}': pattern constraint "
                            f"is typically used with string types, "
                            f"but field has type '{field_mapping.type}'"
                        )
                    else:
                        try:
                            re.compile(field_mapping.pattern)
                        except re.error as e:
                            errors.append(
                                f"Field '{field_name}': invalid regex pattern "
                                f"'{field_mapping.pattern}': {e}"
                            )

                if (
                    field_mapping.on_validation_error == "use_default"
                    and field_mapping.default is None
                ):
                    warnings.append(
                        f"Field '{field_name}': on_validation_error='use_default' "
                        f"but no default value is specified"
                    )

                if field_mapping.operation:
                    valid_operations = {
                        "celsius_to_fahrenheit",
                        "fahrenheit_to_celsius",
                        "multiply",
                        "divide",
                        "add",
                        "subtract",
                        "average",
                        "min",
                        "max",
                        "abs",
                        "round",
                        "ceil",
                        "floor",
                        "modulo",
                        "linear_transform",
                        "concat",
                        "split",
                        "substring",
                        "conditional",
                        "format_number",
                    }
                    if field_mapping.operation not in valid_operations:
                        errors.append(
                            f"Field '{field_name}': unknown operation "
                            f"'{field_mapping.operation}'"
                        )

                    if field_mapping.sources:
                        for source in field_mapping.sources:
                            if source not in defined_fields:
                                warnings.append(
                                    f"Field '{field_name}': source field "
                                    f"'{source}' not defined"
                                )

                if field_mapping.transform:
                    valid_transforms = {
                        "upper",
                        "lower",
                        "title",
                        "strip",
                        "int",
                        "float",
                        "str",
                        "bool",
                    }
                    if field_mapping.transform not in valid_transforms:
                        errors.append(
                            f"Field '{field_name}': unknown transform "
                            f"'{field_mapping.transform}'"
                        )

        console.print()

        if errors:
            console.print(f"[bold red]Errors ({len(errors)}):[/bold red]")
            for error in errors:
                console.print(f"  [red]✗[/red] {error}")
            console.print()

        if warnings:
            console.print(f"[bold yellow]Warnings ({len(warnings)}):[/bold yellow]")
            for warning in warnings:
                console.print(f"  [yellow]⚠[/yellow] {warning}")
            console.print()

        if not errors and not warnings:
            console.print(
                "[bold green]✓ All checks passed! "
                "Configuration is valid.[/bold green]\n"
            )
        elif errors:
            console.print(
                f"[bold red]✗ Validation failed with {len(errors)} "
                f"error(s)[/bold red]\n"
            )
            raise typer.Exit(code=1) from None
        else:
            console.print(
                f"[bold yellow]⚠ Validation passed with {len(warnings)} "
                f"warning(s)[/bold yellow]\n"
            )

    except typer.Exit:
        raise
    except FileNotFoundError as e:
        console.print(f"\n[red]Error:[/red] {e}\n")
        raise typer.Exit(code=1) from None
    except Exception as e:
        console.print(f"\n[red]Unexpected error:[/red] {e}\n")
        raise typer.Exit(code=1) from None


@app.command(name="generate-fields")
def generate_fields(
    output: Optional[str] = typer.Option(
        None, "--output", "-o", help="Output file path (defaults to stdout)"
    ),
    prefix: str = typer.Option("", "--prefix", "-p", help="Prefix for field names"),
) -> None:
    try:
        has_stdin_data = not sys.stdin.isatty()

        if not has_stdin_data:
            console.print(
                "[red]Error:[/red] No stdin data provided. "
                "Pipe JSON data to generate fields."
            )
            console.print(
                "\n[yellow]Example:[/yellow] "
                'echo \'{"name": "John", "age": 30}\' | viewtext generate-fields'
            )
            raise typer.Exit(code=1) from None

        json_data = sys.stdin.read()
        if not json_data.strip():
            console.print("[red]Error:[/red] Empty stdin data")
            raise typer.Exit(code=1) from None

        try:
            data = json.loads(json_data)
        except json.JSONDecodeError as e:
            console.print(f"[red]Error:[/red] Invalid JSON: {e}")
            raise typer.Exit(code=1) from None

        if not isinstance(data, dict):
            console.print(
                "[red]Error:[/red] JSON data must be an object/dictionary at root level"
            )
            raise typer.Exit(code=1) from None

        toml_lines = _generate_field_definitions(data, prefix)

        if output:
            output_path = Path(output)
            try:
                with open(output_path, "w") as f:
                    f.write(toml_lines)
                console.print(
                    f"\n[green]✓ Field definitions written to:[/green] {output_path}\n"
                )
            except OSError as e:
                console.print(f"[red]Error writing to file:[/red] {e}")
                raise typer.Exit(code=1) from None
        else:
            print(toml_lines)

    except typer.Exit:
        raise
    except Exception as e:
        console.print(f"\n[red]Unexpected error:[/red] {e}\n")
        raise typer.Exit(code=1) from None


def _generate_field_definitions(
    data: dict[str, Any], prefix: str = "", path: str = ""
) -> str:
    lines = []

    for key, value in data.items():
        field_name = f"{prefix}{key}" if prefix else key
        context_key = f"{path}.{key}" if path else key

        if isinstance(value, dict):
            nested_fields = _generate_field_definitions(
                value, prefix=f"{field_name}_", path=context_key
            )
            lines.append(nested_fields)
        else:
            lines.append(f"[fields.{field_name}]")
            lines.append(f'context_key = "{context_key}"')

            if isinstance(value, bool):
                lines.append('type = "bool"')
            elif isinstance(value, int):
                lines.append('type = "int"')
            elif isinstance(value, float):
                lines.append('type = "float"')
            elif isinstance(value, str):
                lines.append('type = "str"')
            elif isinstance(value, list):
                lines.append('type = "list"')
            elif value is None:
                lines.append('type = "any"')

            lines.append("")

    return "\n".join(lines)


@app.command()
def info(ctx: typer.Context) -> None:
    config = config_path
    formatters_path = ctx.obj.get("formatters")
    fields_path = ctx.obj.get("fields")
    try:
        config_file = Path(config)

        console.print("\n[bold]ViewText Configuration Info[/bold]\n")

        console.print(f"[bold]Config File:[/bold] {config_file.absolute()}")
        console.print(f"[bold]Exists:[/bold] {config_file.exists()}")
        if formatters_path:
            console.print(f"[bold]Formatters File:[/bold] {formatters_path}")
        if fields_path:
            console.print(f"[bold]Fields File:[/bold] {fields_path}")

        if config_file.exists():
            console.print(f"[bold]Size:[/bold] {config_file.stat().st_size} bytes")

            loader = LayoutLoader(str(config_file), formatters_path, fields_path)
            layouts_config = loader.load()

            console.print(
                f"\n[bold]Layouts:[/bold] {len(layouts_config.layouts)} found"
            )

            if layouts_config.formatters:
                formatter_count = len(layouts_config.formatters)
                console.print(
                    f"[bold]Global Formatters:[/bold] {formatter_count} defined"
                )

                formatter_table = Table(
                    show_header=True, header_style="bold", title="Global Formatters"
                )
                formatter_table.add_column("Name", style="cyan")
                formatter_table.add_column("Type", style="green")
                formatter_table.add_column("Parameters", style="yellow")

                for fmt_name, fmt_config in layouts_config.formatters.items():
                    params = fmt_config.model_dump(exclude_none=True)
                    fmt_type = params.pop("type", "")
                    params_str = ", ".join(f"{k}={v}" for k, v in params.items())
                    formatter_table.add_row(fmt_name, fmt_type, params_str)

                console.print()
                console.print(formatter_table)
            else:
                console.print("[bold]Global Formatters:[/bold] None defined in config")

        console.print()

    except FileNotFoundError as e:
        console.print(f"\n[red]Error:[/red] {e}\n")
        raise typer.Exit(code=1) from None
    except Exception as e:
        console.print(f"\n[red]Error:[/red] {e}\n")
        raise typer.Exit(code=1) from None


def main() -> None:
    app()


if __name__ == "__main__":
    main()
