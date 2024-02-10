# -*- coding: utf-8 -*-
"""Contains helpers for template middleware."""

from typing import Dict, List

from ..core.constants import ANNOTATION_RECTANGLE_KEY
from ..core.font import (auto_detect_font, get_text_field_font_color,
                         get_text_field_font_size, text_field_font_size)
from ..core.template import (construct_widget, get_button_style,
                             get_character_x_paddings, get_dropdown_choices,
                             get_paragraph_auto_wrap_length,
                             get_paragraph_lines, get_text_field_max_length,
                             get_widget_key, get_widgets_by_page,
                             is_text_field_comb, is_text_multiline)
from ..core.watermark import create_watermarks_and_draw
from .checkbox import Checkbox
from .constants import WIDGET_TYPES
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


def widget_rect_watermarks(pdf: bytes) -> List[bytes]:
    """Draws the rectangular border of each widget and returns watermarks."""

    watermarks = []

    for page, widgets in get_widgets_by_page(pdf).items():
        to_draw = []
        for widget in widgets:
            rect = widget[ANNOTATION_RECTANGLE_KEY]
            x = rect[0]
            y = rect[1]
            width = abs(rect[0] - rect[2])
            height = abs(rect[1] - rect[3])

            to_draw.append([x, y, width, height])
        watermarks.append(
            create_watermarks_and_draw(pdf, page, "rect", to_draw)[page - 1]
        )

    return watermarks


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


def update_text_field_attributes(
    template_stream: bytes,
    widgets: Dict[str, WIDGET_TYPES],
) -> None:
    """Auto updates text fields' attributes."""

    for _, _widgets in get_widgets_by_page(template_stream).items():
        for _widget in _widgets:
            key = get_widget_key(_widget)

            if isinstance(widgets[key], Text):
                if widgets[key].font is None:
                    widgets[key].font = auto_detect_font(_widget)
                if widgets[key].font_size is None:
                    widgets[key].font_size = get_text_field_font_size(
                        _widget
                    ) or text_field_font_size(_widget)
                if widgets[key].font_color is None:
                    widgets[key].font_color = get_text_field_font_color(_widget)
                if is_text_multiline(_widget) and widgets[key].text_wrap_length is None:
                    widgets[key].text_wrap_length = get_paragraph_auto_wrap_length(
                        _widget, widgets[key]
                    )
                    widgets[key].text_lines = get_paragraph_lines(_widget, widgets[key])
