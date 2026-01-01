# -*- coding: utf-8 -*-
"""
Contains the RawRectangle class, which represents a rectangle that can be drawn
directly onto a PDF page at specified coordinates and dimensions.
"""

from ..constants import DEFAULT_FONT_COLOR


class RawRectangle:
    """
    Represents a rectangle object intended for direct drawing onto a specific page
    of a PDF document at specified coordinates and size.

    This class encapsulates the necessary information (position, size, color,
    and fill color) to render a rectangle on a PDF page.
    """

    def __init__(
        self,
        page_number: int,
        x: float,
        y: float,
        width: float,
        height: float,
        color: tuple = DEFAULT_FONT_COLOR,
        fill_color: tuple = None,
    ) -> None:
        """
        Initializes a raw rectangle object for drawing.

        Args:
            page_number: The 1-based index of the page where the rectangle should be drawn.
            x: The x-coordinate (horizontal position) of the bottom-left corner of the rectangle.
            y: The y-coordinate (vertical position) of the bottom-left corner of the rectangle.
            width: The width of the rectangle.
            height: The height of the rectangle.
            color: The color of the rectangle's outline as an RGB tuple (0-1 for each channel).
            fill_color: The fill color of the rectangle as an RGB tuple (0-1 for each channel).
        """
        super().__init__()

        self.page_number = page_number
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
        self.fill_color = fill_color

    @property
    def to_draw(self) -> dict:
        """
        Converts the raw rectangle object into a dictionary format ready for drawing.

        Returns:
            A dictionary containing drawing parameters: page number, object type ("rect"),
            coordinates, dimensions, outline color, and fill color.
        """
        return {
            "page_number": self.page_number,
            "type": "rect",
            "x": self.x,
            "y": self.y,
            "width": self.width,
            "height": self.height,
            "color": self.color,
            "fill_color": self.fill_color,
        }
