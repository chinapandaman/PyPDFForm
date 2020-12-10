# -*- coding: utf-8 -*-

from io import BytesIO
from typing import Union
from PIL import Image as Img

from .exceptions.base import InvalidImageError


class Image(object):
    """Contains methods for interacting with images."""

    @staticmethod
    def rotate_image(image_stream: bytes, rotation: Union[float, int]) -> bytes:
        """Rotates an image by a rotation angle."""

        buff = BytesIO()
        buff.write(image_stream)
        buff.seek(0)

        try:
            image = Img.open(buff)
        except Exception:
            raise InvalidImageError

        rotated_buff = BytesIO()
        image.rotate(rotation, expand=True).save(rotated_buff, format=image.format)
        rotated_buff.seek(0)

        result = rotated_buff.read()

        buff.close()
        rotated_buff.close()

        return result
