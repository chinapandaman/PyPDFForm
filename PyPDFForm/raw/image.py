# -*- coding: utf-8 -*-

from typing import BinaryIO, Union

from ..adapter import fp_or_f_obj_or_stream_to_stream
from ..image import rotate_image


class RawImage:
    def __init__(
        self,
        image: Union[bytes, str, BinaryIO],
        page_number: int,
        x: float,
        y: float,
        width: float,
        height: float,
        rotation: float = 0,
    ) -> None:
        super().__init__()

        self.image = image
        self.page_number = page_number
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.rotation = rotation

    @property
    def to_draw(self) -> dict:
        image = fp_or_f_obj_or_stream_to_stream(self.image)
        if self.rotation:
            image = rotate_image(image, self.rotation)

        return {
            "page_number": self.page_number,
            "type": "image",
            "stream": image,
            "x": self.x,
            "y": self.y,
            "width": self.width,
            "height": self.height,
        }
