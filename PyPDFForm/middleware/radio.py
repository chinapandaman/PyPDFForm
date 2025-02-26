# -*- coding: utf-8 -*-
"""Contains radio middleware."""

from .checkbox import Checkbox


class Radio(Checkbox):
    """A class to represent a radiobutton widget."""

    number_of_options = 0

    @property
    def schema_definition(self) -> dict:
        """Json schema definition of the radiobutton."""

        return {
            "maximum": self.number_of_options - 1,
            **super().schema_definition,
            "type": "integer",
        }

    @property
    def sample_value(self) -> int:
        """Sample value of the radiobutton."""

        return self.number_of_options - 1
