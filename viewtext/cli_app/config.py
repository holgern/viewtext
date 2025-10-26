from __future__ import annotations

import os
from pathlib import Path

import typer

from viewtext.loader import LayoutLoader


class ConfigManager:
    def __init__(self, default_path: str = "layouts.toml") -> None:
        self._default_path = default_path
        self._current_path = default_path

    @property
    def current_path(self) -> str:
        return self._current_path

    def update_selected_configs(self, configs: list[str]) -> None:
        if configs:
            self._current_path = configs[0]
        else:
            self._current_path = self._default_path

    def resolve_cli_file(self, value: str | None, option_name: str) -> str | None:
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

        xdg_config_home = Path(
            os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config")
        )
        xdg_base = xdg_config_home / "viewtext"

        xdg_candidate = xdg_base / raw_path
        if xdg_candidate.exists():
            return str(xdg_candidate.resolve())

        if not raw_path.suffix:
            xdg_candidate_with_suffix = xdg_candidate.with_suffix(".toml")
            if xdg_candidate_with_suffix.exists():
                return str(xdg_candidate_with_suffix.resolve())

        message = (
            f"Could not find {option_name} file '{value}'. Checked current directory "
            f"and {xdg_base}."
        )
        raise FileNotFoundError(message)

    def resolve_config_files(self, ctx: typer.Context) -> list[str]:
        if ctx.obj is None:
            ctx.obj = {}

        raw_configs = ctx.obj.get("configs", [])
        if not raw_configs:
            raw_configs = [self._current_path]

        resolved_paths: list[str] = []
        for raw_config in raw_configs:
            resolved = self.resolve_cli_file(raw_config, "config")
            if resolved is None:
                resolved = raw_config
            resolved_paths.append(resolved)

        self._current_path = resolved_paths[0]
        return resolved_paths

    def get_loader_and_configs(
        self, ctx: typer.Context
    ) -> tuple[list[str], LayoutLoader]:
        config_files = self.resolve_config_files(ctx)
        loader = LayoutLoader(config_files)
        return config_files, loader
