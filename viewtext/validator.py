"""
Field validation module for viewtext.

This module provides validation functionality for field values, including
type checking, constraint validation, and error handling strategies.
"""

import re
from re import Pattern
from typing import Any, Optional


class ValidationError(Exception):
    """Exception raised when field validation fails."""

    pass


class FieldValidator:
    """
    Validator for field values based on FieldMapping configuration.

    This class handles type validation, constraint checking, and error
    handling for field values extracted from context data.

    Parameters
    ----------
    field_name : str
        Name of the field being validated
    field_type : str, optional
        Expected type (str, int, float, bool, dict, list, any)
    on_validation_error : str, optional
        Error handling strategy (use_default, raise, skip, coerce)
    default : Any, optional
        Default value to use when validation fails
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
    """

    def __init__(
        self,
        field_name: str,
        field_type: Optional[str] = None,
        on_validation_error: Optional[str] = None,
        default: Optional[Any] = None,
        min_value: Optional[float] = None,
        max_value: Optional[float] = None,
        min_length: Optional[int] = None,
        max_length: Optional[int] = None,
        pattern: Optional[str] = None,
        allowed_values: Optional[list[Any]] = None,
        min_items: Optional[int] = None,
        max_items: Optional[int] = None,
    ):
        self.field_name = field_name
        self.field_type = self._normalize_type(field_type) if field_type else None
        self.on_validation_error = on_validation_error or "use_default"
        self.default = default
        self.min_value = min_value
        self.max_value = max_value
        self.min_length = min_length
        self.max_length = max_length
        self.pattern = pattern
        self.allowed_values = allowed_values
        self.min_items = min_items
        self.max_items = max_items

        self._compiled_pattern: Optional[Pattern[str]]
        if self.pattern:
            self._compiled_pattern = re.compile(self.pattern)
        else:
            self._compiled_pattern = None

    @staticmethod
    def _normalize_type(type_str: str) -> str:
        """Normalize type string to canonical form."""
        type_map = {
            "string": "str",
            "integer": "int",
            "boolean": "bool",
            "object": "dict",
            "array": "list",
        }
        return type_map.get(type_str.lower(), type_str.lower())

    def validate(self, value: Any) -> Any:
        """
        Validate a field value.

        Parameters
        ----------
        value : Any
            Value to validate

        Returns
        -------
        Any
            Validated value, coerced value, default value, or None depending
            on validation result and error handling strategy

        Raises
        ------
        ValidationError
            If validation fails and on_validation_error is "raise"
        """
        if value is None:
            return self._handle_none_value()

        if not self.field_type or self.field_type == "any":
            return value

        try:
            validated_value = self._validate_type(value)
            self._validate_constraints(validated_value)
            return validated_value
        except ValidationError as e:
            return self._handle_validation_error(e, value)

    def _handle_none_value(self) -> Any:
        """Handle None values."""
        if self.on_validation_error == "raise" and self.default is None:
            raise ValidationError(
                f"Field '{self.field_name}' is None and no default provided"
            )
        return self.default

    def _validate_type(self, value: Any) -> Any:
        """
        Validate and optionally coerce the type of a value.

        Parameters
        ----------
        value : Any
            Value to validate

        Returns
        -------
        Any
            Original or coerced value

        Raises
        ------
        ValidationError
            If type validation fails
        """
        actual_type = type(value).__name__

        if self.field_type == "str":
            if not isinstance(value, str):
                if self.on_validation_error == "coerce":
                    return str(value)
                raise ValidationError(
                    f"Field '{self.field_name}' expected type 'str', "
                    f"got '{actual_type}'"
                )

        elif self.field_type == "int":
            if not isinstance(value, int) or isinstance(value, bool):
                if self.on_validation_error == "coerce":
                    try:
                        return int(value)
                    except (ValueError, TypeError) as e:
                        raise ValidationError(
                            f"Field '{self.field_name}' cannot be coerced to int: {e}"
                        ) from e
                raise ValidationError(
                    f"Field '{self.field_name}' expected type 'int', "
                    f"got '{actual_type}'"
                )

        elif self.field_type == "float":
            if not isinstance(value, (int, float)) or isinstance(value, bool):
                if self.on_validation_error == "coerce":
                    try:
                        return float(value)
                    except (ValueError, TypeError) as e:
                        raise ValidationError(
                            f"Field '{self.field_name}' cannot be coerced to float: {e}"
                        ) from e
                raise ValidationError(
                    f"Field '{self.field_name}' expected type 'float', "
                    f"got '{actual_type}'"
                )
            if isinstance(value, int) and not isinstance(value, bool):
                return float(value)

        elif self.field_type == "bool":
            if not isinstance(value, bool):
                if self.on_validation_error == "coerce":
                    return bool(value)
                raise ValidationError(
                    f"Field '{self.field_name}' expected type 'bool', "
                    f"got '{actual_type}'"
                )

        elif self.field_type == "dict":
            if not isinstance(value, dict):
                raise ValidationError(
                    f"Field '{self.field_name}' expected type 'dict', "
                    f"got '{actual_type}'"
                )

        elif self.field_type == "list":
            if not isinstance(value, list):
                raise ValidationError(
                    f"Field '{self.field_name}' expected type 'list', "
                    f"got '{actual_type}'"
                )

        return value

    def _validate_constraints(self, value: Any) -> None:
        """
        Validate constraints on a value.

        Parameters
        ----------
        value : Any
            Value to validate

        Raises
        ------
        ValidationError
            If constraint validation fails
        """
        if self.allowed_values is not None:
            if value not in self.allowed_values:
                raise ValidationError(
                    f"Field '{self.field_name}' value '{value}' not in allowed values: "
                    f"{self.allowed_values}"
                )

        if isinstance(value, (int, float)) and not isinstance(value, bool):
            if self.min_value is not None and value < self.min_value:
                raise ValidationError(
                    f"Field '{self.field_name}' value {value} is less than "
                    f"minimum {self.min_value}"
                )
            if self.max_value is not None and value > self.max_value:
                raise ValidationError(
                    f"Field '{self.field_name}' value {value} is greater than "
                    f"maximum {self.max_value}"
                )

        if isinstance(value, str):
            if self.min_length is not None and len(value) < self.min_length:
                raise ValidationError(
                    f"Field '{self.field_name}' length {len(value)} is less than "
                    f"minimum {self.min_length}"
                )
            if self.max_length is not None and len(value) > self.max_length:
                raise ValidationError(
                    f"Field '{self.field_name}' length {len(value)} is greater than "
                    f"maximum {self.max_length}"
                )
            if self._compiled_pattern and not self._compiled_pattern.match(value):
                raise ValidationError(
                    f"Field '{self.field_name}' value '{value}' does not match "
                    f"pattern '{self.pattern}'"
                )

        if isinstance(value, list):
            if self.min_items is not None and len(value) < self.min_items:
                raise ValidationError(
                    f"Field '{self.field_name}' has {len(value)} items, "
                    f"minimum is {self.min_items}"
                )
            if self.max_items is not None and len(value) > self.max_items:
                raise ValidationError(
                    f"Field '{self.field_name}' has {len(value)} items, "
                    f"maximum is {self.max_items}"
                )

    def _handle_validation_error(
        self, error: ValidationError, original_value: Any
    ) -> Any:
        """
        Handle validation error based on configured strategy.

        Parameters
        ----------
        error : ValidationError
            The validation error that occurred
        original_value : Any
            The original value that failed validation

        Returns
        -------
        Any
            Value to return based on error handling strategy

        Raises
        ------
        ValidationError
            If on_validation_error is "raise"
        """
        if self.on_validation_error == "raise":
            raise error
        elif self.on_validation_error == "skip":
            return None
        elif self.on_validation_error == "use_default":
            return self.default
        elif self.on_validation_error == "coerce":
            return self.default
        else:
            return self.default
