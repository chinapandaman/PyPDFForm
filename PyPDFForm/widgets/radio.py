# -*- coding: utf-8 -*-
"""
This module defines the `RadioGroup` and `RadioWidget` classes, which are used
to represent and manipulate radio button groups within PDF documents.

The `RadioGroup` class is a dataclass that encapsulates the properties of a
radio button group, such as its coordinates and shape.

The `RadioWidget` class extends the base `CheckBoxWidget` class to provide
specific functionality for interacting with radio button form fields in PDFs.
"""

from dataclasses import dataclass
from typing import List, Optional, Type

from reportlab.pdfgen.canvas import Canvas

from .base import Widget
from .checkbox import CheckBoxField, CheckBoxWidget


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


@dataclass
class RadioGroup(CheckBoxField):
    """
    Represents a group of radio buttons in a PDF document.

    This dataclass extends the `CheckBoxField` base class and defines the specific
    attributes that can be configured for a radio button group. Unlike a single
    checkbox, a radio group allows for multiple positions (x, y coordinates)
    where individual radio buttons can be placed, but only one can be selected.

    Attributes:
        _field_type (str): The type of the field, fixed as "radio".
        _widget_class (Type[Widget]): The widget class associated with this field type.
        x (List[float]): A list of x-coordinates for each radio button in the group.
        y (List[float]): A list of y-coordinates for each radio button in the group.
        shape (Optional[str]): The shape of the radio button. Valid values are
            "circle" or "square". Defaults to None, which typically means a default circle shape.
    """

    _field_type: str = "radio"
    _widget_class: Type[Widget] = RadioWidget

    x: List[float]
    y: List[float]
    shape: Optional[str] = None
