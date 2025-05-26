# -*- coding: utf-8 -*-
"""
This module defines the DropdownWidget class, which is a subclass of the
TextWidget class. It represents a dropdown form field in a PDF document.
"""

from .text import TextWidget


class DropdownWidget(TextWidget):
    """
    Represents a dropdown widget in a PDF form.

    Inherits from the base TextWidget class and adds specific parameters for
    dropdown styling, such as options.

    Attributes:
        NONE_DEFAULTS (list): A list of parameters that default to None.
        ACRO_FORM_FUNC (str): The name of the AcroForm function to use for
            creating the dropdown.
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
        """
        Initializes a DropdownWidget object.

        Args:
            name (str): Name of the widget.
            page_number (int): Page number of the widget.
            x (float): X coordinate of the widget.
            y (float): Y coordinate of the widget.
            **kwargs: Additional keyword arguments.
        """
        self.USER_PARAMS = super().USER_PARAMS[:-1] + [
            ("options", "options"),
        ]
        super().__init__(name, page_number, x, y, **kwargs)
        self.acro_form_params["wkind"] = "choice"
        self.acro_form_params["value"] = self.acro_form_params["options"][0]
