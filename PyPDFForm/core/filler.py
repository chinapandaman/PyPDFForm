# -*- coding: utf-8 -*-
"""Contains helpers for filling a PDF form."""

from typing import Dict

from ..middleware.checkbox import Checkbox
from ..middleware.constants import WIDGET_TYPES
from ..middleware.radio import Radio
from ..middleware.signature import Signature
from .coordinate import (get_draw_checkbox_radio_coordinates,
                         get_draw_sig_coordinates_resolutions,
                         get_draw_text_coordinates,
                         get_text_line_x_coordinates)
from .font import checkbox_radio_font_size
from .image import any_image_to_jpg
from .template import get_widget_key, get_widgets_by_page
from .utils import checkbox_radio_to_draw
from .watermark import create_watermarks_and_draw, merge_watermarks_with_pdf


def fill(
    template_stream: bytes,
    widgets: Dict[str, WIDGET_TYPES],
) -> bytes:
    """Fills a PDF using watermarks."""

    # pylint: disable=too-many-branches
    texts_to_draw = {}
    images_to_draw = {}
    any_image_to_draw = False
    text_watermarks = []
    image_watermarks = []

    radio_button_tracker = {}

    for page, _widgets in get_widgets_by_page(template_stream).items():
        texts_to_draw[page] = []
        images_to_draw[page] = []
        text_watermarks.append(b"")
        image_watermarks.append(b"")
        for _widget in _widgets:
            key = get_widget_key(_widget)
            text_needs_to_be_drawn = False
            _to_draw = x = y = None

            if isinstance(widgets[key], (Checkbox, Radio)):
                font_size = checkbox_radio_font_size(_widget)
                _to_draw = checkbox_radio_to_draw(widgets[key], font_size)
                x, y = get_draw_checkbox_radio_coordinates(_widget, _to_draw)
                if isinstance(widgets[key], Checkbox) and widgets[key].value:
                    text_needs_to_be_drawn = True
                elif isinstance(widgets[key], Radio):
                    if key not in radio_button_tracker:
                        radio_button_tracker[key] = 0
                    radio_button_tracker[key] += 1
                    if widgets[key].value == radio_button_tracker[key] - 1:
                        text_needs_to_be_drawn = True
            elif isinstance(widgets[key], Signature):
                stream = widgets[key].stream
                if stream is not None:
                    any_image_to_draw = True
                    stream = any_image_to_jpg(stream)
                    x, y, width, height = get_draw_sig_coordinates_resolutions(_widget)
                    images_to_draw[page].append(
                        [
                            stream,
                            x,
                            y,
                            width,
                            height,
                        ]
                    )
            else:
                widgets[key].text_line_x_coordinates = get_text_line_x_coordinates(
                    _widget, widgets[key]
                )
                x, y = get_draw_text_coordinates(_widget, widgets[key])
                _to_draw = widgets[key]
                text_needs_to_be_drawn = True

            if all(
                [
                    text_needs_to_be_drawn,
                    _to_draw is not None,
                    x is not None,
                    y is not None,
                ]
            ):
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

    result = merge_watermarks_with_pdf(template_stream, text_watermarks)

    if any_image_to_draw:
        for page, images in images_to_draw.items():
            _watermarks = create_watermarks_and_draw(
                template_stream, page, "image", images
            )
            for i, watermark in enumerate(_watermarks):
                if watermark:
                    image_watermarks[i] = watermark
        result = merge_watermarks_with_pdf(result, image_watermarks)

    return result
