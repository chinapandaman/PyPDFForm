# -*- coding: utf-8 -*-

from ..constants import DEFAULT_FONT, DEFAULT_FONT_COLOR, DEFAULT_FONT_SIZE
from ..middleware.text import Text


class RawText:
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
