# -*- coding: utf-8 -*-
"""
Contains the RawLine class, which represents a line that can be drawn
directly onto a PDF page at specified coordinates.
"""

from ..constants import DEFAULT_FONT_COLOR


class RawLine:
    """
    Represents a line object intended for direct drawing onto a specific page
    of a PDF document defined by starting and ending coordinates.

    This class encapsulates the necessary information (start point, end point,
    page number, and color) to render a straight line on a PDF page.
    """

    def __init__(
        self,
        page_number: int,
        src_x: float,
        src_y: float,
        dest_x: float,
        dest_y: float,
        color: tuple = DEFAULT_FONT_COLOR,
    ) -> None:
        """
        Initializes a raw line object for drawing.

        Args:
            page_number: The 1-based index of the page where the line should be drawn.
            src_x: The x-coordinate (horizontal position) of the starting point.
            src_y: The y-coordinate (vertical position) of the starting point.
            dest_x: The x-coordinate (horizontal position) of the ending point.
            dest_y: The y-coordinate (vertical position) of the ending point.
            color: The color of the line as an RGB tuple (0-1 for each channel).
        """
        super().__init__()

        self.page_number = page_number
        self.src_x = src_x
        self.src_y = src_y
        self.dest_x = dest_x
        self.dest_y = dest_y
        self.color = color

    @property
    def to_draw(self) -> dict:
        """
        Converts the raw line object into a dictionary format ready for drawing.

        Returns:
            A dictionary containing drawing parameters: page number, object type ("line"),
            start and end coordinates, and color.
        """
        return {
            "page_number": self.page_number,
            "type": "line",
            "src_x": self.src_x,
            "src_y": self.src_y,
            "dest_x": self.dest_x,
            "dest_y": self.dest_y,
            "color": self.color,
        }
