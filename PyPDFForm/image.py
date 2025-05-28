# -*- coding: utf-8 -*-
"""
This module provides functionalities for handling images within PyPDFForm.

It includes functions for rotating images, retrieving image dimensions, and
calculating the resolutions for drawing an image on a PDF page, taking into
account whether to preserve the aspect ratio.
"""

from io import BytesIO
from typing import Tuple, Union

from PIL import Image

from .constants import Rect


def rotate_image(image_stream: bytes, rotation: Union[float, int]) -> bytes:
    """
    Rotates an image by a specified angle in degrees.

    This function takes an image stream as bytes and rotates it using the PIL library.
    The rotation is performed around the center of the image, and the expand=True
    parameter ensures that the entire rotated image is visible, even if it extends
    beyond the original image boundaries.

    Args:
        image_stream (bytes): The image data as bytes.
        rotation (Union[float, int]): The rotation angle in degrees. Positive values
            rotate the image counterclockwise, while negative values rotate it clockwise.

    Returns:
        bytes: The rotated image data as bytes.
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
    """
    Retrieves the width and height of an image from its byte stream.

    This function uses the PIL library to open the image from the provided byte stream
    and returns its dimensions (width and height) as a tuple of floats.

    Args:
        image_stream (bytes): The image data as bytes.

    Returns:
        Tuple[float, float]: The width and height of the image in pixels.
    """
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
    """
    Calculates the position and dimensions for drawing an image on a PDF page.

    This function determines the x, y coordinates, width, and height for drawing an
    image within a specified widget area on a PDF page. It takes into account whether
    the aspect ratio of the image should be preserved and adjusts the dimensions
    accordingly.

    Args:
        widget (dict): A dictionary containing the widget's rectangle coordinates
            (x1, y1, x2, y2) under the key "Rect".
        preserve_aspect_ratio (bool): Whether to preserve the aspect ratio of the image.
            If True, the image will be scaled to fit within the widget area while
            maintaining its original aspect ratio.
        image_width (float): The width of the image in pixels.
        image_height (float): The height of the image in pixels.

    Returns:
        Tuple[float, float, float, float]: A tuple containing the x, y coordinates,
            width, and height of the image to be drawn on the PDF page.
    """
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
