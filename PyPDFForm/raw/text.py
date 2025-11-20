# -*- coding: utf-8 -*-
"""
Contains the RawText class, which represents a text annotation
that can be drawn directly onto a PDF page without relying on existing form fields.
"""

from ..constants import DEFAULT_FONT, DEFAULT_FONT_COLOR, DEFAULT_FONT_SIZE
from ..middleware.text import Text


class RawText:
    """
    Represents a text object intended for direct drawing onto a specific page
    of a PDF document at specified coordinates.

    This class encapsulates all necessary information (text content, position,
    font, size, and color) to render text on a PDF page outside of traditional
    form fields.
    """

    def __init__(
        self,
        text: str,
        page_number: int,
        x: float,
        y: float,
        font: str = DEFAULT_FONT,
        font_size: float = DEFAULT_FONT_SIZE,
        font_color: tuple = DEFAULT_FONT_COLOR,
    ) -> None:
        """
        Initializes a raw text object for drawing.

        Args:
            text: The string content of the text to be drawn.
            page_number: The 1-based index of the page where the text should be drawn.
            x: The x-coordinate (horizontal position) of the text.
            y: The y-coordinate (vertical position) of the text.
            font: The name of the font to use for the text (defaults to DEFAULT_FONT).
            font_size: The size of the font (defaults to DEFAULT_FONT_SIZE).
            font_color: The color of the text as an RGB tuple (0-255 for each channel).
        """
        super().__init__()

        self.text = text
        self.page_number = page_number
        self.x = x
        self.y = y
        self.font = font
        self.font_size = font_size
        self.font_color = font_color

    @property
    def to_draw(self) -> dict:
        """
        Converts the raw text object to a dict ready for drawing.

        Returns:
            A dictionary containing the page number, object type, an initialized Text widget,
            and the coordinates for drawing.
        """
        widget = Text("new", self.text)
        widget.font = self.font
        widget.font_size = self.font_size
        widget.font_color = self.font_color

        return {
            "page_number": self.page_number,
            "type": "text",
            "widget": widget,
            "x": self.x,
            "y": self.y,
        }
