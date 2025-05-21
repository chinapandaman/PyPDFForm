# -*- coding: utf-8 -*-
"""Provides middleware for PDF checkbox widgets.

This module contains the Checkbox class which handles:
- Checkbox state management (checked/unchecked)
- Button style customization
- Value validation and conversion
- Schema generation for form validation
"""

from typing import Union

from .base import Widget


class Checkbox(Widget):
    """Middleware for PDF checkbox widgets.

    Handles all aspects of checkbox processing including:
    - State management (checked/unchecked)
    - Button style customization (check, cross, circle)
    - Value validation
    - PDF form field integration

    Inherits from Widget base class and extends it with checkbox-specific features.
    """

    SET_ATTR_TRIGGER_HOOK_MAP = {
        "size": "update_check_radio_size",
        "button_style": "update_check_button_style",
    }

    BUTTON_STYLE_MAPPING = {
        "check": "4",
        "cross": "5",
        "circle": "l",
    }

    def __init__(
        self,
        name: str,
        value: bool = None,
    ) -> None:
        """Initializes a new checkbox widget.

        Args:
            name: Field name/key for the checkbox
            value: Initial checked state (default: None)
        """

        super().__init__(name, value)

        self.size = None
        self._button_style = self.BUTTON_STYLE_MAPPING["check"]

    @property
    def schema_definition(self) -> dict:
        """Generates a JSON schema definition for the checkbox.

        Returns:
            dict: Schema properties including:
                - type: boolean
                - description (if available from base class)
        """

        return {"type": "boolean", **super().schema_definition}

    @property
    def sample_value(self) -> Union[bool, int]:
        """Generates a sample value for the checkbox.

        Returns:
            Union[bool, int]: Always returns True as the sample checked state
        """

        return True

    @property
    def button_style(self) -> Union[str, None]:
        """Gets the current button style identifier.

        Returns:
            Union[str, None]: The button style code used in PDF form fields
        """

        return self._button_style

    @button_style.setter
    def button_style(self, value) -> None:
        """Sets the button style for the checkbox.

        Accepts either style names ('check', 'cross', 'circle') or
        direct PDF button style codes ('4', '5', 'l').

        Args:
            value: Button style name or code to set
        """

        if value in self.BUTTON_STYLE_MAPPING:
            self._button_style = self.BUTTON_STYLE_MAPPING[value]
        elif value in self.BUTTON_STYLE_MAPPING.values():
            self._button_style = value
