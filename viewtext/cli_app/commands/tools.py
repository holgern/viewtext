from __future__ import annotations

# ruff: noqa: C901
import ast
import json
import re
import sys
from pathlib import Path
from typing import Any

import typer
from rich.console import Console
from rich.table import Table

from viewtext.cli_app.config import ConfigManager
from viewtext.formatters import get_formatter_registry
from viewtext.loader import DictItemConfig, LineConfig
from viewtext.registry_builder import get_registry_from_config


def _layout_message(layout_name: str, item_label: str, detail: str) -> str:
    return f"Layout '{layout_name}', {item_label}: {detail}"


def _input_message(input_name: str, detail: str) -> str:
    return f"Input '{input_name}': {detail}"


def _presenter_message(presenter_name: str, detail: str) -> str:
    return f"Presenter '{presenter_name}': {detail}"


_CONTEXT_VALUES_ARGUMENT = typer.Argument(
    None,
    help="Context values in format key=value (e.g., membership=premium)",
)

_LAYOUT_OPTION = typer.Option(
    None,
    "--layout",
    "-l",
    help="Layout name to use for formatter parameters (e.g., for template formatters)",
)


def register_tools_commands(
    app: typer.Typer, console: Console, config_manager: ConfigManager
) -> None:  # noqa: C901
    @app.command(name="test")
    def test_input(
        ctx: typer.Context,
        input_name: str = typer.Argument(..., help="Name of the input to test"),
        context_values: list[str] = _CONTEXT_VALUES_ARGUMENT,
        formatter: str | None = typer.Option(
            None, "--formatter", "-F", help="Formatter to apply to the result"
        ),
        layout: str | None = _LAYOUT_OPTION,
    ) -> None:  # noqa: C901
        try:
            config_files, loader = config_manager.get_loader_and_configs(ctx)
            input_mappings = loader.get_input_mappings()

            if input_name not in input_mappings:
                console.print(f"[red]Error:[/red] Input '{input_name}' not found")
                available = ", ".join(sorted(input_mappings.keys()))
                console.print(f"\n[yellow]Available inputs:[/yellow] {available}")
                raise typer.Exit(code=1) from None

            context: dict[str, Any] = {}
            if context_values:
                for value_str in context_values:
                    if "=" not in value_str:
                        console.print(
                            f"[red]Error:[/red] Invalid context value '{value_str}'. "
                            "Expected format: key=value"
                        )
                        raise typer.Exit(code=1) from None
                    key, value = value_str.split("=", 1)
                    try:
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
                formatter_params: dict[str, Any] = {}

                if layout:
                    if layout not in layouts_config.layouts:
                        console.print(f"[red]Error:[/red] Layout '{layout}' not found")
                        available = ", ".join(sorted(layouts_config.layouts.keys()))
                        console.print(
                            f"\n[yellow]Available layouts:[/yellow] {available}"
                        )
                        raise typer.Exit(code=1) from None

                    layout_config = layouts_config.layouts[layout]
                    matching_line: LineConfig | DictItemConfig | None = None
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
                        for key, value in formatter_params.items():
                            console.print(f"  {key}: {value}")
                        console.print()
                    elif not matching_line:
                        console.print(
                            f"[yellow]Warning:[/yellow] Input '{input_name}' with "
                            f"formatter '{formatter}' not found in layout "
                            f"'{layout}'\n"
                        )
                elif (
                    layouts_config.formatters and formatter in layouts_config.formatters
                ):
                    formatter_config = layouts_config.formatters[formatter]
                    formatter_type = formatter_config.type
                    formatter_params = formatter_config.model_dump(exclude_none=True)
                    formatter_params.pop("type", None)

                if formatter_type == "template" and not formatter_params.get(
                    "template"
                ):
                    example_line = (
                        f"       Example: viewtext test {input_name} --formatter "
                        f"{formatter} --layout <layout_name>\n"
                    )
                    console.print(
                        "[yellow]Hint:[/yellow] Template formatter requires "
                        "'template' and 'fields' parameters.\n"
                        "       Use --layout option to specify a layout that uses "
                        "this formatter.\n",
                        example_line,
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
                            if all(
                                field.startswith(common_prefix + ".")
                                for field in fields_list
                            ):
                                if common_prefix not in result or not isinstance(
                                    result.get(common_prefix), dict
                                ):
                                    format_value = {common_prefix: result}

                    formatted_result = formatter_func(format_value, **formatter_params)
                    console.print(
                        f"[bold green]Formatted:[/bold green] {repr(formatted_result)}"
                    )
                except ValueError:
                    console.print(
                        f"[red]Error:[/red] Unknown formatter '{formatter_type}'"
                    )
                    raise typer.Exit(code=1) from None
                except Exception as exc:  # noqa: BLE001
                    console.print(f"[red]Error:[/red] {exc}")
                    raise typer.Exit(code=1) from None

        except typer.Exit:
            raise
        except FileNotFoundError as exc:
            console.print(f"[red]Error:[/red] {exc}")
            raise typer.Exit(code=1) from None
        except Exception as exc:  # noqa: BLE001
            console.print(f"[red]Error:[/red] {exc}")
            raise typer.Exit(code=1) from None

    @app.command()
    def check(ctx: typer.Context) -> None:  # noqa: C901
        errors: list[str] = []
        warnings: list[str] = []
        registry = None

        try:
            config_files, loader = config_manager.get_loader_and_configs(ctx)

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
            except Exception as exc:  # noqa: BLE001
                console.print(f"[red]✗ TOML syntax error:[/red] {exc}\n")
                raise typer.Exit(code=1) from None

            try:
                registry = get_registry_from_config(loader=loader)
                console.print("[green]✓ Input registry built successfully[/green]")
            except Exception as exc:  # noqa: BLE001
                errors.append(f"Failed to build input registry: {exc}")
                console.print(f"[red]✗ Input registry error:[/red] {exc}")

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
                items_to_check: list[tuple[str, LineConfig | DictItemConfig]] = []
                if layout_config.lines:
                    items_to_check.extend(
                        [
                            (f"line {index}", line)
                            for index, line in enumerate(layout_config.lines)
                        ]
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
                                _layout_message(
                                    layout_name,
                                    item_label,
                                    f"input '{input_name}' not defined "
                                    "in input registry",
                                )
                            )

                    presenter_name = (
                        item.presenter
                        if isinstance(item, LineConfig)
                        else item.presenter
                    )
                    if presenter_name:
                        if presenter_name not in defined_presenters:
                            errors.append(
                                _layout_message(
                                    layout_name,
                                    item_label,
                                    f"unknown presenter '{presenter_name}'",
                                )
                            )
                    else:
                        formatter_name = item.formatter
                        if formatter_name:
                            if formatter_name not in all_formatters:
                                errors.append(
                                    _layout_message(
                                        layout_name,
                                        item_label,
                                        f"unknown formatter '{formatter_name}'",
                                    )
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
                                            formatter_detail = (
                                                "formatter "
                                                f"'{formatter_name}' has unknown type "
                                                f"'{formatter_type}'"
                                            )
                                            errors.append(
                                                _layout_message(
                                                    layout_name,
                                                    item_label,
                                                    formatter_detail,
                                                )
                                            )

                        if formatter_name == "template" or (
                            formatter_name in defined_formatters
                            and layouts_config.formatters
                            and layouts_config.formatters[formatter_name].type
                            == "template"
                        ):
                            if not item.formatter_params.get("template"):
                                errors.append(
                                    _layout_message(
                                        layout_name,
                                        item_label,
                                        "template formatter missing 'template' "
                                        "parameter",
                                    )
                                )
                            if not item.formatter_params.get("fields"):
                                errors.append(
                                    _layout_message(
                                        layout_name,
                                        item_label,
                                        "template formatter missing 'fields' parameter",
                                    )
                                )
                            else:
                                template_fields = item.formatter_params.get(
                                    "fields", []
                                )
                                for template_field in template_fields:
                                    base_input = template_field.split(".")[0]
                                    if (
                                        base_input != input_name
                                        and base_input not in defined_inputs
                                    ):
                                        warnings.append(
                                            _layout_message(
                                                layout_name,
                                                item_label,
                                                "template references undefined input "
                                                f"'{base_input}'",
                                            )
                                        )

            if layouts_config.inputs:
                for input_name, input_mapping in layouts_config.inputs.items():
                    if input_mapping.type:
                        valid_types = {
                            "str",
                            "int",
                            "float",
                            "bool",
                            "list",
                            "dict",
                            "any",
                        }
                        if input_mapping.type not in valid_types:
                            errors.append(
                                _input_message(
                                    input_name,
                                    f"unknown type '{input_mapping.type}'",
                                )
                            )

                    if input_mapping.on_validation_error:
                        valid_strategies = {"raise", "skip", "use_default", "coerce"}
                        if input_mapping.on_validation_error not in valid_strategies:
                            errors.append(
                                _input_message(
                                    input_name,
                                    "unknown on_validation_error strategy "
                                    f"'{input_mapping.on_validation_error}'",
                                )
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
                                _input_message(
                                    input_name,
                                    "min_value/max_value constraints are typically "
                                    "used with numeric types (int/float), but input "
                                    f"has type '{input_mapping.type}'",
                                )
                            )

                    if (
                        input_mapping.min_length is not None
                        or input_mapping.max_length is not None
                    ):
                        if input_mapping.type and input_mapping.type not in {
                            "str",
                            "any",
                        }:
                            warnings.append(
                                _input_message(
                                    input_name,
                                    "min_length/max_length constraints are typically "
                                    "used with string types, but input has type "
                                    f"'{input_mapping.type}'",
                                )
                            )

                    if (
                        input_mapping.min_items is not None
                        or input_mapping.max_items is not None
                    ):
                        if input_mapping.type and input_mapping.type not in {
                            "list",
                            "any",
                        }:
                            warnings.append(
                                _input_message(
                                    input_name,
                                    "min_items/max_items constraints are typically "
                                    "used with list types, but input has type "
                                    f"'{input_mapping.type}'",
                                )
                            )

                    if input_mapping.pattern is not None:
                        if input_mapping.type and input_mapping.type not in {
                            "str",
                            "any",
                        }:
                            warnings.append(
                                _input_message(
                                    input_name,
                                    "pattern constraint is typically used with string "
                                    "types, but input has type "
                                    f"'{input_mapping.type}'",
                                )
                            )
                        else:
                            try:
                                re.compile(input_mapping.pattern)
                            except re.error as exc:
                                errors.append(
                                    _input_message(
                                        input_name,
                                        "invalid regex pattern "
                                        f"'{input_mapping.pattern}': {exc}",
                                    )
                                )

                    if (
                        input_mapping.on_validation_error == "use_default"
                        and input_mapping.default is None
                    ):
                        warnings.append(
                            _input_message(
                                input_name,
                                "on_validation_error='use_default' but no default "
                                "value is specified",
                            )
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
                                _input_message(
                                    input_name,
                                    f"unknown operation '{input_mapping.operation}'",
                                )
                            )

                        if input_mapping.sources:
                            for source in input_mapping.sources:
                                if source not in defined_inputs:
                                    warnings.append(
                                        _input_message(
                                            input_name,
                                            f"source input '{source}' not defined",
                                        )
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
                                _input_message(
                                    input_name,
                                    f"unknown transform '{input_mapping.transform}'",
                                )
                            )

            if layouts_config.presenters:
                for (
                    presenter_name,
                    presenter_config,
                ) in layouts_config.presenters.items():
                    if not presenter_config.input:
                        errors.append(
                            _presenter_message(
                                presenter_name,
                                "missing input specification",
                            )
                        )

                    if (
                        presenter_config.formatter
                        and presenter_config.formatter not in all_formatters
                    ):
                        errors.append(
                            _presenter_message(
                                presenter_name,
                                f"unknown formatter '{presenter_config.formatter}'",
                            )
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
                                _presenter_message(
                                    presenter_name,
                                    "formatter "
                                    f"'{presenter_config.formatter}' has unknown type "
                                    f"'{formatter_type}'",
                                )
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
                    "[bold green]✓ All checks passed! Configuration is valid."
                    "[/bold green]\n"
                )
            elif errors:
                console.print(
                    f"[bold red]✗ Validation failed with {len(errors)} error(s)"
                    "[/bold red]\n"
                )
                raise typer.Exit(code=1) from None
            else:
                console.print(
                    f"[bold yellow]⚠ Validation passed with {len(warnings)} warning(s)"
                    "[/bold yellow]\n"
                )

        except typer.Exit:
            raise
        except FileNotFoundError as exc:
            console.print(f"\n[red]Error:[/red] {exc}\n")
            raise typer.Exit(code=1) from None
        except Exception as exc:  # noqa: BLE001
            console.print(f"\n[red]Unexpected error:[/red] {exc}\n")
            raise typer.Exit(code=1) from None

    @app.command(name="generate-inputs")
    def generate_inputs(
        output: str | None = typer.Option(
            None, "--output", "-o", help="Output file path (defaults to stdout)"
        ),
        prefix: str = typer.Option("", "--prefix", "-p", help="Prefix for input names"),
    ) -> None:
        try:
            has_stdin_data = not sys.stdin.isatty()

            if not has_stdin_data:
                console.print(
                    "[red]Error:[/red] No stdin data provided. Pipe JSON data to "
                    "generate inputs."
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
            except json.JSONDecodeError as exc:
                console.print(f"[red]Error:[/red] Invalid JSON: {exc}")
                raise typer.Exit(code=1) from None

            if not isinstance(data, dict):
                console.print(
                    "[red]Error:[/red] JSON data must be an object/dictionary "
                    "at root level"
                )
                raise typer.Exit(code=1) from None

            toml_lines = _generate_input_definitions(data, prefix)

            if output:
                output_path = Path(output)
                try:
                    output_path.write_text(toml_lines)
                    console.print(
                        f"\n[green]✓ Input definitions written to:[/green] "
                        f"{output_path}\n"
                    )
                except OSError as exc:
                    console.print(f"[red]Error writing to file:[/red] {exc}")
                    raise typer.Exit(code=1) from None
            else:
                print(toml_lines)

        except typer.Exit:
            raise
        except Exception as exc:  # noqa: BLE001
            console.print(f"\n[red]Unexpected error:[/red] {exc}\n")
            raise typer.Exit(code=1) from None

    @app.command()
    def info(ctx: typer.Context) -> None:
        try:
            config_files, loader = config_manager.get_loader_and_configs(ctx)

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
                f"[bold]Presenters:[/bold] {len(layouts_config.presenters or {})} "
                "defined"
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
                    params_str = ", ".join(
                        f"{key}={value}" for key, value in params.items()
                    )
                    formatter_table.add_row(fmt_name, fmt_type, params_str)

                console.print()
                console.print(formatter_table)
            else:
                console.print("[bold]Global Formatters:[/bold] None defined in config")

            console.print()

        except FileNotFoundError as exc:
            console.print(f"\n[red]Error:[/red] {exc}\n")
            raise typer.Exit(code=1) from None
        except Exception as exc:  # noqa: BLE001
            console.print(f"\n[red]Error:[/red] {exc}\n")
            raise typer.Exit(code=1) from None


def _generate_input_definitions(
    data: dict[str, Any], prefix: str = "", path: str = ""
) -> str:
    lines: list[str] = []

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
