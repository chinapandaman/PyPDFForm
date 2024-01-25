# -*- coding: utf-8 -*-
"""Contains helpers for template middleware."""

from typing import Dict

from ..core.template import (construct_widget, get_character_x_paddings,
                             get_dropdown_choices, get_text_field_max_length,
                             get_widget_key, get_widgets_by_page,
                             is_text_field_comb, get_button_style)
from .constants import WIDGET_TYPES
from .checkbox import Checkbox
from .dropdown import Dropdown
from .radio import Radio
from .text import Text


def set_character_x_paddings(
    pdf_stream: bytes, widgets: Dict[str, WIDGET_TYPES]
) -> Dict[str, WIDGET_TYPES]:
    """Sets paddings between characters for combed text fields."""

    for _widgets in get_widgets_by_page(pdf_stream).values():
        for widget in _widgets:
            key = get_widget_key(widget)
            _widget = widgets[key]

            if isinstance(_widget, Text) and _widget.comb is True:
                _widget.character_paddings = get_character_x_paddings(widget, _widget)

    return widgets


def build_widgets(pdf_stream: bytes) -> Dict[str, WIDGET_TYPES]:
    """Builds a widget dict given a PDF form stream."""

    results = {}

    for widgets in get_widgets_by_page(pdf_stream).values():
        for widget in widgets:
            key = get_widget_key(widget)

            _widget = construct_widget(widget, key)

            if _widget is not None:
                if isinstance(_widget, Text):
                    _widget.max_length = get_text_field_max_length(widget)
                    if _widget.max_length is not None and is_text_field_comb(widget):
                        _widget.comb = True

                if isinstance(_widget, (Checkbox, Radio)):
                    _widget.button_style = get_button_style(widget)

                if isinstance(_widget, Dropdown):
                    _widget.choices = get_dropdown_choices(widget)

                if isinstance(_widget, Radio):
                    if key not in results:
                        results[key] = _widget

                    results[key].number_of_options += 1
                    continue

                results[key] = _widget

    return results


def dropdown_to_text(dropdown: Dropdown) -> Text:
    """Converts a dropdown widget to a text widget."""

    result = Text(dropdown.name)

    if dropdown.value is not None:
        result.value = (
            dropdown.choices[dropdown.value]
            if dropdown.value < len(dropdown.choices)
            else ""
        )

    return result
