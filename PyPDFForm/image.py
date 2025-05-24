# -*- coding: utf-8 -*-

from io import BytesIO
from typing import Tuple, Union

from PIL import Image

from .constants import Rect


def rotate_image(image_stream: bytes, rotation: Union[float, int]) -> bytes:
    buff = BytesIO()
    buff.write(image_stream)
    buff.seek(0)

    image = Image.open(buff)

    rotated_buff = BytesIO()
    image.rotate(rotation, expand=True).save(rotated_buff, format=image.format)
    rotated_buff.seek(0)

    result = rotated_buff.read()

    buff.close()
    rotated_buff.close()

    return result


def get_image_dimensions(image_stream: bytes) -> Tuple[float, float]:
    buff = BytesIO()
    buff.write(image_stream)
    buff.seek(0)

    image = Image.open(buff)

    return image.size


def get_draw_image_resolutions(
    widget: dict,
    preserve_aspect_ratio: bool,
    image_width: float,
    image_height: float,
) -> Tuple[float, float, float, float]:
    x = float(widget[Rect][0])
    y = float(widget[Rect][1])
    width = abs(float(widget[Rect][0]) - float(widget[Rect][2]))
    height = abs(float(widget[Rect][1]) - float(widget[Rect][3]))

    if preserve_aspect_ratio:
        ratio = max(image_width / width, image_height / height)

        new_width = image_width / ratio
        new_height = image_height / ratio

        x += abs(new_width - width) / 2
        y += abs(new_height - height) / 2

        width = new_width
        height = new_height

    return x, y, width, height
