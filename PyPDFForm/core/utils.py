# -*- coding: utf-8 -*-
"""Contains utility helpers."""

from io import BytesIO
from typing import Union, Dict

import pdfrw

from ..middleware.checkbox import Checkbox
from ..middleware.radio import Radio
from ..middleware.text import Text
from ..middleware.constants import ELEMENT_TYPES
from . import constants, template, font_size as font_size_core


def generate_stream(pdf: pdfrw.PdfReader) -> bytes:
    """Generates new stream for manipulated PDF form."""

    result_stream = BytesIO()

    pdfrw.PdfWriter().write(result_stream, pdf)
    result_stream.seek(0)

    result = result_stream.read()
    result_stream.close()

    return result


def update_text_field_attributes(
    template_stream: bytes,
    elements: Dict[str, ELEMENT_TYPES],
) -> None:
    """Updates text fields' font sizes."""

    template_pdf = pdfrw.PdfReader(fdata=template_stream)

    for _, _elements in template.get_elements_by_page(template_pdf).items():
        for _element in _elements:
            key = template.get_element_key(_element)

            if isinstance(elements[key], Text) and elements[key].font_size is None:
                elements[key].font_size = template.get_text_field_font_size(
                    _element
                ) or font_size_core.text_field_font_size(_element)


def checkbox_radio_to_draw(
    element: Union[Checkbox, Radio], font_size: Union[float, int]
) -> Text:
    """Converts a checkbox/radio element to a drawable text element."""

    new_element = Text(
        element_name=element.name,
        element_value="",
    )
    new_element.font = "Helvetica"
    new_element.font_size = font_size
    new_element.font_color = (0, 0, 0)
    new_element.text_x_offset = 0
    new_element.text_y_offset = 0
    new_element.text_wrap_length = 100

    if isinstance(element, Checkbox):
        new_element.value = constants.CHECKBOX_TO_DRAW
    elif isinstance(element, Radio):
        new_element.value = constants.RADIO_TO_DRAW

    return new_element


def merge_two_pdfs(pdf: bytes, other: bytes) -> bytes:
    """Merges two PDFs into one PDF."""

    writer = pdfrw.PdfWriter()

    writer.addpages(pdfrw.PdfReader(fdata=pdf).pages)
    writer.addpages(pdfrw.PdfReader(fdata=other).pages)

    result_stream = BytesIO()
    writer.write(result_stream)
    result_stream.seek(0)

    result = result_stream.read()
    result_stream.close()

    return result
