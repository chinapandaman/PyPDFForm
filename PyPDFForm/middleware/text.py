# -*- coding: utf-8 -*-
"""Contains text middleware."""

from .base import Widget


class Text(Widget):
    """A class to represent a text field widget."""

    def __init__(
        self,
        name: str,
        value: str = None,
    ) -> None:
        """Constructs all attributes for the text field."""

        super().__init__(name, value)

        self.font = None
        self.font_size = None
        self.font_color = None
        self.text_wrap_length = None
        self.max_length = None
        self.comb = None
        self.character_paddings = None
        self.text_lines = None
        self.text_line_x_coordinates = None
        self.preview = False

    @property
    def schema_definition(self) -> dict:
        """Json schema definition of the text field."""

        result = {"type": "string"}

        if self.max_length is not None:
            result["maxLength"] = self.max_length

        return result

    @property
    def sample_value(self) -> str:
        """Sample value of the text field."""

        return self.name
