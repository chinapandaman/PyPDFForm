# -*- coding: utf-8 -*-
"""Contains dropdown middleware."""

from .base import Widget


class Dropdown(Widget):
    """A class to represent a dropdown widget."""

    def __init__(
        self,
        name: str,
        value: int = None,
    ) -> None:
        """Constructs all attributes for the dropdown."""

        super().__init__(name, value)

        self.choices = []
        self.desc = None

    @property
    def schema_definition(self) -> dict:
        """Json schema definition of the dropdown."""

        return {
            "type": "integer",
            "maximum": len(self.choices) - 1,
            **super().schema_definition,
        }

    @property
    def sample_value(self) -> int:
        """Sample value of the dropdown."""

        return len(self.choices) - 1
