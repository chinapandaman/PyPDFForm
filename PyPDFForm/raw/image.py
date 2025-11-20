# -*- coding: utf-8 -*-
"""
Contains the RawImage class, which represents an image that can be drawn
directly onto a PDF page at a specified position and size.
"""

from typing import BinaryIO, Union

from ..adapter import fp_or_f_obj_or_stream_to_stream
from ..image import rotate_image


class RawImage:
    """
    Represents an image object intended for direct drawing onto a specific page
    of a PDF document at specified coordinates, size, and rotation.

    This class handles converting various input types for the image (file path, bytes,
    or stream) into a standardized stream format, applying rotation if necessary.
    """

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
        """
        Initializes a raw image object for drawing.

        Args:
            image: The image source, which can be a path (str), raw bytes (bytes),
                   or a file stream (BinaryIO).
            page_number: The 1-based index of the page where the image should be drawn.
            x: The x-coordinate (horizontal position) of the bottom-left corner of the image.
            y: The y-coordinate (vertical position) of the bottom-left corner of the image.
            width: The desired width of the image when drawn on the PDF.
            height: The desired height of the image when drawn on the PDF.
            rotation: The rotation angle in degrees (defaults to 0, no rotation).
        """
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
        """
        Converts the raw image object into a dictionary format ready for drawing.

        The image is converted to a stream and rotated if necessary before being included in the dictionary.

        Returns:
            A dictionary containing drawing parameters: page number, object type ("image"),
            the image stream (BinaryIO), coordinates (x, y), and dimensions (width, height).
        """
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
