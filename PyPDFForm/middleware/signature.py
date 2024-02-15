# -*- coding: utf-8 -*-
"""Contains signature middleware."""

from os.path import expanduser

from .widget import Widget


class Signature(Widget):
    """A class to represent a signature field widget."""

    def __init__(
        self,
        name: str,
        value: str = None,
    ) -> None:
        """Constructs all attributes for the signature field."""

        super().__init__(name, value)

    @property
    def schema_definition(self) -> dict:
        """Json schema definition of the signature field."""

        return {"type": "string"}

    @property
    def sample_value(self) -> str:
        """Sample value of the signature field."""

        return expanduser("~/Downloads/sample_image.jpg")
