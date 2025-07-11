# -*- coding: utf-8 -*-
"""
Module representing a radio button widget.

This module defines the Radio class, which is a subclass of the
Checkbox class. It represents a radio button form field in a PDF
document, allowing users to select one option from a group of choices.
"""

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
        self.SET_ATTR_TRIGGER_HOOK_MAP.update(
            {
                "readonly": "flatten_radio",
            }
        )
        super().__init__(name, value)

        self.number_of_options: int = 0

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
            "maximum": self.number_of_options - 1,
            **super().schema_definition,
            "type": "integer",
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
