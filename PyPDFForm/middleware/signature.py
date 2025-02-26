# -*- coding: utf-8 -*-
"""Contains signature middleware."""

from os.path import expanduser
from typing import BinaryIO, Union

from ..adapter import fp_or_f_obj_or_stream_to_stream
from .base import Widget


class Signature(Widget):
    """A class to represent a signature field widget."""

    preserve_aspect_ratio = True

    def __init__(
        self,
        name: str,
        value: Union[bytes, str, BinaryIO] = None,
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

    @property
    def stream(self) -> Union[bytes, None]:
        """Converts the value of the signature field image to a stream."""

        return (
            fp_or_f_obj_or_stream_to_stream(self.value)
            if self.value is not None
            else None
        )
