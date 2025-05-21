# -*- coding: utf-8 -*-
"""Provides middleware for PDF text field widgets.

This module contains the Text class which handles:
- Text field value management
- Font properties (family, size, color)
- Text wrapping and formatting
- Comb field (fixed character spacing) support
- Preview mode for form field visualization
"""

from typing import Any

from .base import Widget


class Text(Widget):
    """Middleware for PDF text field widgets.

    Handles all aspects of text field processing including:
    - Value conversion and validation
    - Font styling and formatting
    - Multiline text wrapping
    - Comb field character spacing
    - Preview mode rendering

    Inherits from Widget base class and extends it with text-specific features.
    """

    SET_ATTR_TRIGGER_HOOK_MAP = {
        "font": "update_text_field_font",
        "font_size": "update_text_field_font_size",
        "font_color": "update_text_field_font_color",
    }

    def __init__(
        self,
        name: str,
        value: str = None,
    ) -> None:
        """Initializes a new text field widget.

        Args:
            name: Field name/key for the text field
            value: Initial text value (default: None)
        """

        super().__init__(name, value)

        self.font = None
        self.font_size = None
        self.font_color = None
        self.text_wrap_length = None
        self.max_length = None
        self.comb = None
        self.character_paddings = []
        self.text_lines = None
        self.text_line_x_coordinates = None
        self.preview = False
        self.available_fonts = {}

    @property
    def value(self) -> Any:
        """Gets the text field's current value with type conversion.

        Converts numeric values to strings automatically.

        Returns:
            Any: The text value as a string (converted if numeric)
        """

        if isinstance(self._value, (int, float)):
            return str(self._value)

        return self._value

    @value.setter
    def value(self, value: str) -> None:
        """Sets the text field's value.

        Args:
            value: New text value (will be converted to string if numeric)
        """

        self._value = value

    @property
    def schema_definition(self) -> dict:
        """Generates a JSON schema definition for the text field.

        Includes:
        - Type constraint (string)
        - Max length if specified
        - Any inherited schema properties

        Returns:
            dict: Complete JSON schema definition
        """

        result = {"type": "string"}

        if self.max_length is not None:
            result["maxLength"] = self.max_length

        return {**result, **super().schema_definition}

    @property
    def sample_value(self) -> str:
        """Generates a sample value demonstrating the text field's capacity.

        Uses the field name as the sample value, truncated to max_length if specified.

        Returns:
            str: Sample text value for demonstration purposes
        """

        return (
            self.name[: self.max_length] if self.max_length is not None else self.name
        )
