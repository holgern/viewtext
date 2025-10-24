"""
Layout engine for building text grid layouts from configuration and context.

This module provides the LayoutEngine class that builds formatted text
layouts by combining field registries, formatters, and layout configurations.
"""

from typing import TYPE_CHECKING, Any, Optional

from .formatters import get_formatter_registry
from .registry import BaseFieldRegistry

if TYPE_CHECKING:
    from .loader import LayoutLoader


class LayoutEngine:
    """
    Engine for building text grid layouts from configuration and context data.

    The LayoutEngine combines a field registry and formatter registry to
    build formatted text layouts according to TOML layout configurations.

    Parameters
    ----------
    field_registry : BaseFieldRegistry, optional
        Registry of field getter functions. If None, fields are retrieved
        directly from the context dictionary.

    Attributes
    ----------
    field_registry : BaseFieldRegistry or None
        The field registry for resolving field values
    formatter_registry : FormatterRegistry
        The formatter registry for formatting values

    Examples
    --------
    >>> from viewtext import LayoutEngine, BaseFieldRegistry
    >>> registry = BaseFieldRegistry()
    >>> registry.register("temp", lambda ctx: ctx["temperature"])
    >>> engine = LayoutEngine(field_registry=registry)
    >>> layout = {
    ...     "lines": [
    ...         {"field": "temp", "index": 0, "formatter": "number",
    ...          "formatter_params": {"decimals": 1}}
    ...     ]
    ... }
    >>> result = engine.build_line_str(layout, {"temperature": 23.456})
    >>> result
    ['23.5']
    """

    def __init__(
        self,
        field_registry: Optional[BaseFieldRegistry] = None,
        layout_loader: Optional["LayoutLoader"] = None,
    ):
        """
        Initialize the layout engine.

        Parameters
        ----------
        field_registry : BaseFieldRegistry, optional
            Registry of field getter functions
        layout_loader : LayoutLoader, optional
            Layout loader for resolving formatter presets
        """
        self.field_registry = field_registry
        self.formatter_registry = get_formatter_registry()
        self.layout_loader = layout_loader

    def build_line_str(
        self, layout_config: dict[str, Any], context: dict[str, Any]
    ) -> list[str]:
        """
        Build formatted text lines from layout configuration and context.

        Parameters
        ----------
        layout_config : dict[str, Any]
            Layout configuration dictionary containing "lines" list
        context : dict[str, Any]
            Context dictionary containing data values

        Returns
        -------
        list[str]
            List of formatted text lines

        Examples
        --------
        >>> engine = LayoutEngine()
        >>> layout = {
        ...     "lines": [
        ...         {"field": "name", "index": 0},
        ...         {"field": "age", "index": 1}
        ...     ]
        ... }
        >>> result = engine.build_line_str(layout, {"name": "John", "age": 30})
        >>> result
        ['John', '30']
        """
        lines = layout_config.get("lines", [])

        max_index = max((line.get("index", 0) for line in lines), default=0)
        line_str = [""] * (max_index + 1)

        for line_config in lines:
            index = line_config.get("index")
            input_name = line_config.get("input")
            presenter_name = line_config.get("presenter")
            formatter_name = line_config.get("formatter")
            formatter_params = line_config.get("formatter_params", {})

            if index is None:
                continue

            # Use presenter definition if specified
            if presenter_name and self.layout_loader:
                presenter_config = self.layout_loader.get_presenter_config(
                    presenter_name
                )
                if presenter_config:
                    # Get input name from presenter config if not specified in line
                    if input_name is None:
                        input_name = presenter_config.get("input")
                    formatter_name = presenter_config.get("formatter")
                    formatter_params = presenter_config.get("formatter_params", {})

            if input_name is None:
                continue

            value = self._get_input_value(input_name, context)

            if formatter_name:
                value = self._format_value(
                    value, formatter_name, formatter_params, context
                )

            if index < len(line_str):
                line_str[index] = str(value) if value is not None else ""

        return line_str

    def build_dict_str(
        self, layout_config: dict[str, Any], context: dict[str, Any]
    ) -> dict[str, str]:
        """
        Build formatted dictionary from layout configuration and context.

        Parameters
        ----------
        layout_config : dict[str, Any]
            Layout configuration dictionary containing "items" list
        context : dict[str, Any]
            Context dictionary containing data values

        Returns
        -------
        dict[str, str]
            Dictionary mapping keys to formatted values

        Examples
        --------
        >>> engine = LayoutEngine()
        >>> layout = {
        ...     "items": [
        ...         {"field": "temp", "key": "temperature",
        ...          "formatter": "number", "formatter_params": {"suffix": "°"}},
        ...         {"field": "price", "key": "cost", "formatter": "price"}
        ...     ]
        ... }
        >>> result = engine.build_dict_str(layout, {"temp": 31, "price": 32})
        >>> result
        {'temperature': '31°', 'cost': '$32.00'}
        """
        items = layout_config.get("items", [])
        result = {}

        for item_config in items:
            key = item_config.get("key")
            input_name = item_config.get("input")
            presenter_name = item_config.get("presenter")
            formatter_name = item_config.get("formatter")
            formatter_params = item_config.get("formatter_params", {})

            if key is None:
                continue

            # Use presenter definition if specified
            if presenter_name and self.layout_loader:
                presenter_config = self.layout_loader.get_presenter_config(
                    presenter_name
                )
                if presenter_config:
                    # Get input name from presenter config if not specified in item
                    if input_name is None:
                        input_name = presenter_config.get("input")
                    formatter_name = presenter_config.get("formatter")
                    formatter_params = presenter_config.get("formatter_params", {})

            if input_name is None:
                continue

            value = self._get_input_value(input_name, context)

            if formatter_name:
                value = self._format_value(
                    value, formatter_name, formatter_params, context
                )

            result[key] = str(value) if value is not None else ""

        return result

    def _get_input_value(self, input_name: str, context: dict[str, Any]) -> Any:
        """
        Get field value from registry or context.

        Parameters
        ----------
        input_name : str
            Name of the input to retrieve
        context : dict[str, Any]
            Context dictionary

        Returns
        -------
        Any
            The field value, or None if not found
        """
        if self.field_registry and self.field_registry.has_field(input_name):
            getter = self.field_registry.get(input_name)
            return getter(context)
        elif input_name in context:
            return context[input_name]
        else:
            return None

    def _format_value(
        self,
        value: Any,
        formatter_name: str,
        formatter_params: dict[str, Any],
        context: Optional[dict[str, Any]] = None,
    ) -> Any:
        """
        Format a value using the specified formatter.

        Parameters
        ----------
        value : Any
            The value to format
        formatter_name : str
            Name of the formatter to use (can be a preset reference)
        formatter_params : dict[str, Any]
            Parameters to pass to the formatter
        context : dict[str, Any], optional
            Context dictionary for template formatter

        Returns
        -------
        Any
            The formatted value
        """
        if not formatter_params:
            formatter_params = {}

        if self.layout_loader and not formatter_params:
            preset = self.layout_loader.get_formatter_preset(formatter_name)
            if preset:
                formatter_type = preset.get("type", formatter_name)
                formatter_params = preset.copy()
                formatter_params.pop("type", None)
            else:
                formatter_type = formatter_name
        else:
            formatter_type = formatter_params.get("type", formatter_name)

        try:
            formatter = self.formatter_registry.get(formatter_type)
        except ValueError:
            formatter = self.formatter_registry.get("text")

        if formatter_type == "template" and context is not None:
            formatter_params = {
                **formatter_params,
                "_context": context,
                "_engine": self,
                "_loader": self.layout_loader,
            }

        return formatter(value, **formatter_params)


_global_layout_engine: Optional[LayoutEngine] = None


def get_layout_engine(
    field_registry: Optional[BaseFieldRegistry] = None,
) -> LayoutEngine:
    """
    Get or create the global layout engine instance.

    Parameters
    ----------
    field_registry : BaseFieldRegistry, optional
        Registry to use when creating a new engine instance

    Returns
    -------
    LayoutEngine
        The global layout engine instance

    Raises
    ------
    ValueError
        If no global engine exists and no field_registry is provided

    Examples
    --------
    >>> from viewtext import get_layout_engine, BaseFieldRegistry
    >>> registry = BaseFieldRegistry()
    >>> engine = get_layout_engine(field_registry=registry)
    """
    global _global_layout_engine
    if _global_layout_engine is None and field_registry is not None:
        _global_layout_engine = LayoutEngine(field_registry)
    if _global_layout_engine is None:
        raise ValueError("LayoutEngine not initialized. Provide a field_registry.")
    return _global_layout_engine
