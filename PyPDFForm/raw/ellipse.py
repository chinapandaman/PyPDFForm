# -*- coding: utf-8 -*-
"""
Contains the RawEllipse class, which represents an ellipse that can be drawn
directly onto a PDF page defined by its bounding box.
"""

from ..constants import DEFAULT_FONT_COLOR


class RawEllipse:
    """
    Represents an ellipse object intended for direct drawing onto a specific page
    of a PDF document defined by its bounding box coordinates.

    This class encapsulates the necessary information (bounding box corners,
    page number, color, and fill color) to render an ellipse on a PDF page.
    """

    def __init__(
        self,
        page_number: int,
        x1: float,
        y1: float,
        x2: float,
        y2: float,
        color: tuple = DEFAULT_FONT_COLOR,
        fill_color: tuple = None,
    ) -> None:
        """
        Initializes a raw ellipse object for drawing.

        Args:
            page_number: The 1-based index of the page where the ellipse should be drawn.
            x1: The x-coordinate of the first corner of the bounding box.
            y1: The y-coordinate of the first corner of the bounding box.
            x2: The x-coordinate of the second corner of the bounding box.
            y2: The y-coordinate of the second corner of the bounding box.
            color: The color of the ellipse's outline as an RGB tuple (0-1 for each channel).
            fill_color: The fill color of the ellipse as an RGB tuple (0-1 for each channel).
        """
        super().__init__()

        self.page_number = page_number
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.color = color
        self.fill_color = fill_color

    @property
    def to_draw(self) -> dict:
        """
        Converts the raw ellipse object into a dictionary format ready for drawing.

        Returns:
            A dictionary containing drawing parameters: page number, object type ("ellipse"),
            bounding box coordinates, outline color, and fill color.
        """
        return {
            "page_number": self.page_number,
            "type": "ellipse",
            "x1": self.x1,
            "y1": self.y1,
            "x2": self.x2,
            "y2": self.y2,
            "color": self.color,
            "fill_color": self.fill_color,
        }
