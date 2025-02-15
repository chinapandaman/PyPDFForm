# -*- coding: utf-8 -*-
"""Contains image field middleware."""

from typing import BinaryIO, Union

from .signature import Signature


class Image(Signature):
    """A class to represent an image field widget."""

    def __init__(
        self,
        name: str,
        value: Union[bytes, str, BinaryIO] = None,
    ) -> None:
        """Constructs all attributes for the image field."""

        super().__init__(name, value)

        self.preserve_aspect_ratio = False
