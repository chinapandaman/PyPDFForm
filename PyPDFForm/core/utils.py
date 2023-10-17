# -*- coding: utf-8 -*-
"""Contains utility helpers."""

from io import BytesIO
from typing import Dict, List, Union

import pdfrw
from reportlab.pdfbase.pdfmetrics import stringWidth

from ..middleware.checkbox import Checkbox
from ..middleware.constants import ELEMENT_TYPES
from ..middleware.radio import Radio
from ..middleware.text import Text
from . import constants
from . import font_size as font_size_core
from . import template
from . import font as font_core


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
                if elements[key].font is None:
                    elements[key].font = font_core.auto_detect_font(_element)
                if elements[key].font_size is None:
                    elements[key].font_size = template.get_text_field_font_size(
                        _element
                    ) or font_size_core.text_field_font_size(_element)
                if elements[key].font_color is None:
                    elements[key].font_color = template.get_text_field_font_color(
                        _element
                    )
                if (
                    template.is_text_multiline(_element)
                    and elements[key].text_wrap_length is None
                ):
                    elements[key].text_wrap_length = get_paragraph_auto_wrap_length(
                        _element, elements[key]
                    )
                    elements[key].text_lines = get_paragraph_lines(elements[key])


def get_paragraph_lines(element_middleware: Text) -> List[str]:
    """Splits the paragraph field's text to a list of lines."""

    lines = []
    result = []
    text_wrap_length = element_middleware.text_wrap_length
    value = element_middleware.value or ""
    if element_middleware.max_length is not None:
        value = value[: element_middleware.max_length]
    characters = value.split(" ")
    current_line = ""
    for each in characters:
        line_extended = f"{current_line} {each}" if current_line else each
        if len(line_extended) <= text_wrap_length:
            current_line = line_extended
        else:
            lines.append(current_line)
            current_line = each
    lines.append(current_line)

    for each in lines:
        while len(each) > text_wrap_length:
            last_index = text_wrap_length - 1
            result.append(each[:last_index])
            each = each[last_index:]
        if each:
            if result and len(each) + 1 + len(result[-1]) <= text_wrap_length:
                result[-1] = f"{result[-1]}{each} "
            else:
                result.append(f"{each} ")

    if result:
        result[-1] = result[-1][:-1]

    return result


def get_paragraph_auto_wrap_length(
    element: pdfrw.PdfDict, element_middleware: Text
) -> int:
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
    new_element.font = constants.DEFAULT_FONT
    new_element.font_size = font_size
    new_element.font_color = constants.DEFAULT_FONT_COLOR

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
