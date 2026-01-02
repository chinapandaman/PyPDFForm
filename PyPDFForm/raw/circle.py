# -*- coding: utf-8 -*-
"""
Contains the RawCircle class, which represents a circle that can be drawn
directly onto a PDF page at specified coordinates and radius.
"""

from ..constants import DEFAULT_FONT_COLOR


class RawCircle:
    """
    Represents a circle object intended for direct drawing onto a specific page
    of a PDF document at specified coordinates and radius.

    This class encapsulates the necessary information (center position, radius,
    color, and fill color) to render a circle on a PDF page.
    """

    def __init__(
        self,
        page_number: int,
        center_x: float,
        center_y: float,
        radius: float,
        color: tuple = DEFAULT_FONT_COLOR,
        fill_color: tuple = None,
    ) -> None:
        """
        Initializes a raw circle object for drawing.

        Args:
            page_number: The 1-based index of the page where the circle should be drawn.
            center_x: The x-coordinate (horizontal position) of the center of the circle.
            center_y: The y-coordinate (vertical position) of the center of the circle.
            radius: The radius of the circle.
            color: The color of the circle's outline as an RGB tuple (0-1 for each channel).
            fill_color: The fill color of the circle as an RGB tuple (0-1 for each channel).
        """
        super().__init__()

        self.page_number = page_number
        self.center_x = center_x
        self.center_y = center_y
        self.radius = radius
        self.color = color
        self.fill_color = fill_color

    @property
    def to_draw(self) -> dict:
        """
        Converts the raw circle object into a dictionary format ready for drawing.

        Returns:
            A dictionary containing drawing parameters: page number, object type ("circle"),
            center coordinates, radius, outline color, and fill color.
        """
        return {
            "page_number": self.page_number,
            "type": "circle",
            "center_x": self.center_x,
            "center_y": self.center_y,
            "radius": self.radius,
            "color": self.color,
            "fill_color": self.fill_color,
        }
