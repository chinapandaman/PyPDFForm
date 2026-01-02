# -*- coding: utf-8 -*-

from ..constants import DEFAULT_FONT_COLOR


class RawEllipse:
    def __init__(
        self,
        page_number: int,
        x1: float,
        y1: float,
        x2: float,
        y2: tuple = DEFAULT_FONT_COLOR,
        color: tuple = DEFAULT_FONT_COLOR,
        fill_color: tuple = None,
    ) -> None:
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
