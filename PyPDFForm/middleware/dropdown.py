# -*- coding: utf-8 -*-
"""
Module representing a dropdown widget.

This module defines the Dropdown class, which is a subclass of the
Widget class. It represents a dropdown form field in a PDF document.
"""

from typing import Union

from .base import Widget


class Dropdown(Widget):
    """
    Represents a dropdown widget in a PDF form.

    Inherits from the Widget class and provides specific functionality
    for handling dropdown form fields.

    Key attributes:
        font (str): The font of the dropdown field.
        choices (List[str]): The list of available options in the dropdown.
        value (int): The index of the selected choice in the choices list.

    Methods:
        schema_definition: Returns a schema definition for the dropdown's value.
        sample_value: Returns a sample value for the dropdown.
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
            font (str): The font of the dropdown field.
            choices (List[str]): The list of choices for the dropdown.
        """
        self.SET_ATTR_TRIGGER_HOOK_MAP.update(
            {
                "font": "update_text_field_font",
                "font_size": "update_text_field_font_size",
                "font_color": "update_text_field_font_color",
                "choices": "update_dropdown_choices",
            }
        )
        super().__init__(name, value)

        self.font: str = None
        self.font_size: float = None
        self.font_color: tuple = None
        self.choices: Union[tuple, list] = None

    @property
    def value(self) -> int:
        """
        Gets the current value of the dropdown.

        Returns:
            int: The index of the selected choice.
        """
        return super().value

    @value.setter
    def value(self, value: Union[str, int]) -> None:
        """
        Sets the value of the dropdown.

        If the value is a string, it attempts to find the corresponding
        index in the choices list. If not found, the string value is
        added to the choices, and its new index is used.

        Args:
            value (Union[str, int]): The value to set. Can be a string
                                      (option text) or an integer (index).
        """
        if isinstance(value, str):
            index = self._get_option_index(value)
            if index is None:
                self.choices = list(self.choices) + [value]
                index = len(self.choices) - 1
            value = index

        self._value = value

    def _get_option_index(self, value: str) -> Union[int, None]:
        """
        Gets the index of a given option value in the dropdown's choices.

        Args:
            value (str): The option value to search for.

        Returns:
            Union[int, None]: The index of the option if found, otherwise None.
        """
        for i, each in enumerate(self.choices):
            if value == each:
                return i

        return None

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
