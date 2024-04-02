# -*- coding: utf-8 -*-
"""Contains dropdown widget to create."""

from .base import Widget


class DropdownWidget(Widget):
    """Dropdown widget to create."""

    USER_PARAMS = [
        ("width", "width"),
        ("height", "height"),
        ("options", "options"),
        ("font", "fontName"),
        ("font_size", "fontSize"),
        ("font_color", "textColor"),
    ]
    COLOR_PARAMS = ["font_color"]
    ACRO_FORM_FUNC = "_textfield"

    def __init__(
        self,
        name: str,
        page_number: int,
        x: float,
        y: float,
        **kwargs,
    ) -> None:
        """Sets acro form parameters."""

        super().__init__(name, page_number, x, y, **kwargs)
        self.acro_form_params["wkind"] = "choice"
        self.acro_form_params["value"] = self.acro_form_params["options"][0]
