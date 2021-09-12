# -*- coding: utf-8 -*-
"""Contains helpers for image."""

from io import BytesIO
from typing import Union

from PIL import Image as Img
from PIL import UnidentifiedImageError


class Image:
    """Contains methods for interacting with images."""

    @staticmethod
    def is_image(stream: bytes) -> bool:
        """Checks if a stream is indeed an image."""

        buff = BytesIO()
        buff.write(stream)
        buff.seek(0)

        try:
            Img.open(buff)
            result = True
        except UnidentifiedImageError:
            result = False

        buff.close()
        return result

    @staticmethod
    def rotate_image(image_stream: bytes, rotation: Union[float, int]) -> bytes:
        """Rotates an image by a rotation angle."""

        buff = BytesIO()
        buff.write(image_stream)
        buff.seek(0)

        image = Img.open(buff)

        rotated_buff = BytesIO()
        image.rotate(rotation, expand=True).save(rotated_buff, format=image.format)
        rotated_buff.seek(0)

        result = rotated_buff.read()

        buff.close()
        rotated_buff.close()

        return result

    @staticmethod
    def any_image_to_jpg(image_stream: bytes) -> bytes:
        """Converts an image of any type to jpg."""

        buff = BytesIO()
        buff.write(image_stream)
        buff.seek(0)

        image = Img.open(buff)

        if image.format == "JPEG":
            buff.close()
            return image_stream

        rgb_image = image.convert("RGB")
        with BytesIO() as _file:
            rgb_image.save(_file, format="JPEG")
            _file.seek(0)
            result = _file.read()

        buff.close()
        return result
