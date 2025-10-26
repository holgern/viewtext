from __future__ import annotations

import typer
from rich.console import Console

from viewtext.cli_app.commands.layouts import register_layout_commands
from viewtext.cli_app.commands.metadata import register_metadata_commands
from viewtext.cli_app.commands.rendering import register_render_commands
from viewtext.cli_app.commands.tools import register_tools_commands
from viewtext.cli_app.config import ConfigManager

console = Console()
config_manager = ConfigManager()

app = typer.Typer(help="ViewText CLI - Text grid layout generator")

_CONFIGS_OPTION = typer.Option(
    None,
    "--config",
    "-c",
    help="Path to TOML config file (can be repeated)",
)


@app.callback()
def main_callback(
    ctx: typer.Context,
    configs: list[str] | None = _CONFIGS_OPTION,
) -> None:
    selected_configs = configs or [config_manager.current_path]
    config_manager.update_selected_configs(selected_configs)
    ctx.obj = {"configs": selected_configs}


register_layout_commands(app, console, config_manager)
register_render_commands(app, console, config_manager)
register_metadata_commands(app, console, config_manager)
register_tools_commands(app, console, config_manager)


def main() -> None:
    app()
