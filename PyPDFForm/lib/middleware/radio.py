# -*- coding: utf-8 -*-
"""
Module representing a radio button widget.

This module defines the Radio class, which is a subclass of the
Checkbox class. It represents a radio button form field in a PDF
document, allowing users to select one option from a group of choices.
"""

from .checkbox import Checkbox
from .common import choice_index_schema, validate_choice_index


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

    @property
    def value(self) -> int:
        """
        Gets the current value of the radio button group.

        Returns:
            int: The index of the selected option.
        """
        return super().value

    @value.setter
    def value(self, value: int) -> None:
        """
        Sets the value of the radio button group.

        Integer indices are checked against the current option count before
        being stored, preserving the previous value when validation fails.

        Args:
            value (int): The index of the option to select.

        Raises:
            ValueError: If an integer index is outside the current options.
        """
        validate_choice_index(value, self.number_of_options)
        self._value = value

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
            **choice_index_schema(self.number_of_options),
        }

    @property
    def sample_value(self) -> int:
        """
        Returns a sample value for the radio button.

        The sample value is used to generate example data for the
        radio button field. It returns the index of the last option
        in the group.

        Returns:
            int: A sample value for the radio button.
        """
        return self.number_of_options - 1
