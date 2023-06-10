# -*- coding: utf-8 -*-
"""Contains helpers for template."""

from typing import Dict, List, Tuple, Union

import pdfrw
from reportlab.pdfbase.pdfmetrics import stringWidth

from ..middleware.constants import ELEMENT_TYPES
from ..middleware.text import Text
from . import constants, utils
from .patterns import (DROPDOWN_CHOICE_PATTERNS, ELEMENT_ALIGNMENT_PATTERNS,
                       ELEMENT_KEY_PATTERNS, ELEMENT_TYPE_PATTERNS,
                       TEXT_FIELD_APPEARANCE_PATTERNS)


def remove_all_elements(pdf: bytes) -> bytes:
    """Removes all elements from a pdfrw parsed PDF form."""

    pdf = pdfrw.PdfReader(fdata=pdf)

    for page in pdf.pages:
        elements = page[constants.ANNOTATION_KEY]
        if elements:
            for j in reversed(range(len(elements))):
                elements.pop(j)

    return utils.generate_stream(pdf)


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


def find_pattern_match(pattern: dict, element: pdfrw.PdfDict) -> bool:
    """Checks if a PDF dict pattern exists in a PDF element."""

    for key, value in element.items():
        result = False
        if key in pattern:
            if isinstance(pattern[key], dict) and isinstance(value, pdfrw.PdfDict):
                result = find_pattern_match(pattern[key], value)
            else:
                result = pattern[key] == value
        if result:
            return result
    return False


def traverse_pattern(pattern: dict, element: pdfrw.PdfDict) -> Union[str, list, None]:
    """Traverses down a PDF dict pattern and find the value."""

    for key, value in element.items():
        result = None
        if key in pattern:
            if isinstance(pattern[key], dict) and isinstance(value, pdfrw.PdfDict):
                result = traverse_pattern(pattern[key], value)
            else:
                if pattern[key] is True and value:
                    return value
        if result:
            return result
    return None


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


def get_text_field_font_size(element: pdfrw.PdfDict) -> Union[float, int]:
    """Returns the font size of the text field if presented or zero."""

    result = 0
    for pattern in TEXT_FIELD_APPEARANCE_PATTERNS:
        text_appearance = traverse_pattern(pattern, element)
        if text_appearance:
            properties = text_appearance.split(" ")
            if len(properties) > 1:
                try:
                    result = float(properties[1])
                except ValueError:
                    pass

    return result


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
    except IndexError:
        return False


def is_text_multiline(element: pdfrw.PdfDict) -> bool:
    """Returns true if a text field is a paragraph field."""

    try:
        return "{0:b}".format(int(element[constants.FIELD_FLAG_KEY]))[::-1][12] == "1"
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

    element_value = element_middleware.value or ""
    length = (
        min(len(element_value), element_middleware.max_length)
        if element_middleware.max_length is not None
        else len(element_value)
    )
    element_value = element_value[:length]
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
