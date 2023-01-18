# -*- coding: utf-8 -*-
"""Contains helpers for filling a PDF form."""

from copy import deepcopy
from typing import Dict

import pdfrw

from ..middleware.element import Element as ElementMiddleware
from ..middleware.element import ElementType
from . import template, utils
from . import watermark as watermark_core


def fill_v2(
    template_stream: bytes,
    elements: Dict[str, ElementMiddleware],
) -> bytes:
    """Fills a PDF using watermarks."""

    template_pdf = pdfrw.PdfReader(fdata=template_stream)

    texts_to_draw = {}
    text_watermarks = []

    radio_button_tracker = {}

    for page, _elements in template.get_elements_by_page_v2(template_pdf).items():
        texts_to_draw[page] = []
        text_watermarks.append(b"")
        for _element in _elements:
            key = template.get_element_key_v2(_element)

            if elements[key].type == ElementType.checkbox:
                if elements[key].value:
                    font_size = utils.checkbox_radio_font_size(_element)
                    _to_draw = utils.checkbox_radio_to_draw(elements[key], font_size)
                    x, y = template.get_draw_checkbox_radio_coordinates_v2(
                        _element, _to_draw
                    )
                    texts_to_draw[page].append(
                        [
                            _to_draw,
                            x,
                            y,
                        ]
                    )
            elif elements[key].type == ElementType.radio:
                if key not in radio_button_tracker:
                    radio_button_tracker[key] = 0
                radio_button_tracker[key] += 1

                if elements[key].value == radio_button_tracker[key] - 1:
                    font_size = utils.checkbox_radio_font_size(_element)
                    _to_draw = utils.checkbox_radio_to_draw(elements[key], font_size)
                    x, y = template.get_draw_checkbox_radio_coordinates_v2(
                        _element, _to_draw
                    )
                    texts_to_draw[page].append(
                        [
                            _to_draw,
                            x,
                            y,
                        ]
                    )
            elif elements[key].type == ElementType.dropdown:
                ele = deepcopy(elements[key])
                ele.value = (
                    ele.choices[ele.value] if ele.value < len(ele.choices) else ""
                )
                x, y = template.get_draw_text_coordinates_v2(_element, ele)
                texts_to_draw[page].append(
                    [
                        ele,
                        x,
                        y,
                    ]
                )
            else:
                x, y = template.get_draw_text_coordinates_v2(_element, elements[key])
                texts_to_draw[page].append(
                    [
                        elements[key],
                        x,
                        y,
                    ]
                )

    for page, texts in texts_to_draw.items():
        _watermarks = watermark_core.create_watermarks_and_draw(
            template_stream, page, "text", texts
        )
        for i, watermark in enumerate(_watermarks):
            if watermark:
                text_watermarks[i] = watermark

    return watermark_core.merge_watermarks_with_pdf(
        utils.generate_stream(template_pdf), text_watermarks
    )
