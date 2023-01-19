# -*- coding: utf-8 -*-
"""Contains checkbox middleware."""

from .element import ElementV2


class Checkbox(ElementV2):
    """A class to represent a checkbox element."""

    def __init__(
            self,
            element_name: str,
            element_value: bool = None,
            ) -> None:
        """Constructs all attributes for the checkbox."""

        super().__init__(element_name, element_value)

    @property
    def schema_definition(self) -> dict:
        """Json schema definition of the checkbox."""

        return {"type": "boolean"}
