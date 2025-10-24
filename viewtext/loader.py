"""
TOML configuration loader for layout definitions.

This module provides classes for loading and parsing TOML layout
configuration files using Pydantic models for validation.
"""

import os
from collections.abc import Sequence
from typing import Any, Optional, Union

try:
    import tomllib  # type: ignore[import-not-found]
except ModuleNotFoundError:
    import tomli as tomllib

from pydantic import BaseModel, Field


class PresenterConfig(BaseModel):
    """
    Configuration for a presenter definition that specifies how an input should look.

    Attributes
    ----------
    input : str
        Name of the input to display
    formatter : str
        Name of the formatter to apply
    formatter_params : dict[str, Any]
        Parameters to pass to the formatter
    """

    input: str
    formatter: str
    formatter_params: dict[str, Any] = Field(default_factory=dict)


class LineConfig(BaseModel):
    """
    Configuration for a single line in a layout.

    Attributes
    ----------
    input : str, optional
        Name of the input to display (can be specified in presenter definition)
    index : int
        Line index (0-based position in the layout)
    presenter : str, optional
        Name of the presenter definition to use
    formatter : str, optional
        Name of the formatter to apply when no presenter is used
    formatter_params : dict[str, Any], optional
        Parameters to pass to the formatter
    """

    input: Optional[str] = None
    index: int
    presenter: Optional[str] = None
    formatter: Optional[str] = None
    formatter_params: dict[str, Any] = Field(default_factory=dict)


class DictItemConfig(BaseModel):
    """
    Configuration for a single dictionary item in a layout.

    Attributes
    ----------
    input : str, optional
        Name of the input to display (can be specified in presenter definition)
    key : str
        Key name in the output dictionary
    presenter : str, optional
        Name of the presenter definition to use
    formatter : str, optional
        Name of the formatter to apply when no presenter is used
    formatter_params : dict[str, Any], optional
        Parameters to pass to the formatter
    """

    input: Optional[str] = None
    key: str
    presenter: Optional[str] = None
    formatter: Optional[str] = None
    formatter_params: dict[str, Any] = Field(default_factory=dict)


class LayoutConfig(BaseModel):
    """
    Configuration for a complete layout.

    Attributes
    ----------
    name : str
        Display name of the layout
    lines : list[LineConfig], optional
        List of line configurations (for line-based layouts)
    items : list[DictItemConfig], optional
        List of dict item configurations (for dict-based layouts)
    """

    name: str
    lines: Optional[list[LineConfig]] = None
    items: Optional[list[DictItemConfig]] = None


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


class InputMapping(BaseModel):
    """
    Mapping configuration for an input.

    Attributes
    ----------
    context_key : str, optional
        Key to look up in the context dictionary
    constant : Any, optional
        Constant value to use for this input (int, float, str, bool, etc.)
    default : Any, optional
        Default value if the input is not found
    transform : str, optional
        Transform to apply (upper, lower, title, strip, int, float, str, bool)
    operation : str, optional
        Named operation to apply (celsius_to_fahrenheit, multiply, add, etc.)
    sources : list[str], optional
        List of input names to use as sources for operations
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
        Expected type of the input value (str, int, float, bool, dict, list, any)
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
    constant: Optional[Any] = None
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
    inputs : dict[str, InputMapping], optional
        Dictionary of input mappings
    presenters : dict[str, PresenterConfig], optional
        Dictionary of presenter configurations
    context_provider : str, optional
        Name of the context provider to use
    """

    layouts: dict[str, LayoutConfig]
    formatters: Optional[dict[str, FormatterConfigParams]] = None
    inputs: Optional[dict[str, InputMapping]] = None
    presenters: Optional[dict[str, PresenterConfig]] = None
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
        config_path: Optional[Union[str, Sequence[str]]] = None,
    ):
        """
        Initialize the layout loader.

        Parameters
        ----------
        config_path : str or sequence[str], optional
            One or more TOML configuration files to load and merge
        """
        if config_path is None:
            config_paths = [self._get_default_config_path()]
        elif isinstance(config_path, str):
            config_paths = [config_path]
        else:
            config_paths = list(config_path)

        if not config_paths:
            raise ValueError("At least one configuration path must be provided")

        self.config_paths = config_paths
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
        data: dict[str, Any] = {}

        for index, path in enumerate(self.config_paths):
            if not os.path.exists(path):
                raise FileNotFoundError(f"Layout config not found: {path}")

            with open(path, "rb") as f:
                loaded = tomllib.load(f)

            if index == 0:
                data = loaded
            else:
                data = self._merge_dicts(data, loaded)

        self._layouts_config = LayoutsConfig(**data)
        return self._layouts_config

    @staticmethod
    def _merge_dicts(
        base_data: dict[str, Any], new_data: dict[str, Any]
    ) -> dict[str, Any]:
        """Merge a secondary configuration dictionary into the base data."""

        merged = base_data.copy()

        for key, value in new_data.items():
            if key in {"layouts", "inputs", "formatters", "presenters"}:
                existing = merged.get(key, {})
                if not isinstance(existing, dict) or not isinstance(value, dict):
                    merged[key] = value
                else:
                    combined = existing.copy()
                    combined.update(value)
                    merged[key] = combined
            else:
                merged[key] = value

        return merged

    @staticmethod
    def load_from_files(
        layouts_path: Union[str, Sequence[str]],
    ) -> LayoutsConfig:
        """
        Load configuration from multiple TOML files.

        Parameters
        ----------
        layouts_path : str or sequence[str]
            One or more TOML configuration files to load and merge

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
        ...     ["layouts.toml", "inputs.toml", "presenters.toml"]
        ... )
        >>> print(list(config.layouts.keys()))
        ['demo', 'advanced']
        """
        if isinstance(layouts_path, str):
            config_paths = [layouts_path]
        else:
            config_paths = list(layouts_path)

        loader = LayoutLoader(config_paths)
        return loader.load()

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

    def get_input_mappings(self) -> dict[str, InputMapping]:
        """
        Get all input mapping configurations.

        Returns
        -------
        dict[str, InputMapping]
            Dictionary of input mappings, or empty dict if none defined

        Examples
        --------
        >>> loader = LayoutLoader("layouts.toml")
        >>> mappings = loader.get_input_mappings()
        >>> print(mappings["temperature"].context_key)
        temp
        """
        if self._layouts_config is None:
            self.load()

        assert self._layouts_config is not None

        if self._layouts_config.inputs is None:
            return {}

        return self._layouts_config.inputs

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

    def get_presenter_config(self, presenter_name: str) -> Optional[dict[str, Any]]:
        """
        Get presenter configuration by name.

        Parameters
        ----------
        presenter_name : str
            Name of the presenter configuration

        Returns
        -------
        dict[str, Any] or None
            Presenter configuration dictionary, or None if not found

        Examples
        --------
        >>> loader = LayoutLoader("layouts.toml")
        >>> presenter = loader.get_presenter_config("price")
        >>> print(presenter["input"])
        price
        """
        if self._layouts_config is None:
            self.load()

        assert self._layouts_config is not None

        if (
            self._layouts_config.presenters is None
            or presenter_name not in self._layouts_config.presenters
        ):
            return None

        presenter_config = self._layouts_config.presenters[presenter_name]
        return presenter_config.model_dump(exclude_none=True)


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
