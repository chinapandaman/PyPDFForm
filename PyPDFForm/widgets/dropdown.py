# -*- coding: utf-8 -*-
"""
This module defines the `DropdownField` and `DropdownWidget` classes, which are
used to represent and manipulate dropdown form fields within PDF documents.

The `DropdownField` class is a dataclass that encapsulates the properties of a
dropdown field, such as its options, dimensions, and styling.

The `DropdownWidget` class extends the base `TextWidget` class to provide
specific functionality for interacting with dropdown form fields in PDFs.
"""

from dataclasses import dataclass
from typing import List, Optional, Tuple, Type, Union

from .base import Field, Widget
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


@dataclass
class DropdownField(Field):
    """
    Represents a dropdown field in a PDF document.

    This dataclass extends the `Field` base class and defines the specific
    attributes that can be configured for a dropdown selection field.

    Attributes:
        _field_type (str): The type of the field, fixed as "dropdown".
        _widget_class (Type[Widget]): The widget class associated with this field type.
        options (Optional[List[Union[str, Tuple[str, str]]]]): A list of options
            available in the dropdown. Each option can be a string (display value)
            or a tuple of strings (display value, export value).
        width (Optional[float]): The width of the dropdown field.
        height (Optional[float]): The height of the dropdown field.
        font (Optional[str]): The font to use for the dropdown text.
        font_size (Optional[float]): The font size for the dropdown text.
        font_color (Optional[Tuple[float, ...]]): The color of the font as an RGB or RGBA tuple.
        bg_color (Optional[Tuple[float, ...]]): The background color of the dropdown field.
        border_color (Optional[Tuple[float, ...]]): The color of the dropdown's border.
        border_width (Optional[float]): The width of the dropdown's border.
    """

    _field_type: str = "dropdown"
    _widget_class: Type[Widget] = DropdownWidget

    options: Optional[List[Union[str, Tuple[str, str]]]] = None
    width: Optional[float] = None
    height: Optional[float] = None
    # pylint: disable=R0801
    font: Optional[str] = None
    font_size: Optional[float] = None
    font_color: Optional[Tuple[float, ...]] = None
    bg_color: Optional[Tuple[float, ...]] = None
    border_color: Optional[Tuple[float, ...]] = None
    border_width: Optional[float] = None
