# -*- coding: utf-8 -*-
"""
Module representing a radio button widget.

This module defines the Radio class, which is a subclass of the
Checkbox class. It represents a radio button form field in a PDF
document, allowing users to select one option from a group of choices.
"""

from typing import Any

from .base import PreparedValue
from .checkbox import Checkbox


class Radio(Checkbox):
    """
    Represents a radio button widget.

    The Radio class provides a concrete implementation for radio button
    form fields. It inherits from the Checkbox class and implements
    the schema_definition and sample_value properties.
    """

    def __init__(
        self,
        name: str,
        value: int = None,
    ) -> None:
        """
        Initializes a radio button widget.

        Args:
            name (str): The name of the radio button.
            value (int): The initial value of the radio button. Defaults to None.

        Attributes:
            number_of_options (int): The number of options for the radio button.
        """
        super().__init__(name, value)

        self.number_of_options: int = 0

    def prepare_value(self, value: Any) -> PreparedValue:
        """
        Prepares a radio selection without changing the current value.

        Integer indices are checked against the current option count. The
        inherited value setter and PDF filling use this same preparation step.

        Args:
            value (Any): The proposed index of the option to select.

        Returns:
            PreparedValue: The selection to apply after validation succeeds.

        Raises:
            ValueError: If an integer index is outside the current options.
        """
        self.validate_choice_index(value)
        return super().prepare_value(value)

    def choice_index_schema(self) -> dict:
        """
        Returns the schema definition for indices into the current radio group.

        Valid indices range from zero to the option count minus one. A group
        with no options explicitly rejects every integer selection.

        Returns:
            dict: A dictionary representing the schema definition for indices.
        """
        if self.number_of_options <= 0:
            return {"type": "integer", "not": {}}
        return {
            "type": "integer",
            "minimum": 0,
            "maximum": self.number_of_options - 1,
        }

    def validate_choice_index(self, value: object) -> None:
        """
        Validates an integer selection against the current radio option count.

        Non-integer values retain their existing handling, including None for
        an unset selection. Broader value-type validation is left to callers.

        Args:
            value (object): The proposed value of the radio button group.

        Raises:
            ValueError: If an integer index is outside the current options.
        """
        if isinstance(value, int) and not 0 <= value < self.number_of_options:
            msg = f"Choice index {value} must satisfy 0 <= index < {self.number_of_options}."
            raise ValueError(msg)

    @property
    def schema_definition(self) -> dict:
        """
        Returns the schema definition for the radio button.

        The schema definition is a dictionary that describes the
        data type and other constraints for the radio button value,
        which is expected to be an integer representing the index
        of the selected option.

        Returns:
            dict: A dictionary representing the schema definition.
        """
        return {
            **super().schema_definition,
            **self.choice_index_schema(),
        }

    @property
    def sample_value(self) -> int | None:
        """
        Returns a sample value for the radio button.

        The sample value is used to generate example data for the
        radio button field. It returns the index of the last option
        in the group, or None when no options are available so sample data can
        omit the field.

        Returns:
            int | None: The last option index, or None when there are no options.
        """
        return self.number_of_options - 1 if self.number_of_options > 0 else None
