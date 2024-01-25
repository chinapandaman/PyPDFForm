# -*- coding: utf-8 -*-
"""Contains radio middleware."""

from .widget import Widget


class Radio(Widget):
    """A class to represent a radiobutton widget."""

    def __init__(
        self,
        name: str,
        value: int = None,
    ) -> None:
        """Constructs all attributes for the radiobutton."""

        super().__init__(name, value)

        self.button_style = None
        self.number_of_options = 0

    @property
    def schema_definition(self) -> dict:
        """Json schema definition of the radiobutton."""

        return {"type": "integer", "maximum": self.number_of_options - 1}

    @property
    def sample_value(self) -> int:
        """Sample value of the radiobutton."""

        return 0
