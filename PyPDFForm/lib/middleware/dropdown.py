# -*- coding: utf-8 -*-
"""
Module representing a dropdown widget.

This module defines the Dropdown class, which is a subclass of the
Widget class. It represents a dropdown form field in a PDF document.
"""

from typing import Any, Optional

from .base import PreparedValue, Widget


class Dropdown(Widget):
    """
    Represents a dropdown widget in a PDF form.

    Inherits from the Widget class and provides specific functionality
    for handling dropdown form fields. The stored value is an option index; string
    assignments are normalized to an existing option index or appended as a new
    choice. Integer indices must identify an existing option.

    Key attributes:
        font (str): The font of the dropdown field.
        choices (List[str]): The list of available options in the dropdown.
        value (int): The index of the selected choice in the choices list.

    Methods:
        schema_definition: Returns a schema definition for the dropdown's value.
        sample_value: Returns a sample value for the dropdown.
    """

    TYPE_SPECIFIC_PROPERTIES = frozenset({"font", "font_size", "font_color", "choices"})

    def __init__(
        self,
        name: str,
        value: int = None,
    ) -> None:
        """
        Initializes a dropdown widget.

        Besides common widget state, dropdowns register hooks for font updates
        and choice replacement.

        Args:
            name (str): The name of the dropdown.
            value (int): The initial value of the dropdown. Defaults to None.

        Attributes:
            font (str): The font of the dropdown field.
            choices (List[str]): The list of choices for the dropdown.
        """
        super().__init__(name, value)
        self.SET_ATTR_TRIGGER_HOOK_MAP.update(
            {
                "font": "update_text_field_font",
                "choices": "update_dropdown_choices",
                "font_size": "update_text_field_font_size",
                "font_color": "update_text_field_font_color",
            }
        )

        self.font: Optional[str] = None
        self.font_size: Optional[float] = None
        self.font_color: Optional[tuple] = None
        self.choices: Optional[tuple | list] = None

    @property
    def value(self) -> int:
        """
        Gets the current value of the dropdown.

        Returns:
            int: The index of the selected choice.
        """
        return super().value

    @value.setter
    def value(self, value: str | int) -> None:
        """
        Sets the value of the dropdown.

        If the value is a string, it attempts to find the corresponding
        index in the choices list. If not found, the string value is
        added to the choices, and its new index is used. Integer values are checked
        against the current choices before being stored.

        Args:
            value (str | int): The value to set. Can be a string
                                      (option text) or an integer (index).

        Raises:
            ValueError: If an integer index is outside the current choices.
        """
        self.apply_value(self.prepare_value(value))

    def prepare_value(self, value: Any) -> PreparedValue:
        """
        Prepares a dropdown selection without changing its value or choices.

        Integer indices are checked against the current choices. Strings are
        normalized to an existing index or staged as a new last option. New
        choices do not trigger hooks until the prepared selection is applied.

        Args:
            value (Any): The proposed option text or index.

        Returns:
            PreparedValue: The selected index and any replacement choices.

        Raises:
            ValueError: If an integer index is outside the current choices.
        """
        self.validate_choice_index(value)
        if isinstance(value, str):
            index = self._get_option_index(value)
            if index is None:
                choices = list(self.choices) + [value]
                return PreparedValue(len(choices) - 1, choices)
            value = index

        return super().prepare_value(value)

    def apply_value(self, update: PreparedValue) -> None:
        """
        Applies a previously prepared dropdown selection.

        Replacement choices are stored through the existing attribute setter
        so their PDF update hook is queued before the selected index is stored.
        Validation and option lookup are not repeated during application.

        Args:
            update (PreparedValue): The prepared selection and optional choices.
        """
        if update.choices is not None:
            self.choices = update.choices
        super().apply_value(update)

    def choice_index_schema(self) -> dict:
        """
        Returns the schema definition for indices into the current choices.

        Valid indices range from zero to the number of choices minus one. An
        empty dropdown explicitly rejects every integer selection.

        Returns:
            dict: A dictionary representing the schema definition for indices.
        """
        number_of_options = len(self.choices or [])
        if not number_of_options:
            return {"type": "integer", "not": {}}
        return {"type": "integer", "minimum": 0, "maximum": number_of_options - 1}

    def validate_choice_index(self, value: object) -> None:
        """
        Validates an integer selection against the current dropdown choices.

        Non-integer values retain their existing handling, including strings
        normalized during preparation and None for an unset selection.

        Args:
            value (object): The proposed value of the dropdown.

        Raises:
            ValueError: If an integer index is outside the current choices.
        """
        number_of_options = len(self.choices or [])
        if isinstance(value, int) and not 0 <= value < number_of_options:
            msg = f"Choice index {value} must satisfy 0 <= index < {number_of_options}."
            raise ValueError(msg)

    def _get_option_index(self, value: str) -> int | None:
        """
        Gets the index of a given option value in the dropdown's choices.

        Args:
            value (str): The option value to search for.

        Returns:
            int | None: The index of the option if found, otherwise None.
        """
        for i, each in enumerate(self.choices):
            if value == each:
                return i

        return None

    @property
    def schema_definition(self) -> dict:
        """
        Returns the schema definition for the dropdown.

        The schema definition accepts either an integer option index bounded by
        the current choices or a string value that can be normalized by the value
        setter.

        Returns:
            dict: A dictionary representing the schema definition.
        """
        return {
            "anyOf": [
                {
                    **self.choice_index_schema(),
                    **super().schema_definition,
                },
                {"type": "string"},
            ]
        }

    @property
    def sample_value(self) -> int | None:
        """
        Returns a sample value for the dropdown.

        The sample value is used to generate example data for the
        dropdown field. It selects the last available option, or returns None
        when no choices are available so sample data can omit the field.

        Returns:
            int | None: The last option index, or None when there are no choices.
        """
        return len(self.choices) - 1 if self.choices else None
