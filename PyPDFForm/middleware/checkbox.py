# -*- coding: utf-8 -*-
"""Contains checkbox middleware."""

from typing import Union

from .base import Widget


class Checkbox(Widget):
    """A class to represent a checkbox widget."""

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
        """Constructs all attributes for the checkbox."""

        super().__init__(name, value)

        self.size = None
        self._button_style = self.BUTTON_STYLE_MAPPING["check"]

    @property
    def schema_definition(self) -> dict:
        """Json schema definition of the checkbox."""

        return {"type": "boolean", **super().schema_definition}

    @property
    def sample_value(self) -> Union[bool, int]:
        """Sample value of the checkbox."""

        return True

    @property
    def button_style(self) -> Union[str, None]:
        """Shape of the tick for the checkbox."""

        return self._button_style

    @button_style.setter
    def button_style(self, value) -> None:
        """Converts user specified button styles to acroform values."""

        if value in self.BUTTON_STYLE_MAPPING:
            self._button_style = self.BUTTON_STYLE_MAPPING[value]
        elif value in self.BUTTON_STYLE_MAPPING.values():
            self._button_style = value
