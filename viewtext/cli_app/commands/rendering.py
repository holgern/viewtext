from __future__ import annotations

# ruff: noqa: C901
import json
from typing import Any

import typer
from rich.console import Console
from rich.table import Table

from viewtext.cli_app.config import ConfigManager
from viewtext.cli_app.context import resolve_context_data
from viewtext.engine import LayoutEngine
from viewtext.registry_builder import get_registry_from_config


def register_render_commands(
    app: typer.Typer,
    console: Console,
    config_manager: ConfigManager,
) -> None:  # noqa: C901
    @app.command()
    def render(
        ctx: typer.Context,
        layout_name: str = typer.Argument(..., help="Name of the layout to render"),
        field_registry: str | None = typer.Option(
            None, "--registry", "-r", help="Custom field registry module path"
        ),
        json_output: bool = typer.Option(
            False, "--json", "-j", help="Output rendered lines as JSON"
        ),
    ) -> None:
        try:
            config_files, loader = config_manager.get_loader_and_configs(ctx)
            layout = loader.get_layout(layout_name)

            if field_registry:
                console.print(
                    "[yellow]Custom registry support not yet implemented[/yellow]"
                )
                registry = None
            else:
                registry = get_registry_from_config(loader=loader)

            engine = LayoutEngine(field_registry=registry, layout_loader=loader)
            context = resolve_context_data(loader, console)

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

                    for index, line in enumerate(lines):
                        console.print(f"[cyan]{index}:[/cyan] {line}")

                    console.print("[dim]" + "─" * 80 + "[/dim]\n")

        except ValueError as exc:
            console.print(f"[red]Error:[/red] {exc}")
            raise typer.Exit(code=1) from None
        except FileNotFoundError as exc:
            console.print(f"[red]Error:[/red] {exc}")
            raise typer.Exit(code=1) from None
        except Exception as exc:  # noqa: BLE001
            console.print(f"[red]Error rendering layout:[/red] {exc}")
            raise typer.Exit(code=1) from None

    @app.command(name="render-inputs")
    def render_inputs(
        ctx: typer.Context,
        layout: str | None = typer.Option(
            None,
            "--layout",
            "-l",
            help="Limit to inputs referenced by the specified layout",
        ),
        json_output: bool = typer.Option(
            False, "--json", "-j", help="Output rendered inputs as JSON"
        ),
    ) -> None:  # noqa: C901
        try:
            config_files, loader = config_manager.get_loader_and_configs(ctx)
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
                            presenter_cfg = layouts_config.presenters.get(
                                line.presenter
                            )
                            if presenter_cfg and presenter_cfg.input:
                                referenced_inputs.add(presenter_cfg.input)

                if layout_cfg.items:
                    for item in layout_cfg.items:
                        if item.input:
                            referenced_inputs.add(item.input)
                        if item.presenter and layouts_config.presenters:
                            presenter_cfg = layouts_config.presenters.get(
                                item.presenter
                            )
                            if presenter_cfg and presenter_cfg.input:
                                referenced_inputs.add(presenter_cfg.input)

                inputs_to_show = [
                    name
                    for name in sorted(input_mappings.keys())
                    if name in referenced_inputs
                ]

                if not inputs_to_show:
                    console.print(
                        f"[yellow]Layout '{layout}' does not reference any "
                        "inputs[/yellow]"
                    )
                    return
            else:
                inputs_to_show = sorted(input_mappings.keys())

            registry = get_registry_from_config(loader=loader)
            context = resolve_context_data(loader, console)
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

            table = Table(
                title="Rendered Inputs", show_header=True, header_style="bold"
            )
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
            total_inputs_rendered = len(inputs_to_show)
            console.print(
                f"\n[bold]Total inputs rendered:[/bold] {total_inputs_rendered}\n"
            )

        except typer.Exit:
            raise
        except FileNotFoundError as exc:
            console.print(f"[red]Error:[/red] {exc}")
            raise typer.Exit(code=1) from None
        except Exception as exc:  # noqa: BLE001
            console.print(f"[red]Error rendering inputs:[/red] {exc}")
            raise typer.Exit(code=1) from None

    @app.command(name="render-presenters")
    def render_presenters(
        ctx: typer.Context,
        layout: str | None = typer.Option(
            None,
            "--layout",
            "-l",
            help="Limit to presenters referenced by the specified layout",
        ),
        json_output: bool = typer.Option(
            False, "--json", "-j", help="Output rendered presenters as JSON"
        ),
    ) -> None:  # noqa: C901
        try:
            config_files, loader = config_manager.get_loader_and_configs(ctx)
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
                        f"[yellow]Layout '{layout}' does not reference any "
                        "presenters[/yellow]"
                    )
                    return
            else:
                presenter_names = sorted(presenters.keys())

            registry = get_registry_from_config(loader=loader)
            input_mappings = loader.get_input_mappings()
            context = resolve_context_data(loader, console)
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
                    formatted_value = engine._format_value(  # noqa: SLF001
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
                title="Rendered Presenters",
                show_header=True,
                header_style="bold",
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
            total_presenters_rendered = len(presenter_names)
            console.print(
                f"\n[bold]Total presenters rendered:[/bold] "
                f"{total_presenters_rendered}\n"
            )

        except typer.Exit:
            raise
        except FileNotFoundError as exc:
            console.print(f"[red]Error:[/red] {exc}")
            raise typer.Exit(code=1) from None
        except Exception as exc:  # noqa: BLE001
            console.print(f"[red]Error rendering presenters:[/red] {exc}")
            raise typer.Exit(code=1) from None
