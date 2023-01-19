# -*- coding: utf-8 -*-
"""Contains dropdown middleware."""

from .element import ElementV2


class Dropdown(ElementV2):
    """A class to represent a dropdown element."""

    def __init__(
            self,
            element_name: str,
            element_value: int = None,
            ) -> None:
        """Constructs all attributes for the dropdown."""

        super().__init__(element_name, element_value)

        self.font = None
        self.font_size = None
        self.font_color = None
        self.text_x_offset = None
        self.text_y_offset = None
        self.text_wrap_length = None

        self.choices = None

    @property
    def schema_definition(self) -> dict:
        """Json schema definition of the dropdown."""

        return {
                "type": "integer",
                "maximum": len(self.choices) - 1
                }
