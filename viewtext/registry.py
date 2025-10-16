"""
Field registry for managing data extraction from context objects.

This module provides the BaseFieldRegistry class for registering and
retrieving field getter functions that extract values from context
dictionaries.
"""

from typing import Callable


class BaseFieldRegistry:
    """
    Registry for field getter functions.

    The field registry maps field names to callable getter functions that
    extract values from context dictionaries. This allows for flexible
    data extraction and transformation before formatting.

    Attributes
    ----------
    _fields : dict[str, Callable]
        Internal dictionary mapping field names to getter functions

    Examples
    --------
    >>> registry = BaseFieldRegistry()
    >>> registry.register("temp", lambda ctx: ctx["temperature"])
    >>> getter = registry.get("temp")
    >>> getter({"temperature": 25})
    25
    """

    def __init__(self) -> None:
        """Initialize an empty field registry."""
        self._fields: dict[str, Callable] = {}

    def register(self, name: str, getter: Callable) -> None:
        """
        Register a field getter function.

        Parameters
        ----------
        name : str
            The field name to register
        getter : Callable
            A callable that takes a context dictionary and returns a value

        Examples
        --------
        >>> registry = BaseFieldRegistry()
        >>> registry.register("temp", lambda ctx: ctx.get("temperature", 0))
        """
        self._fields[name] = getter

    def get(self, name: str) -> Callable:
        """
        Retrieve a registered field getter function.

        Parameters
        ----------
        name : str
            The field name to retrieve

        Returns
        -------
        Callable
            The getter function associated with the field name

        Raises
        ------
        ValueError
            If the field name is not registered

        Examples
        --------
        >>> registry = BaseFieldRegistry()
        >>> registry.register("temp", lambda ctx: ctx["temperature"])
        >>> getter = registry.get("temp")
        >>> getter({"temperature": 25})
        25
        """
        if name not in self._fields:
            raise ValueError(f"Unknown field: {name}")
        return self._fields[name]

    def has_field(self, name: str) -> bool:
        """
        Check if a field is registered.

        Parameters
        ----------
        name : str
            The field name to check

        Returns
        -------
        bool
            True if the field is registered, False otherwise

        Examples
        --------
        >>> registry = BaseFieldRegistry()
        >>> registry.register("temp", lambda ctx: ctx["temperature"])
        >>> registry.has_field("temp")
        True
        >>> registry.has_field("humidity")
        False
        """
        return name in self._fields
