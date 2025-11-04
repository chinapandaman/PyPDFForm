# -*- coding: utf-8 -*-
"""
This module defines the `TextField` and `TextWidget` classes, which are used to
represent and manipulate text fields within PDF documents.

The `TextField` class is a dataclass that encapsulates the properties of a text
field, such as its dimensions, styling, and behavior.

The `TextWidget` class extends the base `Widget` class to provide specific
functionality for interacting with text form fields in PDFs.
"""

from dataclasses import dataclass
from typing import Optional, Tuple, Type

from .base import Field, Widget


class TextWidget(Widget):
    """
    Represents a text widget in a PDF form.

    This class inherits from the base Widget class and provides specific
    parameters for text field styling, such as width, height, font size,
    font color, background color, border color, border width, and maximum
    length.

    Attributes:
        USER_PARAMS (list): A list of tuples, where each tuple contains the
            user-facing parameter name and the corresponding AcroForm parameter name.
        COLOR_PARAMS (list): A list of user-facing parameter names that represent colors.
        ALLOWED_HOOK_PARAMS (list): A list of allowed hook parameters.
        NONE_DEFAULTS (list): A list of parameters that default to None.
        ACRO_FORM_FUNC (str): The name of the AcroForm function to use for
            creating the text field.
    """

    USER_PARAMS = [
        ("required", "required"),
        ("tooltip", "tooltip"),
        ("width", "width"),
        ("height", "height"),
        ("font_size", "fontSize"),
        ("font_color", "textColor"),
        ("bg_color", "fillColor"),
        ("border_color", "borderColor"),
        ("border_width", "borderWidth"),
        ("max_length", "maxlen"),
    ]
    COLOR_PARAMS = ["font_color", "bg_color", "border_color"]
    ALLOWED_HOOK_PARAMS = ["alignment", "multiline", "comb", "font"]
    NONE_DEFAULTS = ["max_length"]
    ACRO_FORM_FUNC = "textfield"


@dataclass
class TextField(Field):
    """
    Represents a text field in a PDF document.

    This dataclass extends the `Field` base class and defines the specific
    attributes that can be configured for a text input field.

    Attributes:
        _field_type (str): The type of the field, fixed as "text".
        _widget_class (Type[Widget]): The widget class associated with this field type.
        width (Optional[float]): The width of the text field.
        height (Optional[float]): The height of the text field.
        max_length (Optional[int]): The maximum number of characters allowed in the text field.
        comb (Optional[bool]): If True, the text field will display characters
            individually in a row of boxes.
        font (Optional[str]): The font to use for the text field.
        font_size (Optional[float]): The font size for the text.
        font_color (Optional[Tuple[float, ...]]): The color of the font as an RGB or RGBA tuple.
        bg_color (Optional[Tuple[float, ...]]): The background color of the text field.
        border_color (Optional[Tuple[float, ...]]): The color of the text field's border.
        border_width (Optional[float]): The width of the text field's border.
        alignment (Optional[int]): The text alignment within the field (e.g., 0 for left, 1 for center, 2 for right).
        multiline (Optional[bool]): If True, the text field can display multiple lines of text.
    """

    _field_type: str = "text"
    _widget_class: Type[Widget] = TextWidget

    width: Optional[float] = None
    height: Optional[float] = None
    max_length: Optional[int] = None
    comb: Optional[bool] = None
    font: Optional[str] = None
    font_size: Optional[float] = None
    font_color: Optional[Tuple[float, ...]] = None
    bg_color: Optional[Tuple[float, ...]] = None
    border_color: Optional[Tuple[float, ...]] = None
    border_width: Optional[float] = None
    alignment: Optional[int] = None
    multiline: Optional[bool] = None
