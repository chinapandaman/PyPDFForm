# -*- coding: utf-8 -*-
"""
This module defines the RadioWidget class, which is a subclass of the
CheckBoxWidget class. It represents a radio button form field in a PDF
document.
"""
# TODO: In `canvas_operations`, `self.acro_form_params.copy()` creates a shallow copy of the dictionary in each iteration of the loop. For a large number of radio buttons, this repeated copying can be inefficient. Consider modifying the dictionary in place and then reverting changes if necessary, or restructuring the data to avoid repeated copying.

from dataclasses import dataclass
from typing import List, Optional

from reportlab.pdfgen.canvas import Canvas

from .checkbox import CheckBoxField, CheckBoxWidget


@dataclass
class RadioGroup(CheckBoxField):
    _field_type: str = "radio"

    x: List[float]
    y: List[float]
    shape: Optional[str] = None


class RadioWidget(CheckBoxWidget):
    """
    Represents a radio button widget in a PDF form.

    This class inherits from the CheckBoxWidget and is designed for handling
    radio button fields in PDF forms. Radio buttons allow the user to select
    only one option from a predefined set of choices.

    Attributes:
        ACRO_FORM_FUNC (str): The name of the AcroForm function to use for
            creating the radio button, set to "radio".
    """

    ACRO_FORM_FUNC = "radio"

    def __init__(
        self,
        name: str,
        page_number: int,
        x: List[float],
        y: List[float],
        **kwargs,
    ) -> None:
        """
        Initializes a RadioWidget object.

        Args:
            name (str): Name of the widget.
            page_number (int): Page number of the widget.
            x (List[float]): List of X coordinates for each radio button.
            y (List[float]): List of Y coordinates for each radio button.
            **kwargs: Additional keyword arguments.
        """
        self.USER_PARAMS.append(("shape", "shape"))
        super().__init__(name, page_number, x, y, **kwargs)

    def canvas_operations(self, canvas: Canvas) -> None:
        """
        Performs canvas operations for the radio button widget.

        This method iterates through the X and Y coordinates of each radio button
        and draws it on the PDF canvas. It also sets the value of the radio button
        based on its index in the list of coordinates.

        Args:
            canvas (Canvas): Canvas object to operate on.
        """
        for i, x in enumerate(self.acro_form_params["x"]):
            y = self.acro_form_params["y"][i]
            new_acro_form_params = self.acro_form_params.copy()
            new_acro_form_params["x"] = x
            new_acro_form_params["y"] = y
            new_acro_form_params["value"] = str(i)
            getattr(canvas.acroForm, self.ACRO_FORM_FUNC)(**new_acro_form_params)
