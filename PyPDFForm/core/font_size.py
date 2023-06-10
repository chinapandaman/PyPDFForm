# -*- coding: utf-8 -*-
"""Contains helpers for calculating font sizes."""

from math import sqrt
from typing import Dict, Union

import pdfrw

from ..middleware.constants import ELEMENT_TYPES, GLOBAL_FONT_SIZE
from ..middleware.text import Text
from . import constants, template


def update_text_field_font_sizes(
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
                ) or text_field_font_size(_element)


def text_field_font_size(element: pdfrw.PdfDict) -> Union[float, int]:
    """
    Calculates the font size it should be drawn with
    given a text field element.
    """

    if template.is_text_multiline(element):
        return GLOBAL_FONT_SIZE

    height = abs(
        float(element[constants.ANNOTATION_RECTANGLE_KEY][1])
        - float(element[constants.ANNOTATION_RECTANGLE_KEY][3])
    )

    return height * 2 / 3


def checkbox_radio_font_size(element: pdfrw.PdfDict) -> Union[float, int]:
    """
    Calculates the font size it should be drawn with
    given a checkbox/radio button element.
    """

    area = abs(
        float(element[constants.ANNOTATION_RECTANGLE_KEY][0])
        - float(element[constants.ANNOTATION_RECTANGLE_KEY][2])
    ) * abs(
        float(element[constants.ANNOTATION_RECTANGLE_KEY][1])
        - float(element[constants.ANNOTATION_RECTANGLE_KEY][3])
    )

    return sqrt(area) * 72 / 96
