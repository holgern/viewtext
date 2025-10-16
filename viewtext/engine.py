from typing import Any

from .formatters import get_formatter_registry
from .registry import BaseFieldRegistry


class LayoutEngine:
    def __init__(self, field_registry: BaseFieldRegistry | None = None):
        self.field_registry = field_registry
        self.formatter_registry = get_formatter_registry()

    def build_line_str(
        self, layout_config: dict[str, Any], context: dict[str, Any]
    ) -> list[str]:
        lines = layout_config.get("lines", [])

        max_index = max((line.get("index", 0) for line in lines), default=0)
        line_str = [""] * (max_index + 1)

        for line_config in lines:
            index = line_config.get("index")
            field_name = line_config.get("field")
            formatter_name = line_config.get("formatter")
            formatter_params = line_config.get("formatter_params", {})

            if index is None or field_name is None:
                continue

            value = self._get_field_value(field_name, context)

            if formatter_name:
                value = self._format_value(value, formatter_name, formatter_params)

            if index < len(line_str):
                line_str[index] = str(value) if value is not None else ""

        return line_str

    def _get_field_value(self, field_name: str, context: dict[str, Any]) -> Any:
        if self.field_registry and self.field_registry.has_field(field_name):
            getter = self.field_registry.get(field_name)
            return getter(context)
        elif field_name in context:
            return context[field_name]
        else:
            return None

    def _format_value(
        self, value: Any, formatter_name: str, formatter_params: dict[str, Any]
    ) -> Any:
        if not formatter_params:
            formatter_params = {}

        formatter_type = formatter_params.get("type", formatter_name)

        try:
            formatter = self.formatter_registry.get(formatter_type)
        except ValueError:
            formatter = self.formatter_registry.get("text")

        return formatter(value, **formatter_params)


_global_layout_engine: LayoutEngine | None = None


def get_layout_engine(field_registry: BaseFieldRegistry | None = None) -> LayoutEngine:
    global _global_layout_engine
    if _global_layout_engine is None and field_registry is not None:
        _global_layout_engine = LayoutEngine(field_registry)
    if _global_layout_engine is None:
        raise ValueError("LayoutEngine not initialized. Provide a field_registry.")
    return _global_layout_engine
