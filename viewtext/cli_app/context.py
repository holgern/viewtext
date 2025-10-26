from __future__ import annotations

import importlib
import json
import sys
from typing import Any

import typer
from rich.console import Console

from viewtext.loader import LayoutLoader


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


def resolve_context_data(loader: LayoutLoader, console: Console) -> dict[str, Any]:
    has_stdin_data = not sys.stdin.isatty()

    if has_stdin_data:
        try:
            json_data = sys.stdin.read()
            if json_data.strip():
                context_data: Any = json.loads(json_data)
            else:
                raise ValueError("Empty stdin")
        except (json.JSONDecodeError, ValueError):
            context_data = _load_context_from_provider(loader, console)
    else:
        context_data = _load_context_from_provider(loader, console)

    if not isinstance(context_data, dict):
        console.print("[red]Error:[/red] Context data must be a JSON object/dictionary")
        raise typer.Exit(code=1) from None

    return context_data


def _load_context_from_provider(loader: LayoutLoader, console: Console) -> Any:
    context_provider_path = loader.get_context_provider()
    if not context_provider_path:
        return create_mock_context()

    try:
        module_name, func_name = context_provider_path.rsplit(".", 1)
        module = importlib.import_module(module_name)
        context_func = getattr(module, func_name)
        return context_func()
    except (ValueError, ImportError, AttributeError) as exc:
        msg = f"Error loading context provider '{context_provider_path}'"
        console.print(f"[red]{msg}:[/red] {exc}")
        raise typer.Exit(code=1) from None
    except Exception as exc:  # noqa: BLE001
        msg = f"Error calling context provider '{context_provider_path}'"
        console.print(f"[red]{msg}:[/red] {exc}")
        raise typer.Exit(code=1) from None
