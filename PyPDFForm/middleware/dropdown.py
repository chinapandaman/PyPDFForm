# -*- coding: utf-8 -*-
"""
Module representing a dropdown widget.

This module defines the Dropdown class, which is a subclass of the
Widget class. It represents a dropdown form field in a PDF document.
"""

from .base import Widget


class Dropdown(Widget):
    """
    Represents a dropdown widget.

    The Dropdown class provides a concrete implementation for
    dropdown form fields. It inherits from the Widget class and
    implements the schema_definition and sample_value properties.
    """

    def __init__(
        self,
        name: str,
        value: int = None,
    ) -> None:
        """
        Initializes a dropdown widget.

        Args:
            name (str): The name of the dropdown.
            value (int): The initial value of the dropdown. Defaults to None.

        Attributes:
            choices (List[str]): The list of choices for the dropdown.
        """
        super().__init__(name, value)

        self.choices = []

    @property
    def schema_definition(self) -> dict:
        """
        Returns the schema definition for the dropdown.

        The schema definition is a dictionary that describes the
        data type and other constraints for the dropdown value.

        Returns:
            dict: A dictionary representing the schema definition.
        """
        return {
            "type": "integer",
            "maximum": len(self.choices) - 1,
            **super().schema_definition,
        }

    @property
    def sample_value(self) -> int:
        """
        Returns a sample value for the dropdown.

        The sample value is used to generate example data for the
        dropdown field.

        Returns:
            int: A sample value for the dropdown.
        """
        return len(self.choices) - 1
