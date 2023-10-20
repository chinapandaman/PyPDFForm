# -*- coding: utf-8 -*-
"""Contains dropdown middleware."""

from .element import Element


class Dropdown(Element):
    """A class to represent a dropdown element."""

    def __init__(
        self,
        element_name: str,
        element_value: int = None,
    ) -> None:
        """Constructs all attributes for the dropdown."""

        super().__init__(element_name, element_value)

        self.choices = None

    @property
    def schema_definition(self) -> dict:
        """Json schema definition of the dropdown."""

        return {"type": "integer", "maximum": len(self.choices) - 1}

    @property
    def sample_value(self) -> int:
        """Sample value of the dropdown."""

        return 0
