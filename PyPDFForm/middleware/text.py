# -*- coding: utf-8 -*-
"""Contains text middleware."""

from .element import Element


class Text(Element):
    """A class to represent a text field element."""

    def __init__(
        self,
        element_name: str,
        element_value: str = None,
    ) -> None:
        """Constructs all attributes for the text field."""

        super().__init__(element_name, element_value)

        self.font = None
        self.font_size = None
        self.font_color = None
        self.text_x_offset = None
        self.text_y_offset = None
        self.text_wrap_length = None
        self.max_length = None
        self.comb = None
        self.character_paddings = None
        self.last_line_x_offset = None

    @property
    def schema_definition(self) -> dict:
        """Json schema definition of the text field."""

        result = {"type": "string"}

        if self.max_length is not None:
            result["maxLength"] = self.max_length

        return result
