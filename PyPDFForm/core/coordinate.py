# -*- coding: utf-8 -*-
"""Contains helpers for coordinates calculations."""

from typing import Tuple, Union, List
from copy import deepcopy
import pdfrw
from reportlab.pdfbase.pdfmetrics import stringWidth

from ..middleware.text import Text
from .constants import ANNOTATION_RECTANGLE_KEY
from .template import get_element_alignment, get_char_rect_width, is_text_multiline


def get_draw_checkbox_radio_coordinates(
    element: pdfrw.PdfDict,
    element_middleware: Text,
) -> Tuple[Union[float, int], Union[float, int]]:
    """Returns coordinates to draw at given a PDF form checkbox/radio element."""

    string_height = element_middleware.font_size * 96 / 72
    width_mid_point = (
        float(element[ANNOTATION_RECTANGLE_KEY][0])
        + float(element[ANNOTATION_RECTANGLE_KEY][2])
    ) / 2
    height_mid_point = (
        float(element[ANNOTATION_RECTANGLE_KEY][1])
        + float(element[ANNOTATION_RECTANGLE_KEY][3])
    ) / 2

    return (
        width_mid_point
        - stringWidth(
            element_middleware.value,
            element_middleware.font,
            element_middleware.font_size,
        )
        / 2,
        (height_mid_point - string_height / 2 + height_mid_point) / 2,
    )


def get_draw_text_coordinates(
    element: pdfrw.PdfDict, element_middleware: Text
) -> Tuple[Union[float, int], Union[float, int]]:
    """Returns coordinates to draw text at given a PDF form text element."""

    if element_middleware.preview:
        return (
            float(element[ANNOTATION_RECTANGLE_KEY][0]),
            float(element[ANNOTATION_RECTANGLE_KEY][3]) + 5,
        )

    element_value = element_middleware.value or ""
    length = (
        min(len(element_value), element_middleware.max_length)
        if element_middleware.max_length is not None
        else len(element_value)
    )
    element_value = element_value[:length]

    if element_middleware.text_wrap_length is not None:
        element_value = element_value[: element_middleware.text_wrap_length]

    character_paddings = (
        element_middleware.character_paddings[:length]
        if element_middleware.character_paddings is not None
        else element_middleware.character_paddings
    )

    alignment = get_element_alignment(element) or 0
    x = float(element[ANNOTATION_RECTANGLE_KEY][0])

    if int(alignment) != 0:
        width_mid_point = (
            float(element[ANNOTATION_RECTANGLE_KEY][0])
            + float(element[ANNOTATION_RECTANGLE_KEY][2])
        ) / 2
        string_width = stringWidth(
            element_value,
            element_middleware.font,
            element_middleware.font_size,
        )
        if element_middleware.comb is True and length:
            string_width = character_paddings[-1] + stringWidth(
                element_value[-1],
                element_middleware.font,
                element_middleware.font_size,
            )

        if int(alignment) == 1:
            x = width_mid_point - string_width / 2
        elif int(alignment) == 2:
            x = float(element[ANNOTATION_RECTANGLE_KEY][2]) - string_width
            if length > 0 and element_middleware.comb is True:
                x -= (
                    get_char_rect_width(element, element_middleware)
                    - stringWidth(
                        element_value[-1],
                        element_middleware.font,
                        element_middleware.font_size,
                    )
                ) / 2

    string_height = element_middleware.font_size * 96 / 72
    height_mid_point = (
        float(element[ANNOTATION_RECTANGLE_KEY][1])
        + float(element[ANNOTATION_RECTANGLE_KEY][3])
    ) / 2
    y = (height_mid_point - string_height / 2 + height_mid_point) / 2
    if is_text_multiline(element):
        y = float(element[ANNOTATION_RECTANGLE_KEY][3]) - string_height / 1.5

    if int(alignment) == 1 and element_middleware.comb is True and length != 0:
        x -= character_paddings[0] / 2
        if length % 2 == 0:
            x -= (
                character_paddings[0]
                + stringWidth(
                    element_value[:1],
                    element_middleware.font,
                    element_middleware.font_size,
                )
                / 2
            )

    return x, y


def get_text_line_x_coordinates(
    element: pdfrw.PdfDict, element_middleware: Text
) -> Union[List[float], None]:
    """
    Returns the x coordinates to draw lines
    of the text at given a PDF form paragraph element.
    """

    if (
        element_middleware.text_wrap_length is not None
        and element_middleware.text_lines is not None
        and len(element_middleware.text_lines)
        and isinstance(element_middleware.value, str)
        and len(element_middleware.value) > element_middleware.text_wrap_length
    ):
        result = []
        _ele = deepcopy(element_middleware)
        for each in element_middleware.text_lines:
            _ele.value = each
            _ele.text_wrap_length = None
            result.append(get_draw_text_coordinates(element, _ele)[0])

        return result

    return None
