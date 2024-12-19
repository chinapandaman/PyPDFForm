# -*- coding: utf-8 -*-
"""Contains text middleware."""

from typing import Any

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
        self.character_paddings = []
        self.text_lines = None
        self.text_line_x_coordinates = None
        self.preview = False

    @property
    def value(self) -> Any:
        """Value to fill for the text field."""

        if isinstance(self._value, (int, float)):
            return str(self._value)

        return self._value

    @value.setter
    def value(self, value: str) -> None:
        """Sets value to fill for the text field."""

        self._value = value

    @property
    def schema_definition(self) -> dict:
        """Json schema definition of the text field."""

        result = {"type": "string"}

        if self.max_length is not None:
            result["maxLength"] = self.max_length

        return {**result, **super().schema_definition}

    @property
    def sample_value(self) -> str:
        """Sample value of the text field."""

        return (
            self.name[: self.max_length] if self.max_length is not None else self.name
        )
