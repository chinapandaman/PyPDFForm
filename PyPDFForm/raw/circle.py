# -*- coding: utf-8 -*-

from ..constants import DEFAULT_FONT_COLOR


class RawCircle:
    def __init__(
        self,
        page_number: int,
        center_x: float,
        center_y: float,
        radius: float,
        color: tuple = DEFAULT_FONT_COLOR,
        fill_color: tuple = None,
    ) -> None:
        super().__init__()

        self.page_number = page_number
        self.center_x = center_x
        self.center_y = center_y
        self.radius = radius
        self.color = color
        self.fill_color = fill_color

    @property
    def to_draw(self) -> dict:
        return {
            "page_number": self.page_number,
            "type": "circle",
            "center_x": self.center_x,
            "center_y": self.center_y,
            "radius": self.radius,
            "color": self.color,
            "fill_color": self.fill_color,
        }
