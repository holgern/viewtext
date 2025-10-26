from __future__ import annotations

# ruff: noqa: C901
from typing import Any

import typer
from rich.console import Console
from rich.table import Table

from viewtext.cli_app.config import ConfigManager
from viewtext.formatters import get_formatter_registry


def register_metadata_commands(
    app: typer.Typer,
    console: Console,
    config_manager: ConfigManager,
) -> None:
    _register_inputs_command(app, console, config_manager)
    _register_presenters_command(app, console, config_manager)
    _register_formatters_command(app, console)
    _register_templates_command(app, console, config_manager)


def _register_inputs_command(
    app: typer.Typer,
    console: Console,
    config_manager: ConfigManager,
) -> None:
    @app.command(name="inputs")
    def list_inputs(ctx: typer.Context) -> None:
        _list_inputs(ctx, console, config_manager)


def _register_presenters_command(
    app: typer.Typer,
    console: Console,
    config_manager: ConfigManager,
) -> None:
    @app.command(name="presenters")
    def list_presenters(ctx: typer.Context) -> None:
        try:
            config_files, loader = config_manager.get_loader_and_configs(ctx)
            layouts_config = loader.load()

            console.print("\n[bold green]Configuration Files:[/bold green]")
            for cfg in config_files:
                console.print(f"  • {cfg}")
            console.print()

            presenters = layouts_config.presenters
            if not presenters:
                console.print(
                    "[yellow]No presenter definitions found in configuration "
                    "file[/yellow]"
                )
                return

            table = Table(
                title="Presenter Definitions",
                show_header=True,
                header_style="bold",
            )
            table.add_column("Presenter", style="cyan", overflow="fold")
            table.add_column("Input", style="green", overflow="fold")
            table.add_column("Formatter", style="yellow", overflow="fold")
            table.add_column("Parameters", style="magenta", overflow="fold")

            for presenter_name, presenter_config in sorted(presenters.items()):
                input_name = presenter_config.input or ""
                formatter = presenter_config.formatter or ""
                params = presenter_config.formatter_params or {}
                params_str = str(params) if params else ""

                table.add_row(presenter_name, input_name, formatter, params_str)

            total_presenters = len(presenters)
            console.print(table)
            console.print(f"\n[bold]Total presenters:[/bold] {total_presenters}\n")

        except FileNotFoundError as exc:
            console.print(f"[red]Error:[/red] {exc}")
            raise typer.Exit(code=1) from None
        except Exception as exc:  # noqa: BLE001
            console.print(f"[red]Error loading presenter definitions:[/red] {exc}")
            raise typer.Exit(code=1) from None


def _register_formatters_command(app: typer.Typer, console: Console) -> None:
    @app.command(name="formatters")
    def list_formatters() -> None:
        get_formatter_registry()

        console.print("\n[bold]Available Formatters[/bold]\n")

        table = Table(show_header=True, header_style="bold")
        table.add_column("Formatter", style="cyan", width=20)
        table.add_column("Description", style="green")

        descriptions: dict[str, str] = {
            "text": "Simple text formatter with optional prefix/suffix",
            "text_uppercase": "Converts text to uppercase",
            "price": "Formats numeric values as prices with symbol and decimals",
            "number": "Formats numbers with optional prefix/suffix and decimals",
            "datetime": "Formats datetime objects or timestamps",
            "relative_time": "Formats time intervals as relative time (e.g., '5m ago')",
            "template": "Combines multiple fields using a template string",
        }

        for formatter_name in sorted(descriptions):
            table.add_row(formatter_name, descriptions[formatter_name])

        total_formatters = len(descriptions)
        console.print(table)
        console.print(f"\n[bold]Total formatters:[/bold] {total_formatters}\n")


def _register_templates_command(
    app: typer.Typer,
    console: Console,
    config_manager: ConfigManager,
) -> None:
    @app.command(name="templates")
    def list_templates(ctx: typer.Context) -> None:
        try:
            config_files, loader = config_manager.get_loader_and_configs(ctx)
            layouts_config = loader.load()

            console.print("\n[bold green]Configuration Files:[/bold green]")
            for cfg in config_files:
                console.print(f"  • {cfg}")
            console.print()

            template_entries: list[dict[str, Any]] = []
            for layout_name, layout_config in layouts_config.layouts.items():
                if layout_config.lines:
                    for line in layout_config.lines:
                        if line.formatter == "template":
                            template_entries.append(
                                {
                                    "layout": layout_name,
                                    "layout_name": layout_config.name,
                                    "input": line.input,
                                    "index": line.index,
                                    "template": line.formatter_params.get(
                                        "template", ""
                                    ),
                                    "fields": line.formatter_params.get("fields", []),
                                }
                            )
                if layout_config.items:
                    for item in layout_config.items:
                        if item.formatter == "template":
                            template_entries.append(
                                {
                                    "layout": layout_name,
                                    "layout_name": layout_config.name,
                                    "input": item.input,
                                    "index": item.key,
                                    "template": item.formatter_params.get(
                                        "template", ""
                                    ),
                                    "fields": item.formatter_params.get("fields", []),
                                }
                            )

            if not template_entries:
                console.print(
                    "[yellow]No template formatters found in configuration "
                    "file[/yellow]"
                )
                return

            table = Table(
                title="Template Formatters",
                show_header=True,
                header_style="bold",
            )
            table.add_column("Layout", style="cyan", overflow="fold")
            table.add_column("Input", style="green", overflow="fold")
            table.add_column("Template", style="yellow", overflow="fold", width=40)
            table.add_column("Fields Used", style="magenta", overflow="fold")

            for entry in template_entries:
                layout_label = f"{entry['layout']}\n({entry['layout_name']})"
                fields_str = ", ".join(entry["fields"])
                table.add_row(
                    layout_label,
                    entry["input"],
                    entry["template"],
                    fields_str,
                )

            total_templates = len(template_entries)
            console.print(table)
            console.print(
                f"\n[bold]Total template formatters:[/bold] {total_templates}\n"
            )

        except FileNotFoundError as exc:
            console.print(f"[red]Error:[/red] {exc}")
            raise typer.Exit(code=1) from None
        except Exception as exc:  # noqa: BLE001
            console.print(f"[red]Error loading templates:[/red] {exc}")
            raise typer.Exit(code=1) from None


def _list_inputs(
    ctx: typer.Context,
    console: Console,
    config_manager: ConfigManager,
) -> None:  # noqa: C901
    try:
        config_files, loader = config_manager.get_loader_and_configs(ctx)
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

        table = Table(
            title="Input Mappings",
            show_header=True,
            header_style="bold",
        )
        table.add_column("Input Name", style="cyan", overflow="fold")
        table.add_column("Context Key", style="green", overflow="fold")
        table.add_column("Operation", style="blue", overflow="fold")
        table.add_column("Parameters", style="magenta", overflow="fold")
        table.add_column("Default", style="yellow", overflow="fold")
        table.add_column("Transform", style="magenta", overflow="fold")

        for input_name, mapping in sorted(input_mappings.items()):
            context_key = mapping.context_key or ""
            operation = mapping.operation or ""
            default = str(mapping.default) if mapping.default is not None else ""
            transform = mapping.transform or ""

            params_parts: list[str] = []
            if mapping.sources:
                params_parts.append(f"sources={mapping.sources}")
            if mapping.multiply is not None:
                params_parts.append(f"multiply={mapping.multiply}")
            if mapping.add is not None:
                params_parts.append(f"add={mapping.add}")
            if mapping.divide is not None:
                params_parts.append(f"divide={mapping.divide}")
            if mapping.separator is not None:
                params_parts.append(f"separator={mapping.separator!r}")
            if mapping.prefix is not None:
                params_parts.append(f"prefix={mapping.prefix!r}")
            if mapping.suffix is not None:
                params_parts.append(f"suffix={mapping.suffix!r}")
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
                params_parts.append(f"if_true={mapping.if_true!r}")
            if mapping.if_false is not None:
                params_parts.append(f"if_false={mapping.if_false!r}")
            if mapping.decimals_param is not None:
                params_parts.append(f"decimals={mapping.decimals_param}")
            if mapping.thousands_sep is not None:
                params_parts.append(f"thousands_sep={mapping.thousands_sep!r}")
            if mapping.decimal_sep is not None:
                params_parts.append(f"decimal_sep={mapping.decimal_sep!r}")

            params_str = ", ".join(params_parts)

            table.add_row(
                input_name,
                context_key,
                operation,
                params_str,
                default,
                transform,
            )

        total_inputs = len(input_mappings)
        console.print(table)
        console.print(f"\n[bold]Total inputs:[/bold] {total_inputs}\n")

    except FileNotFoundError as exc:
        console.print(f"[red]Error:[/red] {exc}")
        raise typer.Exit(code=1) from None
    except Exception as exc:  # noqa: BLE001
        console.print(f"[red]Error loading input mappings:[/red] {exc}")
        raise typer.Exit(code=1) from None
