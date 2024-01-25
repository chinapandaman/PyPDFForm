# -*- coding: utf-8 -*-
"""Contains checkbox middleware."""

from .widget import Widget


class Checkbox(Widget):
    """A class to represent a checkbox widget."""

    def __init__(
        self,
        name: str,
        value: bool = None,
    ) -> None:
        """Constructs all attributes for the checkbox."""

        super().__init__(name, value)

        self.button_style = None

    @property
    def schema_definition(self) -> dict:
        """Json schema definition of the checkbox."""

        return {"type": "boolean"}

    @property
    def sample_value(self) -> bool:
        """Sample value of the checkbox."""

        return True
