# -*- coding: utf-8 -*-
"""
Module containing shared helpers for middleware widgets.

This module provides common schema and validation logic used by middleware
classes. Choice widgets use these helpers to enforce integer-index bounds.
"""

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class PreparedValue:
    """
    Represents a widget value prepared for assignment.

    Preparation validates and normalizes the value without changing the widget.
    Dropdown updates can also include replacement choices, which are stored and
    queued for PDF updates only when the prepared value is applied.

    Attributes:
        value (Any): The value to store in the widget.
        choices (list | None): Replacement dropdown choices, or None when the
            choices should remain unchanged.
    """

    value: Any
    choices: list | None = None


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
