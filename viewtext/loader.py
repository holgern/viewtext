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
    context_key : str
        Key to look up in the context dictionary
    default : Any, optional
        Default value if the field is not found
    transform : str, optional
        Transform to apply (upper, lower, title, strip, int, float, str, bool)
    """

    context_key: str
    default: Optional[Any] = None
    transform: Optional[str] = None


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

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the layout loader.

        Parameters
        ----------
        config_path : str, optional
            Path to the TOML configuration file
        """
        if config_path is None:
            config_path = self._get_default_config_path()
        self.config_path = config_path
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

        self._layouts_config = LayoutsConfig(**data)
        return self._layouts_config

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
