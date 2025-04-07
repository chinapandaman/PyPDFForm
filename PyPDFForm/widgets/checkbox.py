# -*- coding: utf-8 -*-
"""Provides checkbox widget creation functionality for PDF forms.

This module contains the CheckBoxWidget class which handles creation of:
- Interactive checkbox fields
- Custom button styles (check, cross, circle)
- Color styling for tick, background and border
- Size adjustments
"""

from .base import Widget


class CheckBoxWidget(Widget):
    """Creates and configures PDF checkbox widgets.

    Supports all standard checkbox properties including:
    - Button style customization (check, cross, circle)
    - Tick, background and border colors
    - Size adjustments
    - PDF form field integration

    Inherits from Widget base class adding checkbox-specific parameters.
    """

    USER_PARAMS = [
        ("size", "size"),
        ("button_style", "buttonStyle"),
        ("tick_color", "textColor"),
        ("bg_color", "fillColor"),
        ("border_color", "borderColor"),
        ("border_width", "borderWidth"),
    ]
    COLOR_PARAMS = ["tick_color", "bg_color", "border_color"]
    ACRO_FORM_FUNC = "checkbox"
