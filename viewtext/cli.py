#!/usr/bin/env python3

import importlib
import json
import os
import re
import sys
from pathlib import Path
from typing import Any, Optional, Union

import typer
from rich.console import Console
from rich.table import Table

from .engine import LayoutEngine
from .formatters import get_formatter_registry
from .loader import DictItemConfig, LayoutLoader, LineConfig
from .registry_builder import get_registry_from_config

app = typer.Typer(help="ViewText CLI - Text grid layout generator")
console = Console()

config_path: str = "layouts.toml"


def resolve_cli_file(value: Optional[str], option_name: str) -> Optional[str]:
    if value is None:
        return None

    raw_path = Path(value).expanduser()

    if raw_path.exists():
        return str(raw_path.resolve())

    if raw_path.is_absolute():
        raise FileNotFoundError(f"Could not find {option_name} file '{value}'.")

    if not raw_path.suffix:
        local_with_suffix = raw_path.with_suffix(".toml")
        if local_with_suffix.exists():
            return str(local_with_suffix.resolve())

    xdg_config_home = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config"))
    xdg_base = xdg_config_home / "viewtext"

    xdg_candidate = xdg_base / raw_path
    if xdg_candidate.exists():
        return str(xdg_candidate.resolve())

    if not raw_path.suffix:
        xdg_candidate_with_suffix = xdg_candidate.with_suffix(".toml")
        if xdg_candidate_with_suffix.exists():
            return str(xdg_candidate_with_suffix.resolve())

    raise FileNotFoundError(
        f"Could not find {option_name} file '{value}'. Checked current "
        f"directory and {xdg_base}."
    )


def resolve_config_files(ctx: typer.Context) -> list[str]:
    if ctx.obj is None:
        ctx.obj = {}

    raw_configs = ctx.obj.get("configs", [])
    if not raw_configs:
        raw_configs = [config_path]

    resolved_paths: list[str] = []
    for raw_config in raw_configs:
        resolved = resolve_cli_file(raw_config, "config")
        if resolved is None:
            resolved = raw_config
        resolved_paths.append(resolved)

    return resolved_paths


def get_loader_and_configs(ctx: typer.Context) -> tuple[list[str], LayoutLoader]:
    config_files = resolve_config_files(ctx)
    global config_path
    config_path = config_files[0]
    loader = LayoutLoader(config_files)
    return config_files, loader


def _resolve_context_data(loader: LayoutLoader) -> dict[str, Any]:
    has_stdin_data = not sys.stdin.isatty()
    context_data: Any

    if has_stdin_data:
        try:
            json_data = sys.stdin.read()
            if json_data.strip():
                context_data = json.loads(json_data)
            else:
                raise ValueError("Empty stdin")
        except (json.JSONDecodeError, ValueError):
            context_provider_path = loader.get_context_provider()
            if context_provider_path:
                try:
                    module_name, func_name = context_provider_path.rsplit(".", 1)
                    module = importlib.import_module(module_name)
                    context_func = getattr(module, func_name)
                    context_data = context_func()
                except (ValueError, ImportError, AttributeError) as e:
                    msg = f"Error loading context provider '{context_provider_path}'"
                    console.print(f"[red]{msg}:[/red] {e}")
                    raise typer.Exit(code=1) from None
                except Exception as e:  # noqa: BLE001
                    msg = f"Error calling context provider '{context_provider_path}'"
                    console.print(f"[red]{msg}:[/red] {e}")
                    raise typer.Exit(code=1) from None
            else:
                context_data = create_mock_context()
    else:
        context_provider_path = loader.get_context_provider()
        if context_provider_path:
            try:
                module_name, func_name = context_provider_path.rsplit(".", 1)
                module = importlib.import_module(module_name)
                context_func = getattr(module, func_name)
                context_data = context_func()
            except (ValueError, ImportError, AttributeError) as e:
                msg = f"Error loading context provider '{context_provider_path}'"
                console.print(f"[red]{msg}:[/red] {e}")
                raise typer.Exit(code=1) from None
            except Exception as e:  # noqa: BLE001
                msg = f"Error calling context provider '{context_provider_path}'"
                console.print(f"[red]{msg}:[/red] {e}")
                raise typer.Exit(code=1) from None
        else:
            context_data = create_mock_context()

    if not isinstance(context_data, dict):
        console.print("[red]Error:[/red] Context data must be a JSON object/dictionary")
        raise typer.Exit(code=1) from None

    return context_data


@app.callback()
def main_callback(
    ctx: typer.Context,
    configs: list[str] = typer.Option(
        [], "--config", "-c", help="Path to TOML config file (can be repeated)"
    ),
) -> None:
    global config_path
    selected_configs = configs or ["layouts.toml"]
    # Keep the first one as the reference for downstream defaults
    config_path = selected_configs[0]
    ctx.obj = {"configs": selected_configs}


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
    try:
        config_files, loader = get_loader_and_configs(ctx)
        layouts_config = loader.load()

        console.print("\n[bold green]Configuration Files:[/bold green]")
        for cfg in config_files:
            console.print(f"  • {cfg}")
        console.print()

        if not layouts_config.layouts:
            console.print("[yellow]No layouts found in configuration file[/yellow]")
            return

        table = Table(title="Available Layouts", show_header=True, header_style="bold")
        table.add_column("Layout Name", style="cyan", width=30)
        table.add_column("Display Name", style="green", width=40)
        table.add_column("Type", justify="right", style="magenta")
        table.add_column("Count", justify="right", style="magenta")

        for layout_name, layout_config in sorted(layouts_config.layouts.items()):
            display_name = layout_config.name
            if layout_config.items:
                layout_type = "dict"
                count = len(layout_config.items)
            elif layout_config.lines:
                layout_type = "line"
                count = len(layout_config.lines)
            else:
                layout_type = "empty"
                count = 0
            table.add_row(layout_name, display_name, layout_type, str(count))

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
    try:
        config_files, loader = get_loader_and_configs(ctx)
        layout = loader.get_layout(layout_name)

        console.print(
            f"\n[bold green]Layout:[/bold green] {layout_name} - {layout['name']}\n"
        )

        has_items = "items" in layout and layout.get("items")
        has_lines = "lines" in layout and layout.get("lines")

        if has_items:
            table = Table(show_header=True, header_style="bold")
            table.add_column("Key", justify="left", style="cyan", width=20)
            table.add_column("Input", style="green", width=25)
            table.add_column("Presenter", style="blue", width=20)
            table.add_column("Formatter", style="yellow", width=20)
            table.add_column("Parameters", style="magenta")

            for item in layout.get("items", []):
                key = item.get("key", "")
                input_name = item.get("input", "")
                presenter = item.get("presenter", "")
                formatter = item.get("formatter", "")
                params = item.get("formatter_params", {})
                params_str = str(params) if params else ""

                table.add_row(key, input_name, presenter, formatter, params_str)

            console.print(table)
            console.print(
                f"\n[bold]Total items:[/bold] {len(layout.get('items', []))}\n"
            )
        elif has_lines:
            table = Table(show_header=True, header_style="bold")
            table.add_column("Index", justify="right", style="cyan", width=8)
            table.add_column("Input", style="green", width=25)
            table.add_column("Presenter", style="blue", width=20)
            table.add_column("Formatter", style="yellow", width=20)
            table.add_column("Parameters", style="magenta")

            for line in layout.get("lines", []):
                index = str(line.get("index", ""))
                input_name = line.get("input", "")
                presenter = line.get("presenter", "")
                formatter = line.get("formatter", "")
                params = line.get("formatter_params", {})
                params_str = str(params) if params else ""

                table.add_row(index, input_name, presenter, formatter, params_str)

            console.print(table)
            console.print(
                f"\n[bold]Total lines:[/bold] {len(layout.get('lines', []))}\n"
            )
        else:
            console.print("[yellow]Empty layout (no lines or items)[/yellow]\n")

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
    try:
        config_files, loader = get_loader_and_configs(ctx)
        layout = loader.get_layout(layout_name)

        if field_registry:
            console.print(
                "[yellow]Custom registry support not yet implemented[/yellow]"
            )
            registry = None
        else:
            registry = get_registry_from_config(loader=loader)

        engine = LayoutEngine(field_registry=registry, layout_loader=loader)

        context = _resolve_context_data(loader)

        has_items = "items" in layout and layout.get("items")
        has_lines = "lines" in layout and layout.get("lines")

        if has_items and not has_lines:
            result = engine.build_dict_str(layout, context)

            if json_output:
                print(json.dumps(result, indent=2))
            else:
                console.print(
                    f"\n[bold green]Rendered Output:[/bold green] {layout_name}\n"
                )
                console.print("[dim]" + "─" * 80 + "[/dim]")

                for key, value in result.items():
                    console.print(f"[cyan]{key}:[/cyan] {value}")

                console.print("[dim]" + "─" * 80 + "[/dim]\n")
        elif has_lines:
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


@app.command(name="render-inputs")
def render_inputs(
    ctx: typer.Context,
    layout: Optional[str] = typer.Option(
        None,
        "--layout",
        "-l",
        help="Limit to inputs referenced by the specified layout",
    ),
    json_output: bool = typer.Option(
        False, "--json", "-j", help="Output rendered inputs as JSON"
    ),
) -> None:
    try:
        config_files, loader = get_loader_and_configs(ctx)
        layouts_config = loader.load()
        input_mappings = loader.get_input_mappings()

        console.print("\n[bold green]Configuration Files:[/bold green]")
        for cfg in config_files:
            console.print(f"  • {cfg}")
        console.print()

        if not input_mappings:
            console.print("[yellow]No inputs defined in configuration[/yellow]")
            return

        inputs_to_show: list[str]
        if layout:
            if layout not in layouts_config.layouts:
                console.print(f"[red]Error:[/red] Layout '{layout}' not found")
                available = ", ".join(sorted(layouts_config.layouts.keys()))
                console.print(f"\n[yellow]Available layouts:[/yellow] {available}")
                raise typer.Exit(code=1) from None

            layout_cfg = layouts_config.layouts[layout]
            referenced_inputs: set[str] = set()

            if layout_cfg.lines:
                for line in layout_cfg.lines:
                    if line.input:
                        referenced_inputs.add(line.input)
                    if line.presenter and layouts_config.presenters:
                        presenter_cfg = layouts_config.presenters.get(line.presenter)
                        if presenter_cfg and presenter_cfg.input:
                            referenced_inputs.add(presenter_cfg.input)

            if layout_cfg.items:
                for item in layout_cfg.items:
                    if item.input:
                        referenced_inputs.add(item.input)
                    if item.presenter and layouts_config.presenters:
                        presenter_cfg = layouts_config.presenters.get(item.presenter)
                        if presenter_cfg and presenter_cfg.input:
                            referenced_inputs.add(presenter_cfg.input)

            inputs_to_show = [
                name
                for name in sorted(input_mappings.keys())
                if name in referenced_inputs
            ]

            if not inputs_to_show:
                console.print(
                    f"[yellow]Layout '{layout}' does not reference any inputs[/yellow]"
                )
                return
        else:
            inputs_to_show = sorted(input_mappings.keys())

        registry = get_registry_from_config(loader=loader)
        context = _resolve_context_data(loader)
        evaluation_context = dict(context)

        results: dict[str, Any] = {}

        for input_name in inputs_to_show:
            mapping = input_mappings[input_name]
            if registry and registry.has_field(input_name):
                getter = registry.get(input_name)
                value = getter(evaluation_context)
            elif input_name in evaluation_context:
                value = evaluation_context[input_name]
            else:
                value = mapping.default

            evaluation_context[input_name] = value
            results[input_name] = value

        if json_output:
            print(json.dumps(results, indent=2, default=str))
            return

        table = Table(title="Rendered Inputs", show_header=True, header_style="bold")
        table.add_column("Input", style="cyan", overflow="fold")
        table.add_column("Value", style="green", overflow="fold")
        table.add_column("Context Key", style="blue", overflow="fold")
        table.add_column("Operation", style="magenta", overflow="fold")
        table.add_column("Sources", style="magenta", overflow="fold")
        table.add_column("Default", style="yellow", overflow="fold")

        for input_name in inputs_to_show:
            mapping = input_mappings[input_name]
            value = results[input_name]
            sources = ", ".join(mapping.sources) if mapping.sources else ""
            operation = mapping.operation or ""
            context_key = mapping.context_key or ""
            default = mapping.default if mapping.default is not None else ""

            table.add_row(
                input_name,
                repr(value),
                context_key,
                operation,
                sources,
                repr(default),
            )

        console.print(table)
        console.print(f"\n[bold]Total inputs rendered:[/bold] {len(inputs_to_show)}\n")

    except typer.Exit:
        raise
    except FileNotFoundError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(code=1) from None
    except Exception as e:  # noqa: BLE001
        console.print(f"[red]Error rendering inputs:[/red] {e}")
        raise typer.Exit(code=1) from None


@app.command(name="render-presenters")
def render_presenters(
    ctx: typer.Context,
    layout: Optional[str] = typer.Option(
        None,
        "--layout",
        "-l",
        help="Limit to presenters referenced by the specified layout",
    ),
    json_output: bool = typer.Option(
        False, "--json", "-j", help="Output rendered presenters as JSON"
    ),
) -> None:
    try:
        config_files, loader = get_loader_and_configs(ctx)
        layouts_config = loader.load()
        presenters = layouts_config.presenters or {}

        console.print("\n[bold green]Configuration Files:[/bold green]")
        for cfg in config_files:
            console.print(f"  • {cfg}")
        console.print()

        if not presenters:
            console.print("[yellow]No presenters defined in configuration[/yellow]")
            return

        presenter_names: list[str]
        if layout:
            if layout not in layouts_config.layouts:
                console.print(f"[red]Error:[/red] Layout '{layout}' not found")
                available = ", ".join(sorted(layouts_config.layouts.keys()))
                console.print(f"\n[yellow]Available layouts:[/yellow] {available}")
                raise typer.Exit(code=1) from None

            layout_cfg = layouts_config.layouts[layout]
            referenced_presenters: set[str] = set()

            if layout_cfg.lines:
                for line in layout_cfg.lines:
                    if line.presenter:
                        referenced_presenters.add(line.presenter)

            if layout_cfg.items:
                for item in layout_cfg.items:
                    if item.presenter:
                        referenced_presenters.add(item.presenter)

            presenter_names = [
                name
                for name in sorted(presenters.keys())
                if name in referenced_presenters
            ]

            if not presenter_names:
                console.print(
                    f"[yellow]Layout '{layout}' does not reference any presenters"
                    "[/yellow]"
                )
                return
        else:
            presenter_names = sorted(presenters.keys())

        registry = get_registry_from_config(loader=loader)
        input_mappings = loader.get_input_mappings()
        context = _resolve_context_data(loader)
        evaluation_context = dict(context)
        engine = LayoutEngine(field_registry=registry, layout_loader=loader)

        results: dict[str, dict[str, Any]] = {}

        for presenter_name in presenter_names:
            presenter_cfg = presenters[presenter_name]
            input_name = presenter_cfg.input
            raw_value: Any = None

            if input_name:
                if registry and registry.has_field(input_name):
                    raw_value = registry.get(input_name)(evaluation_context)
                elif input_name in evaluation_context:
                    raw_value = evaluation_context[input_name]
                else:
                    mapping = input_mappings.get(input_name)
                    raw_value = mapping.default if mapping else None

                evaluation_context[input_name] = raw_value

            formatter_params = dict(presenter_cfg.formatter_params or {})
            formatted_value = raw_value
            if presenter_cfg.formatter:
                formatted_value = engine._format_value(
                    raw_value,
                    presenter_cfg.formatter,
                    formatter_params,
                    evaluation_context,
                )

            results[presenter_name] = {
                "input": input_name,
                "raw": raw_value,
                "rendered": formatted_value,
                "formatter": presenter_cfg.formatter,
                "params": formatter_params,
            }

        if json_output:
            print(json.dumps(results, indent=2, default=str))
            return

        table = Table(
            title="Rendered Presenters", show_header=True, header_style="bold"
        )
        table.add_column("Presenter", style="cyan", overflow="fold")
        table.add_column("Input", style="green", overflow="fold")
        table.add_column("Formatter", style="yellow", overflow="fold")
        table.add_column("Parameters", style="magenta", overflow="fold")
        table.add_column("Raw Value", style="blue", overflow="fold")
        table.add_column("Rendered", style="green", overflow="fold")

        for presenter_name in presenter_names:
            data = results[presenter_name]
            params_str = (
                json.dumps(data["params"], default=str) if data["params"] else ""
            )
            table.add_row(
                presenter_name,
                data["input"] or "",
                data["formatter"] or "",
                params_str,
                repr(data["raw"]),
                repr(data["rendered"]),
            )

        console.print(table)
        console.print(
            f"\n[bold]Total presenters rendered:[/bold] {len(presenter_names)}\n"
        )

    except typer.Exit:
        raise
    except FileNotFoundError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(code=1) from None
    except Exception as e:  # noqa: BLE001
        console.print(f"[red]Error rendering presenters:[/red] {e}")
        raise typer.Exit(code=1) from None


@app.command(name="inputs")
def list_inputs(ctx: typer.Context) -> None:
    try:
        config_files, loader = get_loader_and_configs(ctx)
        input_mappings = loader.get_input_mappings()

        console.print("\n[bold green]Configuration Files:[/bold green]")
        for cfg in config_files:
            console.print(f"  • {cfg}")
        console.print()

        if not input_mappings:
            console.print(
                "[yellow]No input mappings found in configuration file[/yellow]"
            )
            return

        table = Table(title="Input Mappings", show_header=True, header_style="bold")
        table.add_column("Input Name", style="cyan", overflow="fold")
        table.add_column("Context Key", style="green", overflow="fold")
        table.add_column("Operation", style="blue", overflow="fold")
        table.add_column("Parameters", style="magenta", overflow="fold")
        table.add_column("Default", style="yellow", overflow="fold")
        table.add_column("Transform", style="magenta", overflow="fold")

        for input_name, mapping in sorted(input_mappings.items()):
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
                input_name, context_key, operation, params_str, default, transform
            )

        console.print(table)
        console.print(f"\n[bold]Total inputs:[/bold] {len(input_mappings)}\n")

    except FileNotFoundError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(code=1) from None
    except Exception as e:
        console.print(f"[red]Error loading input mappings:[/red] {e}")
        raise typer.Exit(code=1) from None


@app.command(name="presenters")
def list_presenters(ctx: typer.Context) -> None:
    try:
        config_files, loader = get_loader_and_configs(ctx)
        layouts_config = loader.load()

        console.print("\n[bold green]Configuration Files:[/bold green]")
        for cfg in config_files:
            console.print(f"  • {cfg}")
        console.print()

        if not layouts_config.presenters:
            console.print(
                "[yellow]No presenter definitions found in configuration file[/yellow]"
            )
            return

        table = Table(
            title="Presenter Definitions", show_header=True, header_style="bold"
        )
        table.add_column("Presenter", style="cyan", overflow="fold")
        table.add_column("Input", style="green", overflow="fold")
        table.add_column("Formatter", style="yellow", overflow="fold")
        table.add_column("Parameters", style="magenta", overflow="fold")

        for presenter_name, presenter_config in sorted(
            layouts_config.presenters.items()
        ):
            input_name = presenter_config.input if presenter_config.input else ""
            formatter = presenter_config.formatter if presenter_config.formatter else ""
            params = (
                presenter_config.formatter_params
                if presenter_config.formatter_params
                else {}
            )
            params_str = str(params) if params else ""

            table.add_row(presenter_name, input_name, formatter, params_str)

        console.print(table)
        console.print(
            f"\n[bold]Total presenters:[/bold] {len(layouts_config.presenters)}\n"
        )

    except FileNotFoundError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(code=1) from None
    except Exception as e:
        console.print(f"[red]Error loading presenter definitions:[/red] {e}")
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
    try:
        config_files, loader = get_loader_and_configs(ctx)
        layouts_config = loader.load()

        console.print("\n[bold green]Configuration Files:[/bold green]")
        for cfg in config_files:
            console.print(f"  • {cfg}")
        console.print()

        template_lines = []
        for layout_name, layout_config in layouts_config.layouts.items():
            if layout_config.lines:
                for line in layout_config.lines:
                    if line.formatter == "template":
                        template_lines.append(
                            {
                                "layout": layout_name,
                                "layout_name": layout_config.name,
                                "input": line.input,
                                "index": line.index,
                                "template": line.formatter_params.get("template", ""),
                                "fields": line.formatter_params.get("fields", []),
                            }
                        )
            if layout_config.items:
                for item in layout_config.items:
                    if item.formatter == "template":
                        template_lines.append(
                            {
                                "layout": layout_name,
                                "layout_name": layout_config.name,
                                "input": item.input,
                                "index": item.key,
                                "template": item.formatter_params.get("template", ""),
                                "fields": item.formatter_params.get("fields", []),
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
        table.add_column("Input", style="green", overflow="fold")
        table.add_column("Template", style="yellow", overflow="fold", width=40)
        table.add_column("Fields Used", style="magenta", overflow="fold")

        for template_item in template_lines:
            fields_str = ", ".join(template_item["fields"])
            table.add_row(
                f"{template_item['layout']}\n({template_item['layout_name']})",
                template_item["input"],
                template_item["template"],
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
def test_input(
    ctx: typer.Context,
    input_name: str = typer.Argument(..., help="Name of the input to test"),
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
    try:
        config_files, loader = get_loader_and_configs(ctx)
        input_mappings = loader.get_input_mappings()

        if input_name not in input_mappings:
            console.print(f"[red]Error:[/red] Input '{input_name}' not found")
            available = ", ".join(sorted(input_mappings.keys()))
            console.print(f"\n[yellow]Available inputs:[/yellow] {available}")
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

        console.print(f"\n[bold green]Testing Input:[/bold green] {input_name}\n")

        mapping = input_mappings[input_name]
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

        if registry and registry.has_field(input_name):
            getter = registry.get(input_name)
            result = getter(context)
        elif input_name in context:
            result = context[input_name]
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
                matching_line: Optional[Union[LineConfig, DictItemConfig]] = None
                if layout_config.lines:
                    for line in layout_config.lines:
                        if line.input == input_name and line.formatter == formatter:
                            matching_line = line
                            break
                if layout_config.items and not matching_line:
                    for item in layout_config.items:
                        if item.input == input_name and item.formatter == formatter:
                            matching_line = item
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
                        f"[yellow]Warning:[/yellow] Input '{input_name}' with "
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
                    f"       Example: viewtext test {input_name} "
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
    errors = []
    warnings = []
    registry = None

    try:
        config_files, loader = get_loader_and_configs(ctx)

        console.print("\n[bold]ViewText Configuration Validation[/bold]\n")
        console.print("[bold]Config Files:[/bold]")
        for cfg in config_files:
            console.print(f"  • {cfg}")
        console.print()

        missing_files = [cfg for cfg in config_files if not Path(cfg).exists()]
        if missing_files:
            missing_path = Path(missing_files[0]).absolute()
            console.print(f"[red]✗ Config file not found:[/red] {missing_path}\n")
            raise typer.Exit(code=1) from None

        try:
            layouts_config = loader.load()
            console.print("[green]✓ TOML syntax is valid[/green]")
        except Exception as e:
            console.print(f"[red]✗ TOML syntax error:[/red] {e}\n")
            raise typer.Exit(code=1) from None

        try:
            registry = get_registry_from_config(loader=loader)
            console.print("[green]✓ Input registry built successfully[/green]")
        except Exception as e:
            errors.append(f"Failed to build input registry: {e}")
            console.print(f"[red]✗ Input registry error:[/red] {e}")

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

        defined_inputs = (
            set(layouts_config.inputs.keys()) if layouts_config.inputs else set()
        )
        defined_formatters = (
            set(layouts_config.formatters.keys())
            if layouts_config.formatters
            else set()
        )
        defined_presenters = (
            set(layouts_config.presenters.keys())
            if layouts_config.presenters
            else set()
        )
        all_formatters = builtin_formatters | defined_formatters

        for layout_name, layout_config in layouts_config.layouts.items():
            items_to_check: list[tuple[str, Union[LineConfig, DictItemConfig]]] = []
            if layout_config.lines:
                items_to_check.extend(
                    [(f"line {i}", line) for i, line in enumerate(layout_config.lines)]
                )
            if layout_config.items:
                items_to_check.extend(
                    [(f"item '{item.key}'", item) for item in layout_config.items]
                )

            for item_label, item in items_to_check:
                input_name = item.input

                if registry and input_name and not registry.has_field(input_name):
                    if input_name not in defined_inputs:
                        warnings.append(
                            f"Layout '{layout_name}', {item_label}: "
                            f"input '{input_name}' not defined in input registry"
                        )

                presenter_name = (
                    item.presenter if isinstance(item, LineConfig) else item.presenter
                )
                if presenter_name:
                    if presenter_name not in defined_presenters:
                        errors.append(
                            f"Layout '{layout_name}', {item_label}: "
                            f"unknown presenter '{presenter_name}'"
                        )
                else:
                    formatter_name = item.formatter
                    if formatter_name:
                        if formatter_name not in all_formatters:
                            errors.append(
                                f"Layout '{layout_name}', {item_label}: "
                                f"unknown formatter '{formatter_name}'"
                            )
                        else:
                            try:
                                formatter_registry.get(formatter_name)
                            except ValueError:
                                if (
                                    formatter_name in defined_formatters
                                    and layouts_config.formatters
                                ):
                                    formatter_config = layouts_config.formatters[
                                        formatter_name
                                    ]
                                    formatter_type = formatter_config.type
                                    try:
                                        formatter_registry.get(formatter_type)
                                    except ValueError:
                                        errors.append(
                                            f"Layout '{layout_name}', {item_label}: "
                                            f"formatter '{formatter_name}' has unknown "
                                            f"type '{formatter_type}'"
                                        )

                    if formatter_name == "template" or (
                        formatter_name in defined_formatters
                        and layouts_config.formatters
                        and layouts_config.formatters[formatter_name].type == "template"
                    ):
                        if not item.formatter_params.get("template"):
                            errors.append(
                                f"Layout '{layout_name}', {item_label}: "
                                "template formatter missing 'template' parameter"
                            )
                        if not item.formatter_params.get("fields"):
                            errors.append(
                                f"Layout '{layout_name}', {item_label}: "
                                "template formatter missing 'fields' parameter"
                            )
                        else:
                            template_fields = item.formatter_params.get("fields", [])
                            for tf in template_fields:
                                base_input = tf.split(".")[0]
                                if (
                                    base_input != input_name
                                    and base_input not in defined_inputs
                                ):
                                    warnings.append(
                                        f"Layout '{layout_name}', {item_label}: "
                                        f"template references undefined input "
                                        f"'{base_input}'"
                                    )

        if layouts_config.inputs:
            for input_name, input_mapping in layouts_config.inputs.items():
                if input_mapping.type:
                    valid_types = {"str", "int", "float", "bool", "list", "dict", "any"}
                    if input_mapping.type not in valid_types:
                        errors.append(
                            f"Input '{input_name}': unknown type '{input_mapping.type}'"
                        )

                if input_mapping.on_validation_error:
                    valid_strategies = {"raise", "skip", "use_default", "coerce"}
                    if input_mapping.on_validation_error not in valid_strategies:
                        errors.append(
                            f"Input '{input_name}': unknown on_validation_error "
                            f"strategy '{input_mapping.on_validation_error}'"
                        )

                if (
                    input_mapping.min_value is not None
                    or input_mapping.max_value is not None
                ):
                    if input_mapping.type and input_mapping.type not in {
                        "int",
                        "float",
                        "any",
                    }:
                        warnings.append(
                            f"Input '{input_name}': min_value/max_value constraints "
                            f"are typically used with numeric types (int/float), "
                            f"but input has type '{input_mapping.type}'"
                        )

                if (
                    input_mapping.min_length is not None
                    or input_mapping.max_length is not None
                ):
                    if input_mapping.type and input_mapping.type not in {"str", "any"}:
                        warnings.append(
                            f"Input '{input_name}': min_length/max_length constraints "
                            f"are typically used with string types, "
                            f"but input has type '{input_mapping.type}'"
                        )

                if (
                    input_mapping.min_items is not None
                    or input_mapping.max_items is not None
                ):
                    if input_mapping.type and input_mapping.type not in {"list", "any"}:
                        warnings.append(
                            f"Input '{input_name}': min_items/max_items constraints "
                            f"are typically used with list types, "
                            f"but input has type '{input_mapping.type}'"
                        )

                if input_mapping.pattern is not None:
                    if input_mapping.type and input_mapping.type not in {"str", "any"}:
                        warnings.append(
                            f"Input '{input_name}': pattern constraint "
                            f"is typically used with string types, "
                            f"but input has type '{input_mapping.type}'"
                        )
                    else:
                        try:
                            re.compile(input_mapping.pattern)
                        except re.error as e:
                            errors.append(
                                f"Input '{input_name}': invalid regex pattern "
                                f"'{input_mapping.pattern}': {e}"
                            )

                if (
                    input_mapping.on_validation_error == "use_default"
                    and input_mapping.default is None
                ):
                    warnings.append(
                        f"Input '{input_name}': on_validation_error='use_default' "
                        f"but no default value is specified"
                    )

                if input_mapping.operation:
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
                    if input_mapping.operation not in valid_operations:
                        errors.append(
                            f"Input '{input_name}': unknown operation "
                            f"'{input_mapping.operation}'"
                        )

                    if input_mapping.sources:
                        for source in input_mapping.sources:
                            if source not in defined_inputs:
                                warnings.append(
                                    f"Input '{input_name}': source input "
                                    f"'{source}' not defined"
                                )

                if input_mapping.transform:
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
                    if input_mapping.transform not in valid_transforms:
                        errors.append(
                            f"Input '{input_name}': unknown transform "
                            f"'{input_mapping.transform}'"
                        )

        if layouts_config.presenters:
            for presenter_name, presenter_config in layouts_config.presenters.items():
                if not presenter_config.input:
                    errors.append(
                        f"Presenter '{presenter_name}': missing input specification"
                    )

                if (
                    presenter_config.formatter
                    and presenter_config.formatter not in all_formatters
                ):
                    errors.append(
                        f"Presenter '{presenter_name}': unknown formatter "
                        f"'{presenter_config.formatter}'"
                    )
                elif (
                    presenter_config.formatter in defined_formatters
                    and layouts_config.formatters
                ):
                    formatter_config = layouts_config.formatters[
                        presenter_config.formatter
                    ]
                    formatter_type = formatter_config.type
                    try:
                        formatter_registry.get(formatter_type)
                    except ValueError:
                        errors.append(
                            f"Presenter '{presenter_name}': formatter "
                            f"'{presenter_config.formatter}' has unknown "
                            f"type '{formatter_type}'"
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


@app.command(name="generate-inputs")
def generate_inputs(
    output: Optional[str] = typer.Option(
        None, "--output", "-o", help="Output file path (defaults to stdout)"
    ),
    prefix: str = typer.Option("", "--prefix", "-p", help="Prefix for input names"),
) -> None:
    try:
        has_stdin_data = not sys.stdin.isatty()

        if not has_stdin_data:
            console.print(
                "[red]Error:[/red] No stdin data provided. "
                "Pipe JSON data to generate inputs."
            )
            console.print(
                "\n[yellow]Example:[/yellow] "
                'echo \'{"name": "John", "age": 30}\' | viewtext generate-inputs'
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

        toml_lines = _generate_input_definitions(data, prefix)

        if output:
            output_path = Path(output)
            try:
                with open(output_path, "w") as f:
                    f.write(toml_lines)
                console.print(
                    f"\n[green]✓ Input definitions written to:[/green] {output_path}\n"
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


def _generate_input_definitions(
    data: dict[str, Any], prefix: str = "", path: str = ""
) -> str:
    lines = []

    for key, value in data.items():
        input_name = f"{prefix}{key}" if prefix else key
        context_key = f"{path}.{key}" if path else key

        if isinstance(value, dict):
            nested_inputs = _generate_input_definitions(
                value, prefix=f"{input_name}_", path=context_key
            )
            lines.append(nested_inputs)
        else:
            lines.append(f"[inputs.{input_name}]")
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
    try:
        config_files, loader = get_loader_and_configs(ctx)

        console.print("\n[bold]ViewText Configuration Info[/bold]\n")

        for cfg in config_files:
            cfg_path = Path(cfg)
            exists = cfg_path.exists()
            size_info = f" ({cfg_path.stat().st_size} bytes)" if exists else ""
            console.print(
                f"[bold]-[/bold] {cfg_path.absolute()} - "
                f"{'exists' if exists else 'missing'}{size_info}"
            )

        console.print()

        layouts_config = loader.load()

        console.print(f"[bold]Layouts:[/bold] {len(layouts_config.layouts)} found")
        console.print(
            f"[bold]Inputs:[/bold] {len(layouts_config.inputs or {})} defined"
        )
        console.print(
            f"[bold]Presenters:[/bold] {len(layouts_config.presenters or {})} defined"
        )

        if layouts_config.formatters:
            formatter_count = len(layouts_config.formatters)
            console.print(f"[bold]Global Formatters:[/bold] {formatter_count} defined")

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
