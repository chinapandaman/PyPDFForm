# -*- coding: utf-8 -*-
"""Contains helpers for template."""

from typing import Dict, List, Tuple, Union

from pdfrw import PdfDict, PdfReader
from reportlab.pdfbase.pdfmetrics import stringWidth

from ..middleware.constants import ELEMENT_TYPES
from ..middleware.text import Text
from .constants import (ANNOTATION_KEY, ANNOTATION_RECTANGLE_KEY,
                        FIELD_FLAG_KEY, NEW_LINE_SYMBOL,
                        TEXT_FIELD_MAX_LENGTH_KEY)
from .patterns import (DROPDOWN_CHOICE_PATTERNS, ELEMENT_ALIGNMENT_PATTERNS,
                       ELEMENT_KEY_PATTERNS, ELEMENT_TYPE_PATTERNS,
                       TEXT_FIELD_FLAG_PATTERNS)
from .utils import find_pattern_match, traverse_pattern


def get_elements_by_page(pdf: Union[bytes, PdfReader]) -> Dict[int, List[PdfDict]]:
    """Iterates through a PDF and returns all elements found grouped by page."""

    if isinstance(pdf, bytes):
        pdf = PdfReader(fdata=pdf)

    result = {}

    for i, page in enumerate(pdf.pages):
        elements = page[ANNOTATION_KEY]
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


def get_element_key(element: PdfDict) -> Union[str, None]:
    """Finds a PDF element's annotated key by pattern matching."""

    result = None
    for pattern in ELEMENT_KEY_PATTERNS:
        value = traverse_pattern(pattern, element)
        if value:
            result = value[1:-1]
            break
    return result


def get_element_alignment(element: PdfDict) -> Union[str, None]:
    """Finds a PDF element's alignment by pattern matching."""

    result = None
    for pattern in ELEMENT_ALIGNMENT_PATTERNS:
        value = traverse_pattern(pattern, element)
        if value:
            result = value
            break
    return result


def construct_element(element: PdfDict, key: str) -> Union[ELEMENT_TYPES, None]:
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


def get_text_field_max_length(element: PdfDict) -> Union[int, None]:
    """Returns the max length of the text field if presented or None."""

    return (
        int(element[TEXT_FIELD_MAX_LENGTH_KEY])
        if TEXT_FIELD_MAX_LENGTH_KEY in element
        else None
    )


def is_text_field_comb(element: PdfDict) -> bool:
    """Returns true if characters in a text field needs to be formatted into combs."""

    try:
        return "{0:b}".format(int(element[FIELD_FLAG_KEY]))[::-1][24] == "1"
    except (IndexError, TypeError):
        return False


def is_text_multiline(element: PdfDict) -> bool:
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


def get_dropdown_choices(element: PdfDict) -> Union[Tuple[str], None]:
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


def get_char_rect_width(element: PdfDict, element_middleware: Text) -> float:
    """Returns rectangular width of each character for combed text fields."""

    rect_width = abs(
        float(element[ANNOTATION_RECTANGLE_KEY][0])
        - float(element[ANNOTATION_RECTANGLE_KEY][2])
    )
    return rect_width / element_middleware.max_length


def get_character_x_paddings(element: PdfDict, element_middleware: Text) -> List[float]:
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


def calculate_wrap_length(element: PdfDict, element_middleware: Text, v: str) -> int:
    """Increments the substring until reaching maximum horizontal width."""

    width = abs(
        float(element[ANNOTATION_RECTANGLE_KEY][0])
        - float(element[ANNOTATION_RECTANGLE_KEY][2])
    )
    value = element_middleware.value or ""
    value = value.replace(NEW_LINE_SYMBOL, " ")

    counter = 0
    _width = 0
    while _width <= width and counter < len(value):
        counter += 1
        _width = stringWidth(
            v[:counter],
            element_middleware.font,
            element_middleware.font_size,
        )
    return counter - 1


def get_paragraph_lines(element: PdfDict, element_middleware: Text) -> List[str]:
    """Splits the paragraph field's text to a list of lines."""

    # pylint: disable=R0912
    lines = []
    result = []
    text_wrap_length = element_middleware.text_wrap_length
    value = element_middleware.value or ""
    if element_middleware.max_length is not None:
        value = value[: element_middleware.max_length]

    width = abs(
        float(element[ANNOTATION_RECTANGLE_KEY][0])
        - float(element[ANNOTATION_RECTANGLE_KEY][2])
    )

    split_by_new_line_symbol = value.split(NEW_LINE_SYMBOL)
    for line in split_by_new_line_symbol:
        characters = line.split(" ")
        current_line = ""
        for each in characters:
            line_extended = f"{current_line} {each}" if current_line else each
            if len(line_extended) <= text_wrap_length:
                current_line = line_extended
            else:
                lines.append(current_line)
                current_line = each
        lines.append(
            current_line + NEW_LINE_SYMBOL
            if len(split_by_new_line_symbol) > 1
            else current_line
        )

    for line in lines:
        while stringWidth(
            line[:text_wrap_length],
            element_middleware.font,
            element_middleware.font_size,
        ) > width:
            text_wrap_length -= 1

    for each in lines:
        while len(each) > text_wrap_length:
            last_index = text_wrap_length
            result.append(each[:last_index])
            each = each[last_index:]
        if each:
            if (
                result
                and len(each) + 1 + len(result[-1]) <= text_wrap_length
                and NEW_LINE_SYMBOL not in result[-1]
            ):
                result[-1] = f"{result[-1]}{each} "
            else:
                result.append(f"{each} ")

    for i, each in enumerate(result):
        result[i] = each.replace(NEW_LINE_SYMBOL, "")

    if result:
        result[-1] = result[-1][:-1]

    return result


def get_paragraph_auto_wrap_length(element: PdfDict, element_middleware: Text) -> int:
    """Calculates the text wrap length of a paragraph field."""

    value = element_middleware.value or ""
    value = value.replace(NEW_LINE_SYMBOL, " ")
    width = abs(
        float(element[ANNOTATION_RECTANGLE_KEY][0])
        - float(element[ANNOTATION_RECTANGLE_KEY][2])
    )
    text_width = stringWidth(
        value,
        element_middleware.font,
        element_middleware.font_size,
    )

    lines = text_width / width
    if lines > 1:
        current_min = 0
        while len(value) and current_min < len(value):
            result = calculate_wrap_length(element, element_middleware, value)
            value = value[result:]
            if current_min == 0:
                current_min = result
            elif result < current_min:
                current_min = result
        return current_min

    return len(value) + 1
