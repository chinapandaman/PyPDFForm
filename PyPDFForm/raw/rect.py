# -*- coding: utf-8 -*-

from ..constants import DEFAULT_FONT_COLOR


class RawRectangle:

    def __init__(
        self,
        page_number: int,
        x: float,
        y: float,
        width: float,
        height: float,
        color: tuple = DEFAULT_FONT_COLOR,
    ) -> None:
        super().__init__()

        self.page_number = page_number
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color

    @property
    def to_draw(self) -> dict:
        return {
            "page_number": self.page_number,
            "type": "rect",
            "x": self.x,
            "y": self.y,
            "width": self.width,
            "height": self.height,
            "color": self.color,
        }
