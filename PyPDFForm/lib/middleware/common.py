# -*- coding: utf-8 -*-
"""
Module containing shared helpers for middleware widgets.

This module provides common schema and validation logic used by middleware
classes. Choice widgets use these helpers to enforce integer-index bounds.
"""


def choice_index_schema(number_of_options: int) -> dict:
    """
    Returns the schema definition for a choice widget's integer indices.

    Valid indices range from zero to the number of options minus one. When no
    options are available, the schema explicitly rejects every integer index.

    Args:
        number_of_options (int): The number of available options.

    Returns:
        dict: A dictionary representing the schema definition for option indices.
    """
    if number_of_options <= 0:
        return {"type": "integer", "not": {}}
    return {"type": "integer", "minimum": 0, "maximum": number_of_options - 1}


def validate_choice_index(value: object, number_of_options: int) -> None:
    """
    Validates an integer choice index against the available options.

    Integer indices are checked before the caller stores the new widget value.
    Non-integer values are left unchanged so callers retain their existing
    handling of strings, None, and other value types.

    Args:
        value (object): The proposed value of the choice widget.
        number_of_options (int): The number of available options.

    Raises:
        ValueError: If an integer does not identify an existing option.
    """
    if isinstance(value, int) and not 0 <= value < number_of_options:
        msg = f"Choice index {value} must satisfy 0 <= index < {number_of_options}."
        raise ValueError(msg)
