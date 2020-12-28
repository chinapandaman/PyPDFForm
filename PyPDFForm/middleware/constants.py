# -*- coding: utf-8 -*-
"""Contains constants for middleware layer."""

from typing import Tuple, Union


class Text:
    """Contains constants for text parameters."""

    @property
    def global_font(self) -> str:
        """Used for setting global font for text."""

        return "Helvetica"

    @property
    def global_font_size(self) -> Union[float, int]:
        """Used for setting global font size for text."""

        return 12

    @property
    def global_font_color(
        self,
    ) -> Tuple[Union[float, int], Union[float, int], Union[float, int]]:
        """Used for setting global font color for text."""

        return 0, 0, 0

    @property
    def global_text_x_offset(self) -> Union[float, int]:
        """Used for setting global x offset for text."""

        return 0

    @property
    def global_text_y_offset(self) -> Union[float, int]:
        """Used for setting global y offset for text."""

        return 0

    @property
    def global_text_wrap_length(self) -> int:
        """Used for setting global wrap length for text."""

        return 100
