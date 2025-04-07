# -*- coding: utf-8 -*-
"""Provides checkbox widget creation functionality for PDF forms.

This module contains the CheckBoxWidget class which handles creation of:
- Interactive checkbox fields with three states (checked, unchecked, read-only)
- Custom button styles (check, cross, circle)
- Color styling for tick, background and border
- Size adjustments
- PDF form field integration

Supports all standard PDF checkbox properties and integrates with both
AcroForm and non-AcroForm PDF documents.

Example:
    >>> widget = CheckBoxWidget(
    ...     name="agree",
    ...     page_number=1,
    ...     x=100,
    ...     y=200,
    ...     size=20,
    ...     button_style="check",
    ...     tick_color=(0,0,0)  # Black
    ... )
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
