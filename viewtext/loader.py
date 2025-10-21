"""
TOML configuration loader for layout definitions.

This module provides classes for loading and parsing TOML layout
configuration files using Pydantic models for validation.
"""

import os
from typing import Any, Optional

try:
    import tomllib  # type: ignore[import-not-found]
except ModuleNotFoundError:
    import tomli as tomllib

from pydantic import BaseModel, Field


class LineConfig(BaseModel):
    """
    Configuration for a single line in a layout.

    Attributes
    ----------
    field : str
        Name of the field to display
    index : int
        Line index (0-based position in the layout)
    formatter : str, optional
        Name of the formatter to apply
    formatter_params : dict[str, Any]
        Parameters to pass to the formatter
    """

    field: str
    index: int
    formatter: Optional[str] = None
    formatter_params: dict[str, Any] = Field(default_factory=dict)


class LayoutConfig(BaseModel):
    """
    Configuration for a complete layout.

    Attributes
    ----------
    name : str
        Display name of the layout
    lines : list[LineConfig]
        List of line configurations
    """

    name: str
    lines: list[LineConfig]


class FormatterConfigParams(BaseModel):
    """
    Configuration parameters for a formatter.

    Attributes
    ----------
    type : str
        Formatter type (text, number, price, datetime, etc.)
    symbol : str, optional
        Currency symbol for price formatter
    decimals : int, optional
        Number of decimal places
    thousands_sep : str, optional
        Thousands separator character
    decimal_sep : str, optional
        Decimal separator character
    prefix : str, optional
        String to prepend to the value
    suffix : str, optional
        String to append to the value
    format : str, optional
        Format string (e.g., datetime format)
    symbol_position : str, optional
        Position of currency symbol ("prefix" or "suffix")
    template : str, optional
        Template string with {field} placeholders
    fields : list[str], optional
        List of field names for template substitution
    """

    type: str
    symbol: Optional[str] = None
    decimals: Optional[int] = None
    thousands_sep: Optional[str] = None
    decimal_sep: Optional[str] = None
    prefix: Optional[str] = None
    suffix: Optional[str] = None
    format: Optional[str] = None
    symbol_position: Optional[str] = None
    template: Optional[str] = None
    fields: Optional[list[str]] = None


class FieldMapping(BaseModel):
    """
    Mapping configuration for a field.

    Attributes
    ----------
    context_key : str, optional
        Key to look up in the context dictionary
    default : Any, optional
        Default value if the field is not found
    transform : str, optional
        Transform to apply (upper, lower, title, strip, int, float, str, bool)
    operation : str, optional
        Named operation to apply (celsius_to_fahrenheit, multiply, add, etc.)
    sources : list[str], optional
        List of field names to use as sources for operations
    multiply : float, optional
        Multiplier for linear transform operations
    add : float, optional
        Addend for linear transform operations
    divide : float, optional
        Divisor for division operations
    start : int, optional
        Start index for substring operation
    end : int, optional
        End index for substring operation
    separator : str, optional
        Separator string for concat and split operations
    prefix : str, optional
        Prefix string for concat operation
    suffix : str, optional
        Suffix string for concat operation
    skip_empty : bool, optional
        Skip None/missing sources in concat operation instead of returning default
    thousands_sep : str, optional
        Thousands separator for format_number operation
    decimal_sep : str, optional
        Decimal separator for format_number operation
    decimals_param : int, optional
        Decimal places for format_number operation
    type : str, optional
        Expected type of the field value (str, int, float, bool, dict, list, any)
    on_validation_error : str, optional
        Error handling strategy (use_default, raise, skip, coerce)
    min_value : float, optional
        Minimum value for numeric types
    max_value : float, optional
        Maximum value for numeric types
    min_length : int, optional
        Minimum length for string types
    max_length : int, optional
        Maximum length for string types
    pattern : str, optional
        Regex pattern for string validation
    allowed_values : list[Any], optional
        List of allowed values (enum validation)
    min_items : int, optional
        Minimum number of items for list/array types
    max_items : int, optional
        Maximum number of items for list/array types
    python_module : str, optional
        Python module to import for python_function execution
    python_function : str, optional
        Python function call expression to execute (e.g., "datetime.now().timestamp()")
    """

    context_key: Optional[str] = None
    default: Optional[Any] = None
    transform: Optional[str] = None
    operation: Optional[str] = None
    sources: Optional[list[str]] = None
    multiply: Optional[float] = None
    add: Optional[float] = None
    divide: Optional[float] = None
    start: Optional[int] = None
    end: Optional[int] = None
    separator: Optional[str] = None
    prefix: Optional[str] = None
    suffix: Optional[str] = None
    skip_empty: Optional[bool] = None
    index: Optional[int] = None
    condition: Optional[dict[str, Any]] = None
    if_true: Optional[str] = None
    if_false: Optional[str] = None
    decimal_sep: Optional[str] = None
    thousands_sep: Optional[str] = None
    decimals_param: Optional[int] = None
    type: Optional[str] = None
    on_validation_error: Optional[str] = None
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    min_length: Optional[int] = None
    max_length: Optional[int] = None
    pattern: Optional[str] = None
    allowed_values: Optional[list[Any]] = None
    min_items: Optional[int] = None
    max_items: Optional[int] = None
    python_module: Optional[str] = None
    python_function: Optional[str] = None


class LayoutsConfig(BaseModel):
    """
    Complete configuration for all layouts.

    Attributes
    ----------
    layouts : dict[str, LayoutConfig]
        Dictionary of layout configurations
    formatters : dict[str, FormatterConfigParams], optional
        Dictionary of formatter configurations
    fields : dict[str, FieldMapping], optional
        Dictionary of field mappings
    context_provider : str, optional
        Name of the context provider to use
    """

    layouts: dict[str, LayoutConfig]
    formatters: Optional[dict[str, FormatterConfigParams]] = None
    fields: Optional[dict[str, FieldMapping]] = None
    context_provider: Optional[str] = None


class LayoutLoader:
    """
    Loader for TOML layout configuration files.

    The LayoutLoader reads and parses TOML files containing layout definitions,
    formatter configurations, and field mappings.

    Parameters
    ----------
    config_path : str, optional
        Path to the TOML configuration file. If None, uses default path.

    Attributes
    ----------
    config_path : str
        Path to the configuration file
    _layouts_config : LayoutsConfig or None
        Cached configuration after loading

    Examples
    --------
    >>> loader = LayoutLoader("layouts.toml")
    >>> layout = loader.get_layout("weather")
    >>> print(layout["name"])
    Weather Display
    """

    def __init__(
        self,
        config_path: Optional[str] = None,
        formatters_path: Optional[str] = None,
        fields_path: Optional[str] = None,
    ):
        """
        Initialize the layout loader.

        Parameters
        ----------
        config_path : str, optional
            Path to the TOML configuration file
        formatters_path : str, optional
            Path to separate formatters TOML file
        fields_path : str, optional
            Path to separate fields TOML file
        """
        if config_path is None:
            config_path = self._get_default_config_path()
        self.config_path = config_path
        self.formatters_path = formatters_path
        self.fields_path = fields_path
        self._layouts_config: Optional[LayoutsConfig] = None

    @staticmethod
    def _get_default_config_path() -> str:
        """
        Get the default configuration file path.

        Returns
        -------
        str
            Default path to layouts.toml in the project root
        """
        base_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
        return os.path.join(base_dir, "layouts.toml")

    def load(self) -> LayoutsConfig:
        """
        Load and parse the TOML configuration file.

        Returns
        -------
        LayoutsConfig
            Parsed configuration object

        Raises
        ------
        FileNotFoundError
            If the configuration file does not exist

        Examples
        --------
        >>> loader = LayoutLoader("layouts.toml")
        >>> config = loader.load()
        >>> print(list(config.layouts.keys()))
        ['demo', 'advanced']
        """
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f"Layout config not found: {self.config_path}")

        with open(self.config_path, "rb") as f:
            data = tomllib.load(f)

        if self.formatters_path or self.fields_path:
            data = self._merge_configs(data)

        self._layouts_config = LayoutsConfig(**data)
        return self._layouts_config

    def _merge_configs(self, base_data: dict[str, Any]) -> dict[str, Any]:
        """
        Merge additional configuration files into the base data.

        Parameters
        ----------
        base_data : dict[str, Any]
            Base configuration data from main config file

        Returns
        -------
        dict[str, Any]
            Merged configuration data
        """
        if self.formatters_path and os.path.exists(self.formatters_path):
            with open(self.formatters_path, "rb") as f:
                formatters_data = tomllib.load(f)
                if "formatters" in formatters_data:
                    if "formatters" not in base_data:
                        base_data["formatters"] = {}
                    base_data["formatters"].update(formatters_data["formatters"])

        if self.fields_path and os.path.exists(self.fields_path):
            with open(self.fields_path, "rb") as f:
                fields_data = tomllib.load(f)
                if "fields" in fields_data:
                    if "fields" not in base_data:
                        base_data["fields"] = {}
                    base_data["fields"].update(fields_data["fields"])

        return base_data

    @staticmethod
    def load_from_files(
        layouts_path: str,
        formatters_path: Optional[str] = None,
        fields_path: Optional[str] = None,
    ) -> LayoutsConfig:
        """
        Load configuration from multiple TOML files.

        Parameters
        ----------
        layouts_path : str
            Path to the layouts TOML file
        formatters_path : str, optional
            Path to the formatters TOML file
        fields_path : str, optional
            Path to the fields TOML file

        Returns
        -------
        LayoutsConfig
            Merged configuration object

        Raises
        ------
        FileNotFoundError
            If the layouts file does not exist

        Examples
        --------
        >>> config = LayoutLoader.load_from_files(
        ...     "layouts.toml",
        ...     formatters_path="formatters.toml",
        ...     fields_path="fields.toml"
        ... )
        >>> print(list(config.layouts.keys()))
        ['demo', 'advanced']
        """
        if not os.path.exists(layouts_path):
            raise FileNotFoundError(f"Layout config not found: {layouts_path}")

        with open(layouts_path, "rb") as f:
            data = tomllib.load(f)

        if formatters_path and os.path.exists(formatters_path):
            with open(formatters_path, "rb") as f:
                formatters_data = tomllib.load(f)
                if "formatters" in formatters_data:
                    if "formatters" not in data:
                        data["formatters"] = {}
                    data["formatters"].update(formatters_data["formatters"])

        if fields_path and os.path.exists(fields_path):
            with open(fields_path, "rb") as f:
                fields_data = tomllib.load(f)
                if "fields" in fields_data:
                    if "fields" not in data:
                        data["fields"] = {}
                    data["fields"].update(fields_data["fields"])

        return LayoutsConfig(**data)

    def get_layout(self, layout_name: str) -> dict[str, Any]:
        """
        Get a specific layout configuration by name.

        Parameters
        ----------
        layout_name : str
            Name of the layout to retrieve

        Returns
        -------
        dict[str, Any]
            Layout configuration dictionary

        Raises
        ------
        ValueError
            If the layout name is not found in the configuration

        Examples
        --------
        >>> loader = LayoutLoader("layouts.toml")
        >>> layout = loader.get_layout("demo")
        >>> print(layout["name"])
        Demo Display
        """
        if self._layouts_config is None:
            self.load()

        assert self._layouts_config is not None

        if layout_name not in self._layouts_config.layouts:
            raise ValueError(f"Unknown layout: {layout_name}")

        layout = self._layouts_config.layouts[layout_name]
        return layout.model_dump()

    def get_formatter_params(self, formatter_name: str) -> dict[str, Any]:
        """
        Get formatter configuration parameters by name.

        Parameters
        ----------
        formatter_name : str
            Name of the formatter

        Returns
        -------
        dict[str, Any]
            Formatter parameters dictionary, or empty dict if not found

        Examples
        --------
        >>> loader = LayoutLoader("layouts.toml")
        >>> params = loader.get_formatter_params("price_usd")
        >>> print(params["symbol"])
        $
        """
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

    def get_formatter_preset(self, preset_name: str) -> Optional[dict[str, Any]]:
        """
        Get formatter preset configuration by name.

        Parameters
        ----------
        preset_name : str
            Name of the formatter preset

        Returns
        -------
        dict[str, Any] or None
            Formatter preset configuration, or None if not found

        Examples
        --------
        >>> loader = LayoutLoader("layouts.toml")
        >>> preset = loader.get_formatter_preset("time_hms")
        >>> print(preset["type"])
        datetime
        """
        if self._layouts_config is None:
            self.load()

        assert self._layouts_config is not None

        if (
            self._layouts_config.formatters is None
            or preset_name not in self._layouts_config.formatters
        ):
            return None

        formatter_config = self._layouts_config.formatters[preset_name]
        return formatter_config.model_dump(exclude_none=True)

    def get_field_mappings(self) -> dict[str, FieldMapping]:
        """
        Get all field mapping configurations.

        Returns
        -------
        dict[str, FieldMapping]
            Dictionary of field mappings, or empty dict if none defined

        Examples
        --------
        >>> loader = LayoutLoader("layouts.toml")
        >>> mappings = loader.get_field_mappings()
        >>> print(mappings["temperature"].context_key)
        temp
        """
        if self._layouts_config is None:
            self.load()

        assert self._layouts_config is not None

        if self._layouts_config.fields is None:
            return {}

        return self._layouts_config.fields

    def get_context_provider(self) -> Optional[str]:
        """
        Get the configured context provider name.

        Returns
        -------
        str or None
            Context provider name, or None if not configured

        Examples
        --------
        >>> loader = LayoutLoader("layouts.toml")
        >>> provider = loader.get_context_provider()
        >>> print(provider)
        my_provider
        """
        if self._layouts_config is None:
            self.load()

        assert self._layouts_config is not None

        return self._layouts_config.context_provider


_global_layout_loader: Optional[LayoutLoader] = None


def get_layout_loader(config_path: Optional[str] = None) -> LayoutLoader:
    """
    Get or create the global layout loader instance.

    Parameters
    ----------
    config_path : str, optional
        Path to the configuration file for new instances

    Returns
    -------
    LayoutLoader
        The global layout loader instance

    Examples
    --------
    >>> from viewtext import get_layout_loader
    >>> loader = get_layout_loader("layouts.toml")
    >>> layout = loader.get_layout("demo")
    """
    global _global_layout_loader
    if _global_layout_loader is None:
        _global_layout_loader = LayoutLoader(config_path)
    return _global_layout_loader
