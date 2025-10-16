import os
from typing import Any, Optional

try:
    import tomllib  # type: ignore[import-not-found]
except ModuleNotFoundError:
    import tomli as tomllib

from pydantic import BaseModel, Field


class LineConfig(BaseModel):
    field: str
    index: int
    formatter: Optional[str] = None
    formatter_params: dict[str, Any] = Field(default_factory=dict)


class LayoutConfig(BaseModel):
    name: str
    lines: list[LineConfig]


class FormatterConfigParams(BaseModel):
    type: str
    symbol: Optional[str] = None
    decimals: Optional[int] = None
    thousands_sep: Optional[str] = None
    prefix: Optional[str] = None
    suffix: Optional[str] = None
    format: Optional[str] = None
    symbol_position: Optional[str] = None
    template: Optional[str] = None
    fields: Optional[list[str]] = None


class FieldMapping(BaseModel):
    context_key: str
    default: Optional[Any] = None
    transform: Optional[str] = None


class LayoutsConfig(BaseModel):
    layouts: dict[str, LayoutConfig]
    formatters: Optional[dict[str, FormatterConfigParams]] = None
    fields: Optional[dict[str, FieldMapping]] = None
    context_provider: Optional[str] = None


class LayoutLoader:
    def __init__(self, config_path: Optional[str] = None):
        if config_path is None:
            config_path = self._get_default_config_path()
        self.config_path = config_path
        self._layouts_config: Optional[LayoutsConfig] = None

    @staticmethod
    def _get_default_config_path() -> str:
        base_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
        return os.path.join(base_dir, "layouts.toml")

    def load(self) -> LayoutsConfig:
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f"Layout config not found: {self.config_path}")

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

    def get_context_provider(self) -> Optional[str]:
        if self._layouts_config is None:
            self.load()

        assert self._layouts_config is not None

        return self._layouts_config.context_provider


_global_layout_loader: Optional[LayoutLoader] = None


def get_layout_loader(config_path: Optional[str] = None) -> LayoutLoader:
    global _global_layout_loader
    if _global_layout_loader is None:
        _global_layout_loader = LayoutLoader(config_path)
    return _global_layout_loader
