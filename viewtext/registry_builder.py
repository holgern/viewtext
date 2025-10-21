"""
Registry builder for creating field registries from TOML configuration.

This module provides classes for building field registries from TOML
configuration files, including support for complex context key parsing
with attribute access and method calls.
"""

import math
import re
from typing import Any, Callable, Optional, Union, cast

from .loader import FieldMapping, LayoutLoader
from .registry import BaseFieldRegistry
from .validator import FieldValidator


class MethodCallParser:
    """
    Parser for context_key strings with attribute access and method calls.

    The MethodCallParser enables complex field extraction patterns like
    dictionary lookups, attribute access, and method calls with arguments.

    Examples
    --------
    >>> operations = MethodCallParser.parse("ticker.name")
    >>> operations
    [('key', 'ticker', []), ('attr', 'name', [])]

    >>> operations = MethodCallParser.parse("ticker.get_price('fiat')")
    >>> operations
    [('key', 'ticker', []), ('method', 'get_price', ['fiat'])]
    """

    @staticmethod
    def parse(context_key: str) -> list[tuple[str, str, list[Any]]]:
        """
        Parse context_key into a chain of operations.

        Parameters
        ----------
        context_key : str
            The context key string to parse

        Returns
        -------
        list[tuple[str, str, list[Any]]]
            List of (type, name, args) tuples where:

            - type: 'key' (dict lookup), 'attr' (attribute), 'index'
              (array access), or 'method' (call)
            - name: key/attribute/method name or index number as string
            - args: list of arguments (empty for key/attr/index)

        Examples
        --------
        >>> MethodCallParser.parse("ticker")
        [('key', 'ticker', [])]

        >>> MethodCallParser.parse("ticker.name")
        [('key', 'ticker', []), ('attr', 'name', [])]

        >>> MethodCallParser.parse("items.0.name")
        [('key', 'items', []), ('index', '0', []), ('attr', 'name', [])]

        >>> MethodCallParser.parse("ticker.get_price()")
        [('key', 'ticker', []), ('method', 'get_price', [])]

        >>> MethodCallParser.parse("ticker.get_price('fiat')")
        [('key', 'ticker', []), ('method', 'get_price', ['fiat'])]

        >>> MethodCallParser.parse(
        ...     "portfolio.get_ticker('BTC').get_current_price('fiat')"
        ... )  # doctest: +NORMALIZE_WHITESPACE
        [('key', 'portfolio', []), ('method', 'get_ticker', ['BTC']),
         ('method', 'get_current_price', ['fiat'])]
        """
        operations: list[tuple[str, str, list[Any]]] = []
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
                    index_match = re.match(r"^(\d+)(\.(.+))?$", remaining)
                    if index_match:
                        index = index_match.group(1)
                        operations.append(("index", index, []))
                        remaining = index_match.group(3) or ""
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
    def _parse_args(args_str: str) -> list[Union[str, int, float, bool, None]]:
        """
        Parse argument string into Python values.

        Parameters
        ----------
        args_str : str
            Comma-separated argument string

        Returns
        -------
        list[Union[str, int, float, bool, None]]
            List of parsed argument values

        Examples
        --------
        >>> MethodCallParser._parse_args("'hello', 42, 3.14, True, None")
        ['hello', 42, 3.14, True, None]
        """
        if not args_str.strip():
            return []

        args: list[Union[str, int, float, bool, None]] = []
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
    """
    Builder for creating field registries from TOML configuration.

    The RegistryBuilder reads field mappings from TOML configuration files
    and creates a BaseFieldRegistry with getter functions that support
    complex field extraction patterns.

    Examples
    --------
    >>> from viewtext import RegistryBuilder
    >>> registry = RegistryBuilder.build_from_config("layouts.toml")
    >>> getter = registry.get("temperature")
    >>> getter({"temp": 25})
    25
    """

    OPERATIONS = {
        "celsius_to_fahrenheit": lambda v: v * 9 / 5 + 32,
        "fahrenheit_to_celsius": lambda v: (v - 32) * 5 / 9,
        "multiply": lambda *sources: (
            sources[0] * sources[1]
            if len(sources) >= 2
            else (sources[0] if sources else 0)
        ),
        "divide": lambda a, b: a / b if b != 0 else None,
        "add": lambda *sources: sum(sources),
        "subtract": lambda a, b: a - b if len([a, b]) == 2 else 0,
        "average": lambda *sources: sum(sources) / len(sources) if sources else 0,
        "min": lambda *sources: min(sources) if sources else None,
        "max": lambda *sources: max(sources) if sources else None,
        "abs": lambda v: abs(v),
        "round": lambda v, decimals=0: round(v, int(decimals)),
        "ceil": lambda v: math.ceil(v),
        "floor": lambda v: math.floor(v),
        "modulo": lambda a, b: a % b if b != 0 else None,
    }

    @staticmethod
    def build_from_config(
        config_path: Optional[str] = None, loader: Optional[LayoutLoader] = None
    ) -> BaseFieldRegistry:
        """
        Build a field registry from TOML configuration.

        Parameters
        ----------
        config_path : str, optional
            Path to the TOML configuration file
        loader : LayoutLoader, optional
            Pre-configured layout loader to use

        Returns
        -------
        BaseFieldRegistry
            Populated field registry

        Examples
        --------
        >>> registry = RegistryBuilder.build_from_config("layouts.toml")
        >>> registry.has_field("temperature")
        True
        """
        if loader is None:
            loader = LayoutLoader(config_path)
        field_mappings = loader.get_field_mappings()

        registry = BaseFieldRegistry()

        for field_name, mapping in field_mappings.items():
            if not mapping.operation:
                if mapping.python_function:
                    getter = RegistryBuilder._create_python_function_getter(
                        field_name, mapping
                    )
                else:
                    context_key = mapping.context_key or field_name
                    getter = RegistryBuilder._create_getter(
                        field_name,
                        context_key,
                        mapping.default,
                        mapping.transform,
                        mapping,
                    )
                registry.register(field_name, getter)

        for field_name, mapping in field_mappings.items():
            if mapping.operation:
                getter = RegistryBuilder._create_operation_getter(
                    field_name, mapping, registry
                )
                registry.register(field_name, getter)

        return registry

    @staticmethod
    def _create_getter(
        field_name: str,
        context_key: Optional[str] = None,
        default: Any = None,
        transform: Optional[str] = None,
        mapping: Optional[FieldMapping] = None,
    ) -> Callable[[dict[str, Any]], Any]:
        """
        Create a getter function for a field.

        Parameters
        ----------
        field_name : str
            Name of the field
        context_key : str, optional
            Context key string with optional attribute/method access
        default : Any, optional
            Default value if field is not found
        transform : str, optional
            Transform to apply (upper, lower, title, strip, int, float, str, bool)
        mapping : FieldMapping, optional
            Complete field mapping with validation configuration

        Returns
        -------
        Callable[[dict[str, Any]], Any]
            Getter function that extracts the field value from context

        Examples
        --------
        >>> getter = RegistryBuilder._create_getter("temp", "temperature", default=0)
        >>> getter({"temperature": 25})
        25
        >>> getter({})
        0
        """
        validator = None
        if mapping and mapping.type:
            validator = FieldValidator(
                field_name=field_name,
                field_type=mapping.type,
                on_validation_error=mapping.on_validation_error,
                default=default,
                min_value=mapping.min_value,
                max_value=mapping.max_value,
                min_length=mapping.min_length,
                max_length=mapping.max_length,
                pattern=mapping.pattern,
                allowed_values=mapping.allowed_values,
                min_items=mapping.min_items,
                max_items=mapping.max_items,
            )

        def getter(context: dict[str, Any]) -> Any:
            if context_key is None:
                return default

            operations = MethodCallParser.parse(context_key)

            try:
                value = None
                for op_type, name, args in operations:
                    if op_type == "key":
                        value = context.get(name)
                        if value is None:
                            return default
                    elif op_type == "attr":
                        if value is None:
                            return default
                        if isinstance(value, dict):
                            value = value.get(name)
                            if value is None:
                                return default
                        else:
                            value = getattr(value, name)
                    elif op_type == "index":
                        if value is None:
                            return default
                        if not isinstance(value, (list, tuple)):
                            return default
                        idx = int(name)
                        value = value[idx]
                    elif op_type == "method":
                        if value is None:
                            return default
                        method = getattr(value, name)
                        value = method(*args)

            except (AttributeError, TypeError, KeyError, IndexError, ValueError):
                return default

            if validator:
                value = validator.validate(value)

            if transform and value is not None:
                value = RegistryBuilder._apply_transform(value, transform)

            return value

        return getter

    @staticmethod
    def _create_python_function_getter(
        field_name: str,
        mapping: FieldMapping,
    ) -> Callable[[dict[str, Any]], Any]:
        """
        Create a getter function for fields that execute Python functions.

        Parameters
        ----------
        field_name : str
            Name of the field
        mapping : FieldMapping
            Field mapping configuration containing python_module and python_function

        Returns
        -------
        Callable[[dict[str, Any]], Any]
            Getter function that executes the Python function

        Examples
        --------
        >>> from viewtext.loader import FieldMapping
        >>> mapping = FieldMapping(
        ...     python_module="datetime",
        ...     python_function="datetime.now().timestamp()",
        ...     transform="int"
        ... )
        >>> getter = RegistryBuilder._create_python_function_getter(
        ...     "current_time", mapping
        ... )
        >>> result = getter({})
        >>> isinstance(result, int)
        True
        """
        python_module = mapping.python_module
        python_function = mapping.python_function
        default = mapping.default
        transform = mapping.transform

        validator = None
        if mapping.type:
            validator = FieldValidator(
                field_name=field_name,
                field_type=mapping.type,
                on_validation_error=mapping.on_validation_error,
                default=default,
                min_value=mapping.min_value,
                max_value=mapping.max_value,
                min_length=mapping.min_length,
                max_length=mapping.max_length,
                pattern=mapping.pattern,
                allowed_values=mapping.allowed_values,
                min_items=mapping.min_items,
                max_items=mapping.max_items,
            )

        def getter(context: dict[str, Any]) -> Any:
            cache_key = f"__python_function_cache_{field_name}"
            if cache_key in context:
                return context[cache_key]

            if not python_function:
                return default

            try:
                namespace: dict[str, Any] = {"__builtins__": __builtins__}
                if python_module:
                    exec(f"import {python_module}", namespace)

                # Type narrowing - at this point python_function is str
                assert isinstance(python_function, str)
                value = eval(python_function, namespace)

                if transform and value is not None:
                    value = RegistryBuilder._apply_transform(value, transform)

                if validator:
                    value = validator.validate(value)

                context[cache_key] = value
                return value

            except (
                ImportError,
                NameError,
                AttributeError,
                SyntaxError,
                TypeError,
                ValueError,
            ):
                return default

        return getter

    @staticmethod
    def _apply_transform(value: Any, transform: str) -> Any:
        """
        Apply a transform to a value.

        Parameters
        ----------
        value : Any
            The value to transform
        transform : str
            Transform name (upper, lower, title, strip, int, float, str, bool)

        Returns
        -------
        Any
            Transformed value

        Examples
        --------
        >>> RegistryBuilder._apply_transform("hello", "upper")
        'HELLO'
        >>> RegistryBuilder._apply_transform("  text  ", "strip")
        'text'
        >>> RegistryBuilder._apply_transform("123", "int")
        123
        """
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

    @staticmethod
    def _get_source_value(
        context: dict[str, Any],
        source: str,
        default: Any,
        registry: Optional[BaseFieldRegistry] = None,
    ) -> Optional[float]:
        """Get numeric value from source field, resolving through
        registry if available."""
        if registry and registry.has_field(source):
            getter = registry.get(source)
            value = getter(context)
        else:
            value = context.get(source)

        if value is None or not isinstance(value, (int, float)):
            return None
        return float(value)

    @staticmethod
    def _get_numeric_value(
        context: dict[str, Any], key: str, default: Any
    ) -> Optional[float]:
        """Get numeric value from context with validation."""
        value = context.get(key)
        if value is None or not isinstance(value, (int, float)):
            return None
        return float(value)

    @staticmethod
    def _apply_linear_transform(
        value: float,
        multiply: Optional[float],
        divide: Optional[float],
        add: Optional[float],
        default: Any,
    ) -> Any:
        """Apply linear transformation (multiply/divide/add) to a value."""
        m = multiply if multiply is not None else 1
        d = divide if divide is not None else 1
        a = add if add is not None else 0
        if d == 0:
            return default
        return (value * m / d) + a

    @staticmethod
    def _handle_linear_transform(
        context: dict[str, Any],
        params: dict[str, Any],
    ) -> Any:
        """Handle linear_transform operation."""
        sources = params.get("sources")
        context_key = params.get("context_key")
        default = params.get("default")
        multiply = params.get("multiply")
        divide = params.get("divide")
        add = params.get("add")

        source_key = sources[0] if sources else context_key
        if source_key is None or not isinstance(source_key, str):
            return default
        value = RegistryBuilder._get_numeric_value(context, source_key, default)
        if value is None:
            return default
        return RegistryBuilder._apply_linear_transform(
            value, multiply, divide, add, default
        )

    @staticmethod
    def _handle_sources_operation(
        context: dict[str, Any],
        operation: str,
        op_func: Callable[..., Any],
        params: dict[str, Any],
        registry: Optional[BaseFieldRegistry] = None,
    ) -> Any:
        """Handle operations with multiple source values."""
        sources = params.get("sources", [])
        multiply = params.get("multiply")
        default = params.get("default")

        values = []
        for source in sources:
            val = RegistryBuilder._get_source_value(context, source, default, registry)
            if val is None:
                return default
            values.append(val)

        if operation == "round" and len(values) == 1:
            decimals = int(multiply) if multiply is not None else 0
            return op_func(values[0], decimals)
        result = op_func(*values)
        return result if result is not None else default

    @staticmethod
    def _handle_context_key_operation(
        context: dict[str, Any],
        operation: str,
        op_func: Callable[..., Any],
        params: dict[str, Any],
    ) -> Any:
        """Handle operations with single context key."""
        context_key = params.get("context_key")
        multiply = params.get("multiply")
        default = params.get("default")

        if context_key is None:
            return default

        value = RegistryBuilder._get_numeric_value(context, context_key, default)
        if value is None:
            return default

        if operation == "round":
            decimals = int(multiply) if multiply is not None else 0
            return op_func(value, decimals)
        return op_func(value)

    @staticmethod
    def _get_string_value(context: dict[str, Any], key: str, default: Any) -> Any:
        """Get string value from context."""
        value = context.get(key)
        if value is None:
            return default
        return str(value)

    @staticmethod
    def _handle_concat_operation(
        context: dict[str, Any],
        params: dict[str, Any],
    ) -> Any:
        """Handle concat operation for joining strings."""
        sources = params.get("sources", [])
        separator = params.get("separator") or ""
        prefix = params.get("prefix") or ""
        suffix = params.get("suffix") or ""
        skip_empty = params.get("skip_empty") or False
        default = params.get("default") or ""

        values = []
        for source in sources:
            val = RegistryBuilder._get_string_value(context, source, None)
            if val is None:
                if skip_empty:
                    continue
                return default
            values.append(val)

        if not values and not skip_empty:
            return default

        result = separator.join(values)
        return f"{prefix}{result}{suffix}"

    @staticmethod
    def _handle_split_operation(
        context: dict[str, Any],
        params: dict[str, Any],
    ) -> Any:
        """Handle split operation for splitting strings."""
        context_key = params.get("context_key")
        sources = params.get("sources")
        separator = params.get("separator", " ")
        index = params.get("index")
        default = params.get("default", "")

        source_key = sources[0] if sources else context_key
        if source_key is None:
            return default

        value = RegistryBuilder._get_string_value(context, source_key, None)
        if value is None:
            return default

        parts = value.split(separator)
        if index is not None:
            if -len(parts) <= index < len(parts):
                return parts[index]
            return default
        return parts

    @staticmethod
    def _handle_substring_operation(
        context: dict[str, Any],
        params: dict[str, Any],
    ) -> Any:
        """Handle substring operation for extracting substrings."""
        context_key = params.get("context_key")
        sources = params.get("sources")
        start = params.get("start", 0)
        end = params.get("end")
        default = params.get("default", "")

        source_key = sources[0] if sources else context_key
        if source_key is None:
            return default

        value = RegistryBuilder._get_string_value(context, source_key, None)
        if value is None:
            return default

        if end is None:
            return value[start:]
        return value[start:end]

    @staticmethod
    def _handle_conditional_operation(
        context: dict[str, Any],
        params: dict[str, Any],
    ) -> Any:
        """Handle conditional operation for if/else logic."""
        condition = params.get("condition")
        if_true = params.get("if_true")
        if_false = params.get("if_false")
        default = params.get("default", "")

        if condition is None or if_true is None or if_false is None:
            return default

        field = condition.get("field")
        equals = condition.get("equals")

        if field is None:
            return default

        field_value = context.get(field)

        if field_value is None:
            return default

        condition_met = field_value == equals

        result_template = if_true if condition_met else if_false

        result = RegistryBuilder._resolve_field_references(
            result_template, context, default
        )
        return result

    @staticmethod
    def _handle_format_number_operation(
        context: dict[str, Any],
        params: dict[str, Any],
    ) -> Any:
        """Handle format_number operation for formatting numbers with separators."""
        context_key = params.get("context_key")
        sources = params.get("sources")
        thousands_sep = params.get("thousands_sep") or ""
        decimal_sep = params.get("decimal_sep") or "."
        decimals_param = params.get("decimals_param") or 0
        default = params.get("default") or ""

        source_key = sources[0] if sources else context_key
        if source_key is None:
            return default

        value = RegistryBuilder._get_numeric_value(context, source_key, None)
        if value is None:
            return default

        try:
            if thousands_sep or decimal_sep != ".":
                formatted = f"{value:,.{decimals_param}f}"
                if decimal_sep != ".":
                    formatted = formatted.replace(".", "\x00")
                if thousands_sep:
                    formatted = formatted.replace(",", thousands_sep)
                else:
                    formatted = formatted.replace(",", "")
                if decimal_sep != ".":
                    formatted = formatted.replace("\x00", decimal_sep)
            else:
                formatted = f"{value:.{decimals_param}f}"
            return formatted
        except (ValueError, TypeError):
            return default

    @staticmethod
    def _resolve_field_references(
        template: str, context: dict[str, Any], default: Any
    ) -> str:
        """Resolve ~field_name~ references in a template string."""
        import re

        pattern = r"~([^~]+)~"

        def replace_field(match: re.Match[str]) -> str:
            field_name = match.group(1)
            value = context.get(field_name)
            if value is None:
                return str(default) if default is not None else ""
            return str(value)

        result = re.sub(pattern, replace_field, template)
        return result

    @staticmethod
    def _create_operation_getter(
        field_name: str,
        mapping: FieldMapping,
        registry: Optional[BaseFieldRegistry] = None,
    ) -> Callable[[dict[str, Any]], Any]:
        """
        Create a getter function for computed fields with operations.

        Parameters
        ----------
        field_name : str
            Name of the field
        mapping : FieldMapping
            Field mapping configuration containing operation and parameters

        Returns
        -------
        Callable[[dict[str, Any]], Any]
            Getter function that computes the field value

        Examples
        --------
        >>> from viewtext.loader import FieldMapping
        >>> mapping = FieldMapping(
        ...     operation="celsius_to_fahrenheit",
        ...     context_key="temp_c"
        ... )
        >>> getter = RegistryBuilder._create_operation_getter("temp_f", mapping)
        >>> getter({"temp_c": 0})
        32.0
        """
        operation = mapping.operation
        string_operations = [
            "concat",
            "split",
            "substring",
            "conditional",
            "format_number",
        ]
        if (
            operation not in RegistryBuilder.OPERATIONS
            and operation != "linear_transform"
            and operation not in string_operations
        ):
            raise ValueError(f"Unknown operation: {operation}")

        validator = None
        if mapping.type:
            validator = FieldValidator(
                field_name=field_name,
                field_type=mapping.type,
                on_validation_error=mapping.on_validation_error,
                default=mapping.default,
                min_value=mapping.min_value,
                max_value=mapping.max_value,
                min_length=mapping.min_length,
                max_length=mapping.max_length,
                pattern=mapping.pattern,
                allowed_values=mapping.allowed_values,
                min_items=mapping.min_items,
                max_items=mapping.max_items,
            )

        params = {
            "sources": mapping.sources,
            "context_key": mapping.context_key,
            "default": mapping.default,
            "multiply": mapping.multiply,
            "add": mapping.add,
            "divide": mapping.divide,
            "start": mapping.start,
            "end": mapping.end,
            "separator": mapping.separator,
            "index": mapping.index,
            "condition": mapping.condition,
            "if_true": mapping.if_true,
            "if_false": mapping.if_false,
            "thousands_sep": mapping.thousands_sep,
            "decimal_sep": mapping.decimal_sep,
            "decimals_param": mapping.decimals_param,
            "prefix": mapping.prefix,
            "suffix": mapping.suffix,
            "skip_empty": mapping.skip_empty,
        }

        def getter(context: dict[str, Any]) -> Any:
            try:
                result = None
                if operation == "linear_transform":
                    result = RegistryBuilder._handle_linear_transform(context, params)

                elif operation == "concat":
                    result = RegistryBuilder._handle_concat_operation(context, params)

                elif operation == "split":
                    result = RegistryBuilder._handle_split_operation(context, params)

                elif operation == "substring":
                    result = RegistryBuilder._handle_substring_operation(
                        context, params
                    )

                elif operation == "conditional":
                    result = RegistryBuilder._handle_conditional_operation(
                        context, params
                    )

                elif operation == "format_number":
                    result = RegistryBuilder._handle_format_number_operation(
                        context, params
                    )

                else:
                    op_func = RegistryBuilder.OPERATIONS.get(operation)
                    if op_func is None:
                        result = params["default"]
                    else:
                        op_func_typed = cast(Callable[..., Any], op_func)

                        if params["sources"]:
                            result = RegistryBuilder._handle_sources_operation(
                                context, operation, op_func_typed, params, registry
                            )
                        elif params["context_key"]:
                            result = RegistryBuilder._handle_context_key_operation(
                                context, operation, op_func_typed, params
                            )
                        else:
                            result = params["default"]

                if validator and result is not None:
                    result = validator.validate(result)

                return result

            except (TypeError, ValueError, ZeroDivisionError, KeyError, IndexError):
                return params["default"]

        return getter


def get_registry_from_config(
    config_path: Optional[str] = None, loader: Optional[LayoutLoader] = None
) -> BaseFieldRegistry:
    """
    Get a field registry from TOML configuration.

    Convenience function that calls RegistryBuilder.build_from_config.

    Parameters
    ----------
    config_path : str, optional
        Path to the TOML configuration file
    loader : LayoutLoader, optional
        Pre-configured layout loader to use

    Returns
    -------
    BaseFieldRegistry
        Populated field registry

    Examples
    --------
    >>> from viewtext import get_registry_from_config
    >>> registry = get_registry_from_config("layouts.toml")
    >>> getter = registry.get("temperature")
    """
    return RegistryBuilder.build_from_config(config_path, loader)
