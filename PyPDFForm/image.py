# -*- coding: utf-8 -*-
"""Provides image processing utilities for PDF forms.

This module contains functions for:
- Rotating images while maintaining quality
- Extracting image dimensions
- Handling image streams and formats

Supports common image formats including JPEG, PNG, and others supported by PIL.
"""

from io import BytesIO
from typing import Tuple, Union

from PIL import Image


def rotate_image(image_stream: bytes, rotation: Union[float, int]) -> bytes:
    """Rotates an image while maintaining original quality and format.

    Args:
        image_stream: Input image as bytes
        rotation: Rotation angle in degrees (can be float for precise angles)

    Returns:
        bytes: Rotated image as bytes in the original format

    Note:
        Automatically expands the canvas to prevent cropping during rotation.
    """

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
    """Extracts width and height from an image stream.

    Args:
        image_stream: Input image as bytes

    Returns:
        Tuple[float, float]: (width, height) in pixels

    Note:
        Works with any image format supported by PIL (Pillow)
    """

    buff = BytesIO()
    buff.write(image_stream)
    buff.seek(0)

    image = Image.open(buff)

    return image.size
