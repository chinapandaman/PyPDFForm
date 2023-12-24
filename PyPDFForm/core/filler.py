# -*- coding: utf-8 -*-
"""Contains helpers for filling a PDF form."""

from typing import Dict

from pdfrw import PdfReader

from ..middleware.checkbox import Checkbox
from ..middleware.constants import WIDGET_TYPES
from ..middleware.radio import Radio
from .coordinate import (get_draw_checkbox_radio_coordinates,
                         get_draw_text_coordinates,
                         get_text_line_x_coordinates)
from .font import checkbox_radio_font_size
from .template import get_widget_key, get_widgets_by_page
from .utils import checkbox_radio_to_draw, generate_stream
from .watermark import create_watermarks_and_draw, merge_watermarks_with_pdf


def fill(
    template_stream: bytes,
    widgets: Dict[str, WIDGET_TYPES],
) -> bytes:
    """Fills a PDF using watermarks."""

    template_pdf = PdfReader(fdata=template_stream)

    texts_to_draw = {}
    text_watermarks = []

    radio_button_tracker = {}

    for page, _widgets in get_widgets_by_page(template_pdf).items():
        texts_to_draw[page] = []
        text_watermarks.append(b"")
        for _widget in _widgets:
            key = get_widget_key(_widget)
            needs_to_be_drawn = False

            if isinstance(widgets[key], (Checkbox, Radio)):
                font_size = checkbox_radio_font_size(_widget)
                _to_draw = checkbox_radio_to_draw(widgets[key], font_size)
                x, y = get_draw_checkbox_radio_coordinates(_widget, _to_draw)
                if isinstance(widgets[key], Checkbox) and widgets[key].value:
                    needs_to_be_drawn = True
                elif isinstance(widgets[key], Radio):
                    if key not in radio_button_tracker:
                        radio_button_tracker[key] = 0
                    radio_button_tracker[key] += 1
                    if widgets[key].value == radio_button_tracker[key] - 1:
                        needs_to_be_drawn = True
            else:
                widgets[key].text_line_x_coordinates = get_text_line_x_coordinates(
                    _widget, widgets[key]
                )
                x, y = get_draw_text_coordinates(_widget, widgets[key])
                _to_draw = widgets[key]
                needs_to_be_drawn = True

            if needs_to_be_drawn:
                texts_to_draw[page].append(
                    [
                        _to_draw,
                        x,
                        y,
                    ]
                )

    for page, texts in texts_to_draw.items():
        _watermarks = create_watermarks_and_draw(template_stream, page, "text", texts)
        for i, watermark in enumerate(_watermarks):
            if watermark:
                text_watermarks[i] = watermark

    return merge_watermarks_with_pdf(generate_stream(template_pdf), text_watermarks)
