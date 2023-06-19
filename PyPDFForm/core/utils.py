# -*- coding: utf-8 -*-
"""Contains utility helpers."""

from io import BytesIO
from typing import Union, Dict

import pdfrw
from reportlab.pdfbase.pdfmetrics import stringWidth

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
    """Auto updates text fields' attributes."""

    template_pdf = pdfrw.PdfReader(fdata=template_stream)

    for _, _elements in template.get_elements_by_page(template_pdf).items():
        for _element in _elements:
            key = template.get_element_key(_element)

            if isinstance(elements[key], Text):
                if elements[key].font_size is None:
                    elements[key].font_size = template.get_text_field_font_size(
                        _element
                    ) or font_size_core.text_field_font_size(_element)
                if template.is_text_multiline(_element):
                    elements[key].text_wrap_length = get_paragraph_auto_wrap_length(
                        _element, elements[key]
                    )


def get_paragraph_auto_wrap_length(element: pdfrw.PdfDict, element_middleware: Text) -> int:
    """Calculates the text wrap length of a paragraph field."""

    value = element_middleware.value or ""
    width = abs(
        float(element[constants.ANNOTATION_RECTANGLE_KEY][0])
        - float(element[constants.ANNOTATION_RECTANGLE_KEY][2])
    )
    text_width = stringWidth(
        value,
        element_middleware.font,
        element_middleware.font_size,
    )

    lines = text_width / width
    if lines > 1:
        counter = 0
        _width = 0
        while _width <= width:
            counter += 1
            _width = stringWidth(
                value[:counter],
                element_middleware.font,
                element_middleware.font_size,
            )
        return counter - 1

    return len(value) + 1


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


def remove_all_elements(pdf: bytes) -> bytes:
    """Removes all elements from a pdfrw parsed PDF form."""

    pdf = pdfrw.PdfReader(fdata=pdf)

    for page in pdf.pages:
        elements = page[constants.ANNOTATION_KEY]
        if elements:
            for j in reversed(range(len(elements))):
                elements.pop(j)

    return generate_stream(pdf)


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
