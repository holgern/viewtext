from datetime import datetime
from typing import Any, Callable


class FormatterRegistry:
    def __init__(self) -> None:
        self._formatters: dict[str, Callable] = {}
        self._register_builtin_formatters()

    def _register_builtin_formatters(self) -> None:
        self.register("text", self._format_text)
        self.register("text_uppercase", self._format_text_uppercase)
        self.register("price", self._format_price)
        self.register("number", self._format_number)
        self.register("datetime", self._format_datetime)
        self.register("relative_time", self._format_relative_time)
        self.register("template", self._format_template)

    def register(self, name: str, formatter: Callable) -> None:
        self._formatters[name] = formatter

    def get(self, name: str) -> Callable:
        if name not in self._formatters:
            raise ValueError(f"Unknown formatter: {name}")
        return self._formatters[name]

    @staticmethod
    def _format_text(value: Any, **kwargs: Any) -> str:
        prefix = kwargs.get("prefix", "")
        suffix = kwargs.get("suffix", "")
        return f"{prefix}{str(value)}{suffix}"

    @staticmethod
    def _format_text_uppercase(value: Any, **kwargs: Any) -> str:
        return str(value).upper()

    @staticmethod
    def _format_price(value: Any, **kwargs: Any) -> str:
        symbol = kwargs.get("symbol", "")
        decimals = kwargs.get("decimals", 2)
        thousands_sep = kwargs.get("thousands_sep", "")

        if value is None:
            return ""

        try:
            num_val = float(value)
        except (ValueError, TypeError):
            return str(value)

        if thousands_sep:
            formatted = f"{num_val:,.{decimals}f}"
        else:
            formatted = f"{num_val:.{decimals}f}"

        if symbol:
            symbol_position = kwargs.get("symbol_position", "prefix")
            if symbol_position == "suffix":
                return f"{formatted}{symbol}"
            else:
                return f"{symbol}{formatted}"

        return formatted

    @staticmethod
    def _format_number(value: Any, **kwargs: Any) -> str:
        prefix = kwargs.get("prefix", "")
        suffix = kwargs.get("suffix", "")
        decimals = kwargs.get("decimals", 0)
        thousands_sep = kwargs.get("thousands_sep", "")

        if value is None:
            return ""

        try:
            num_val = float(value)
        except (ValueError, TypeError):
            return str(value)

        if thousands_sep:
            formatted = f"{num_val:,.{decimals}f}"
        else:
            formatted = f"{num_val:.{decimals}f}"

        return f"{prefix}{formatted}{suffix}"

    @staticmethod
    def _format_datetime(value: Any, **kwargs: Any) -> str:
        format_str = kwargs.get("format", "%Y-%m-%d %H:%M:%S")

        if value is None:
            return ""

        if isinstance(value, datetime):
            return value.strftime(format_str)
        elif isinstance(value, (int, float)):
            return datetime.fromtimestamp(value).strftime(format_str)
        elif isinstance(value, str):
            return value

        return str(value)

    @staticmethod
    def _format_relative_time(value: Any, **kwargs: Any) -> str:
        format_type = kwargs.get("format", "short")

        if value is None:
            return ""

        try:
            seconds = int(value)
        except (ValueError, TypeError):
            return str(value)

        if seconds < 60:
            return (
                f"{seconds}s ago"
                if format_type == "short"
                else f"{seconds} seconds ago"
            )
        elif seconds < 3600:
            minutes = seconds // 60
            return (
                f"{minutes}m ago"
                if format_type == "short"
                else f"{minutes} minutes ago"
            )
        elif seconds < 86400:
            hours = seconds // 3600
            return f"{hours}h ago" if format_type == "short" else f"{hours} hours ago"
        else:
            days = seconds // 86400
            return f"{days}d ago" if format_type == "short" else f"{days} days ago"

    @staticmethod
    def _format_template(value: Any, **kwargs: Any) -> str:
        template = str(kwargs.get("template", "{}"))
        fields = kwargs.get("fields", [])

        if not isinstance(value, dict):
            return str(value)

        field_values: dict[str, Any] = {}
        for field_path in fields:
            val: Any = value
            for key in field_path.split("."):
                if isinstance(val, dict):
                    val = val.get(key)
                    if val is None:
                        break
                else:
                    val = None
                    break

            field_name = field_path.replace(".", "_")
            field_values[field_name] = val if val is not None else ""

        try:
            return str(template.format(**field_values))
        except (KeyError, ValueError) as e:
            return f"Template error: {e}"


_global_formatter_registry = FormatterRegistry()


def get_formatter_registry() -> FormatterRegistry:
    return _global_formatter_registry
