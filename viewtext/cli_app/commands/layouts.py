from __future__ import annotations

from typing import Any

import typer
from rich.console import Console
from rich.table import Table

from viewtext.cli_app.config import ConfigManager


def register_layout_commands(
    app: typer.Typer,
    console: Console,
    config_manager: ConfigManager,
) -> None:
    @app.command(name="list")
    def list_layouts(ctx: typer.Context) -> None:
        try:
            config_files, loader = config_manager.get_loader_and_configs(ctx)
            layouts_config = loader.load()

            console.print("\n[bold green]Configuration Files:[/bold green]")
            for cfg in config_files:
                console.print(f"  • {cfg}")
            console.print()

            if not layouts_config.layouts:
                console.print("[yellow]No layouts found in configuration file[/yellow]")
                return

            table = Table(
                title="Available Layouts",
                show_header=True,
                header_style="bold",
            )
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
            total_layouts = len(layouts_config.layouts)
            console.print(f"\n[bold]Total layouts:[/bold] {total_layouts}\n")

        except FileNotFoundError as exc:
            console.print(f"[red]Error:[/red] {exc}")
            raise typer.Exit(code=1) from None
        except Exception as exc:  # noqa: BLE001
            console.print(f"[red]Error loading layouts:[/red] {exc}")
            raise typer.Exit(code=1) from None

    @app.command(name="show")
    def show_layout(
        ctx: typer.Context,
        layout_name: str = typer.Argument(..., help="Name of the layout to display"),
    ) -> None:
        try:
            config_files, loader = config_manager.get_loader_and_configs(ctx)
            layout: dict[str, Any] = loader.get_layout(layout_name)

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

        except ValueError as exc:
            console.print(f"[red]Error:[/red] {exc}")
            raise typer.Exit(code=1) from None
        except FileNotFoundError as exc:
            console.print(f"[red]Error:[/red] {exc}")
            raise typer.Exit(code=1) from None
        except Exception as exc:  # noqa: BLE001
            console.print(f"[red]Error displaying layout:[/red] {exc}")
            raise typer.Exit(code=1) from None
