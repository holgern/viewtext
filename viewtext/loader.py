import os
import sys
from typing import Any

from pydantic import BaseModel, Field


class LineConfig(BaseModel):
    field: str
    index: int
    formatter: str | None = None
    formatter_params: dict[str, Any] = Field(default_factory=dict)


class LayoutConfig(BaseModel):
    name: str
    lines: list[LineConfig]


class FormatterConfigParams(BaseModel):
    type: str
    symbol: str | None = None
    decimals: int | None = None
    thousands_sep: str | None = None
    prefix: str | None = None
    suffix: str | None = None
    format: str | None = None
    symbol_position: str | None = None


class FieldMapping(BaseModel):
    context_key: str
    default: Any | None = None
    transform: str | None = None


class LayoutsConfig(BaseModel):
    layouts: dict[str, LayoutConfig]
    formatters: dict[str, FormatterConfigParams] | None = None
    fields: dict[str, FieldMapping] | None = None
    context_provider: str | None = None


class LayoutLoader:
    def __init__(self, config_path: str | None = None):
        if config_path is None:
            config_path = self._get_default_config_path()
        self.config_path = config_path
        self._layouts_config: LayoutsConfig | None = None

    @staticmethod
    def _get_default_config_path() -> str:
        base_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
        return os.path.join(base_dir, "layouts.toml")

    def _import_toml_libs(self) -> tuple[Any, Any]:
        """Import TOML libraries with fallback handling."""
        tomllib = None
        tomli_w = None

        try:
            if sys.version_info >= (3, 11):
                tomllib = __import__("tomllib")
            else:
                tomllib = __import__("tomli")
        except ImportError:
            pass

        try:
            tomli_w = __import__("tomli_w")
        except ImportError:
            pass

        return tomllib, tomli_w

    def load(self) -> LayoutsConfig:
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f"Layout config not found: {self.config_path}")

        tomllib, _ = self._import_toml_libs()
        if tomllib is None:
            raise ImportError(
                "TOML support not available. Install with: pip install tomli tomli-w"
            )

        with open(self.config_path, "rb") as f:
            data = tomllib.load(f)

        self._layouts_config = LayoutsConfig(**data)
        return self._layouts_config

    def get_layout(self, layout_name: str) -> dict[str, Any]:
        if self._layouts_config is None:
            self.load()

        assert self._layouts_config is not None

        if layout_name not in self._layouts_config.layouts:
            raise ValueError(f"Unknown layout: {layout_name}")

        layout = self._layouts_config.layouts[layout_name]
        return layout.model_dump()

    def get_formatter_params(self, formatter_name: str) -> dict[str, Any]:
        if self._layouts_config is None:
            self.load()

        assert self._layouts_config is not None

        if (
            self._layouts_config.formatters is None
            or formatter_name not in self._layouts_config.formatters
        ):
            return {}

        formatter_config = self._layouts_config.formatters[formatter_name]
        params = formatter_config.model_dump(exclude_none=True)
        params.pop("type", None)
        return params

    def get_field_mappings(self) -> dict[str, FieldMapping]:
        if self._layouts_config is None:
            self.load()

        assert self._layouts_config is not None

        if self._layouts_config.fields is None:
            return {}

        return self._layouts_config.fields

    def get_context_provider(self) -> str | None:
        if self._layouts_config is None:
            self.load()

        assert self._layouts_config is not None

        return self._layouts_config.context_provider


_global_layout_loader: LayoutLoader | None = None


def get_layout_loader(config_path: str | None = None) -> LayoutLoader:
    global _global_layout_loader
    if _global_layout_loader is None:
        _global_layout_loader = LayoutLoader(config_path)
    return _global_layout_loader
