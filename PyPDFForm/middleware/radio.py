# -*- coding: utf-8 -*-
"""Contains radio middleware."""

from .element import ElementV2


class Radio(ElementV2):
    """A class to represent a radiobutton element."""

    def __init__(
            self,
            element_name: str,
            element_value: int = None,
            ) -> None:
        """Constructs all attributes for the radiobutton."""

        super().__init__(element_name, element_value)

        self.number_of_options = 0

    @property
    def schema_definition(self) -> dict:
        """Json schema definition of the radiobutton."""

        return {
                "type": "integer",
                "maximum": self.number_of_options - 1
                }
