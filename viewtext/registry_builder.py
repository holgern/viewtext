import re
from typing import Any

from .loader import LayoutLoader
from .registry import BaseFieldRegistry


class MethodCallParser:
    """Parse context_key strings for attribute access and method calls."""

    @staticmethod
    def parse(context_key: str) -> list[tuple[str, str, list[Any]]]:
        """
        Parse context_key into a chain of operations.

        Returns:
            List of (type, name, args) tuples where:
            - type: 'key' (dict lookup), 'attr' (attribute),
              or 'method' (method call)
            - name: key/attribute/method name
            - args: list of arguments (empty for key/attr)

        Examples:
            "ticker" -> [('key', 'ticker', [])]
            "ticker.name" ->
                [('key', 'ticker', []), ('attr', 'name', [])]
            "ticker.get_price()" ->
                [('key', 'ticker', []), ('method', 'get_price', [])]
            "ticker.get_price('fiat')" ->
                [('key', 'ticker', []),
                 ('method', 'get_price', ['fiat'])]
            "portfolio.get_ticker('BTC').get_current_price('fiat')" ->
                [('key', 'portfolio', []),
                 ('method', 'get_ticker', ['BTC']),
                 ('method', 'get_current_price', ['fiat'])]
        """
        operations = []
        remaining = context_key
        first = True

        while remaining:
            if first:
                if "." in remaining:
                    key = remaining.split(".", 1)[0]
                    remaining = remaining[len(key) + 1 :]
                    operations.append(("key", key, []))
                    first = False
                else:
                    operations.append(("key", remaining, []))
                    remaining = ""
            else:
                method_match = re.match(r"^(\w+)\((.*?)\)(\.(.+))?$", remaining)
                if method_match:
                    method_name = method_match.group(1)
                    args_str = method_match.group(2)
                    args = MethodCallParser._parse_args(args_str)
                    operations.append(("method", method_name, args))
                    remaining = method_match.group(4) or ""
                else:
                    attr_match = re.match(r"^(\w+)(\.(.+))?$", remaining)
                    if attr_match:
                        attr_name = attr_match.group(1)
                        operations.append(("attr", attr_name, []))
                        remaining = attr_match.group(3) or ""
                    else:
                        break

        return operations

    @staticmethod
    def _parse_args(args_str: str) -> list[Any]:
        """Parse argument string into Python values."""
        if not args_str.strip():
            return []

        args = []
        for arg in args_str.split(","):
            arg = arg.strip()

            if (arg.startswith("'") and arg.endswith("'")) or (
                arg.startswith('"') and arg.endswith('"')
            ):
                args.append(arg[1:-1])
            elif arg.replace("-", "").replace(".", "").isdigit():
                if "." in arg:
                    args.append(float(arg))
                else:
                    args.append(int(arg))
            elif arg.lower() == "true":
                args.append(True)
            elif arg.lower() == "false":
                args.append(False)
            elif arg.lower() == "none":
                args.append(None)
            else:
                args.append(arg)

        return args


class RegistryBuilder:
    @staticmethod
    def build_from_config(
        config_path: str | None = None, loader: LayoutLoader | None = None
    ) -> BaseFieldRegistry:
        if loader is None:
            loader = LayoutLoader(config_path)
        field_mappings = loader.get_field_mappings()

        registry = BaseFieldRegistry()

        for field_name, mapping in field_mappings.items():
            context_key = mapping.context_key
            default = mapping.default
            transform = mapping.transform

            getter = RegistryBuilder._create_getter(context_key, default, transform)
            registry.register(field_name, getter)

        return registry

    @staticmethod
    def _create_getter(
        context_key: str, default: Any = None, transform: str | None = None
    ):
        def getter(context: dict[str, Any]) -> Any:
            operations = MethodCallParser.parse(context_key)

            try:
                value = None
                for op_type, name, args in operations:
                    if op_type == "key":
                        value = context.get(name)
                        if value is None:
                            return default
                    elif op_type == "attr":
                        value = getattr(value, name)
                    elif op_type == "method":
                        method = getattr(value, name)
                        value = method(*args)

            except (AttributeError, TypeError, KeyError):
                return default

            if transform and value is not None:
                value = RegistryBuilder._apply_transform(value, transform)

            return value

        return getter

    @staticmethod
    def _apply_transform(value: Any, transform: str) -> Any:
        if transform == "upper":
            return str(value).upper()
        elif transform == "lower":
            return str(value).lower()
        elif transform == "title":
            return str(value).title()
        elif transform == "strip":
            return str(value).strip()
        elif transform == "int":
            return int(value)
        elif transform == "float":
            return float(value)
        elif transform == "str":
            return str(value)
        elif transform == "bool":
            return bool(value)
        else:
            return value


def get_registry_from_config(
    config_path: str | None = None, loader: LayoutLoader | None = None
) -> BaseFieldRegistry:
    return RegistryBuilder.build_from_config(config_path, loader)
