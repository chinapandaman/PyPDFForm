# -*- coding: utf-8 -*-
"""Contains helpers for template."""

from copy import deepcopy
from typing import Dict, List, Tuple, Union

import pdfrw
from reportlab.pdfbase.pdfmetrics import stringWidth

from ..middleware.constants import ELEMENT_TYPES
from ..middleware.text import Text
from . import constants
from .utils import find_pattern_match, traverse_pattern
from .patterns import (DROPDOWN_CHOICE_PATTERNS, ELEMENT_ALIGNMENT_PATTERNS,
                       ELEMENT_KEY_PATTERNS, ELEMENT_TYPE_PATTERNS,
                       TEXT_FIELD_FLAG_PATTERNS)


def get_elements_by_page(
    pdf: Union[bytes, pdfrw.PdfReader]
) -> Dict[int, List[pdfrw.PdfDict]]:
    """Iterates through a PDF and returns all elements found grouped by page."""

    if isinstance(pdf, bytes):
        pdf = pdfrw.PdfReader(fdata=pdf)

    result = {}

    for i, page in enumerate(pdf.pages):
        elements = page[constants.ANNOTATION_KEY]
        result[i + 1] = []
        if elements:
            for element in elements:
                for each in ELEMENT_TYPE_PATTERNS:
                    patterns = each[0]
                    check = True
                    for pattern in patterns:
                        check = check and find_pattern_match(pattern, element)
                    if check:
                        result[i + 1].append(element)
                        break

    return result


def get_element_key(element: pdfrw.PdfDict) -> Union[str, None]:
    """Finds a PDF element's annotated key by pattern matching."""

    result = None
    for pattern in ELEMENT_KEY_PATTERNS:
        value = traverse_pattern(pattern, element)
        if value:
            result = value[1:-1]
            break
    return result


def get_element_alignment(element: pdfrw.PdfDict) -> Union[str, None]:
    """Finds a PDF element's alignment by pattern matching."""

    result = None
    for pattern in ELEMENT_ALIGNMENT_PATTERNS:
        value = traverse_pattern(pattern, element)
        if value:
            result = value
            break
    return result


def construct_element(element: pdfrw.PdfDict, key: str) -> Union[ELEMENT_TYPES, None]:
    """Finds a PDF element's annotated type by pattern matching."""

    result = None
    for each in ELEMENT_TYPE_PATTERNS:
        patterns, _type = each
        check = True
        for pattern in patterns:
            check = check and find_pattern_match(pattern, element)
        if check:
            result = _type(key)
            break
    return result


def get_draw_checkbox_radio_coordinates(
    element: pdfrw.PdfDict,
    element_middleware: Text,
) -> Tuple[Union[float, int], Union[float, int]]:
    """Returns coordinates to draw at given a PDF form checkbox/radio element."""

    string_height = element_middleware.font_size * 96 / 72
    width_mid_point = (
        float(element[constants.ANNOTATION_RECTANGLE_KEY][0])
        + float(element[constants.ANNOTATION_RECTANGLE_KEY][2])
    ) / 2
    height_mid_point = (
        float(element[constants.ANNOTATION_RECTANGLE_KEY][1])
        + float(element[constants.ANNOTATION_RECTANGLE_KEY][3])
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


def get_text_field_max_length(element: pdfrw.PdfDict) -> Union[int, None]:
    """Returns the max length of the text field if presented or None."""

    return (
        int(element[constants.TEXT_FIELD_MAX_LENGTH_KEY])
        if constants.TEXT_FIELD_MAX_LENGTH_KEY in element
        else None
    )


def is_text_field_comb(element: pdfrw.PdfDict) -> bool:
    """Returns true if characters in a text field needs to be formatted into combs."""

    try:
        return "{0:b}".format(int(element[constants.FIELD_FLAG_KEY]))[::-1][24] == "1"
    except (IndexError, TypeError):
        return False


def is_text_multiline(element: pdfrw.PdfDict) -> bool:
    """Returns true if a text field is a paragraph field."""

    field_flag = None
    for pattern in TEXT_FIELD_FLAG_PATTERNS:
        field_flag = traverse_pattern(pattern, element)
        if field_flag is not None:
            break

    if field_flag is None:
        return False

    try:
        return "{0:b}".format(int(field_flag))[::-1][12] == "1"
    except (IndexError, TypeError):
        return False


def get_dropdown_choices(element: pdfrw.PdfDict) -> Union[Tuple[str], None]:
    """Returns string options of a dropdown field."""

    result = None
    for pattern in DROPDOWN_CHOICE_PATTERNS:
        choices = traverse_pattern(pattern, element)
        if choices:
            result = tuple(
                (each if isinstance(each, str) else str(each[1]))
                .replace("(", "")
                .replace(")", "")
                for each in choices
            )
            break

    return result


def get_char_rect_width(element: pdfrw.PdfDict, element_middleware: Text) -> float:
    """Returns rectangular width of each character for combed text fields."""

    rect_width = abs(
        float(element[constants.ANNOTATION_RECTANGLE_KEY][0])
        - float(element[constants.ANNOTATION_RECTANGLE_KEY][2])
    )
    return rect_width / element_middleware.max_length


def get_character_x_paddings(
    element: pdfrw.PdfDict, element_middleware: Text
) -> List[float]:
    """Returns paddings between characters for combed text fields."""

    length = min(len(element_middleware.value or ""), element_middleware.max_length)
    char_rect_width = get_char_rect_width(element, element_middleware)

    result = []

    current_x = 0
    for char in (element_middleware.value or "")[:length]:
        current_mid_point = current_x + char_rect_width / 2
        result.append(
            current_mid_point
            - stringWidth(char, element_middleware.font, element_middleware.font_size)
            / 2
        )
        current_x += char_rect_width

    return result


def get_draw_text_coordinates(
    element: pdfrw.PdfDict, element_middleware: Text
) -> Tuple[Union[float, int], Union[float, int]]:
    """Returns coordinates to draw text at given a PDF form text element."""

    if element_middleware.preview:
        return (
            float(element[constants.ANNOTATION_RECTANGLE_KEY][0]),
            float(element[constants.ANNOTATION_RECTANGLE_KEY][3]) + 5,
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
    x = float(element[constants.ANNOTATION_RECTANGLE_KEY][0])

    if int(alignment) != 0:
        width_mid_point = (
            float(element[constants.ANNOTATION_RECTANGLE_KEY][0])
            + float(element[constants.ANNOTATION_RECTANGLE_KEY][2])
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
            x = float(element[constants.ANNOTATION_RECTANGLE_KEY][2]) - string_width
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
        float(element[constants.ANNOTATION_RECTANGLE_KEY][1])
        + float(element[constants.ANNOTATION_RECTANGLE_KEY][3])
    ) / 2
    y = (height_mid_point - string_height / 2 + height_mid_point) / 2
    if is_text_multiline(element):
        y = float(element[constants.ANNOTATION_RECTANGLE_KEY][3]) - string_height / 1.5

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
