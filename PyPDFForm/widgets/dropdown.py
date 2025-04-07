# -*- coding: utf-8 -*-
"""Provides dropdown widget creation functionality for PDF forms.

This module contains the DropdownWidget class which handles creation of:
- Interactive dropdown/combobox fields
- Option list management
- Visual styling inheritance from text fields
- Form field integration
"""

from .text import TextWidget


class DropdownWidget(TextWidget):
    """Creates and configures PDF dropdown widgets.

    Extends TextWidget to support dropdown/combobox functionality including:
    - Option list management
    - Initial value selection
    - All inherited text field styling options

    Class Attributes:
        NONE_DEFAULTS: Empty list - dropdowns require options
        ACRO_FORM_FUNC: Uses underlying text field creation function
    """

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
        """Initializes a new dropdown widget with options.

        Args:
            name: Field name/key for the dropdown
            page_number: Page number to place widget on (1-based)
            x: X coordinate for widget position
            y: Y coordinate for widget position
            **kwargs: Additional widget parameters including:
                width/height: Field dimensions
                font/font_size: Text styling
                options: List of dropdown choices
        """

        self.USER_PARAMS = super().USER_PARAMS[:-1] + [
            ("options", "options"),
        ]
        super().__init__(name, page_number, x, y, **kwargs)
        self.acro_form_params["wkind"] = "choice"
        self.acro_form_params["value"] = self.acro_form_params["options"][0]
