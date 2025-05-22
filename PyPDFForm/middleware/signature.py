# -*- coding: utf-8 -*-

from os.path import expanduser
from typing import BinaryIO, Union

from ..adapter import fp_or_f_obj_or_stream_to_stream
from .base import Widget


class Signature(Widget):
    preserve_aspect_ratio = True

    def __init__(
        self,
        name: str,
        value: Union[bytes, str, BinaryIO] = None,
    ) -> None:
        super().__init__(name, value)

    @property
    def schema_definition(self) -> dict:
        return {"type": "string"}

    @property
    def sample_value(self) -> str:
        return expanduser("~/Downloads/sample_image.jpg")

    @property
    def stream(self) -> Union[bytes, None]:
        return (
            fp_or_f_obj_or_stream_to_stream(self.value)
            if self.value is not None
            else None
        )
