# -*- coding: utf-8 -*-

from typing import Tuple

from ..constants import DEFAULT_FONT_COLOR


class RawLine:
    def __init__(
        self,
        page_number: int,
        src_x: float,
        src_y: float,
        dest_x: float,
        dest_y: float,
        color: Tuple[float, float, float] = DEFAULT_FONT_COLOR,
    ) -> None:
        super().__init__()

        self.page_number = page_number
        self.src_x = src_x
        self.src_y = src_y
        self.dest_x = dest_x
        self.dest_y = dest_y
        self.color = color

    @property
    def to_draw(self) -> dict:
        return {
            "page_number": self.page_number,
            "type": "line",
            "src_x": self.src_x,
            "src_y": self.src_y,
            "dest_x": self.dest_x,
            "dest_y": self.dest_y,
            "color": self.color,
        }
