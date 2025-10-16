#!/usr/bin/env python3

import importlib
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

        engine = LayoutEngine(field_registry=registry)

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

        for line_config in layout.get("lines", []):
            formatter_name = line_config.get("formatter")
            if formatter_name and loader.get_formatter_params(formatter_name):
                line_config["formatter_params"] = loader.get_formatter_params(
                    formatter_name
                )

        lines = engine.build_line_str(layout, context)

        console.print(f"\n[bold green]Rendered Output:[/bold green] {layout_name}\n")
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
        table.add_column("Default", style="yellow", overflow="fold")
        table.add_column("Transform", style="magenta", overflow="fold")

        for field_name, mapping in sorted(field_mappings.items()):
            context_key = mapping.context_key
            default = str(mapping.default) if mapping.default is not None else ""
            transform = mapping.transform if mapping.transform else ""
            table.add_row(field_name, context_key, default, transform)

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
