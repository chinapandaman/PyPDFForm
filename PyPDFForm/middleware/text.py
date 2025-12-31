# -*- coding: utf-8 -*-
"""
Module representing a text field widget.

This module defines the Text class, which is a subclass of the
Widget class. It represents a text field form field in a PDF document,
allowing users to enter text.
"""

from .base import Widget


class Text(Widget):
    """
    Represents a text field widget.

    The Text class provides a concrete implementation for text field
    form fields. It inherits from the Widget class and implements
    the value, schema_definition, and sample_value properties. It
    also defines a number of attributes that can be used to customize
    the appearance and behavior of the text field, such as font,
    font_size, font_color, comb, alignment, and multiline.
    """

    def __init__(
        self,
        name: str,
        value: str = None,
    ) -> None:
        """
        Initializes a text field widget.

        Args:
            name (str): The name of the text field.
            value (str): The initial value of the text field. Defaults to None.

        Attributes:
            font (str): The font of the text field. Defaults to None.
            font_size (int): The font size of the text field. Defaults to None.
            font_color (str): The font color of the text field. Defaults to None.
            comb (bool): Whether the text field is a comb field. Defaults to None.
            alignment (str): The alignment of the text field. Defaults to None.
            multiline (bool): Whether the text field is multiline. Defaults to None.
            max_length (int): The maximum length of the text field. Defaults to None.
        """
        self.SET_ATTR_TRIGGER_HOOK_MAP.update(
            {
                "font": "update_text_field_font",
                "font_size": "update_text_field_font_size",
                "font_color": "update_text_field_font_color",
                "comb": "update_text_field_comb",
                "alignment": "update_text_field_alignment",
                "multiline": "update_text_field_multiline",
                "max_length": "update_text_field_max_length",
            }
        )
        super().__init__(name, value)

        self.font: str = None
        self.font_size: float = None
        self.font_color: tuple = None
        self.comb: bool = None
        self.alignment: int = None
        self.multiline: bool = None
        self.max_length: int = None

    @property
    def value(self) -> str:
        """
        Returns the value of the text field.

        If the value is an integer or float, it is converted to a string.

        Returns:
            str: The value of the text field.
        """
        if isinstance(self._value, (int, float)):
            return str(self._value)

        return self._value

    @value.setter
    def value(self, value: str) -> None:
        """
        Sets the value of the text field.

        Args:
            value (str): The value to set.
        """
        self._value = value

    @property
    def schema_definition(self) -> dict:
        """
        Returns the schema definition for the text field.

        The schema definition is a dictionary that describes the
        data type and other constraints for the text field value.

        Returns:
            dict: A dictionary representing the schema definition.
        """
        result = {"type": "string"}

        if self.max_length is not None:
            result["maxLength"] = self.max_length

        return {**result, **super().schema_definition}

    @property
    def sample_value(self) -> str:
        """
        Returns a sample value for the text field.

        The sample value is used to generate example data for the
        text field. It returns the name of the field, truncated to
        the maximum length if specified.

        Returns:
            str: A sample value for the text field.
        """
        return (
            self.name[: self.max_length] if self.max_length is not None else self.name
        )
