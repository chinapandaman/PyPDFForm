# -*- coding: utf-8 -*-
"""Contains dropdown widget to create."""

from .text import TextWidget


class DropdownWidget(TextWidget):
    """Dropdown widget to create."""

    NONE_DEFAULTS = []
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

        self.USER_PARAMS = super().USER_PARAMS[:-1] + [
            ("options", "options"),
        ]
        super().__init__(name, page_number, x, y, **kwargs)
        self.acro_form_params["wkind"] = "choice"
        self.acro_form_params["value"] = self.acro_form_params["options"][0]
