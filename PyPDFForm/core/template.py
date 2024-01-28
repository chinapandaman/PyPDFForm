# -*- coding: utf-8 -*-
"""Contains helpers for template."""

from typing import Dict, List, Tuple, Union

from pypdf import PdfReader
from reportlab.pdfbase.pdfmetrics import stringWidth

from ..middleware.constants import WIDGET_TYPES
from ..middleware.text import Text
from .constants import (ANNOTATION_RECTANGLE_KEY, COMB, MULTILINE,
                        NEW_LINE_SYMBOL, TEXT_FIELD_MAX_LENGTH_KEY)
from .patterns import (BUTTON_STYLE_PATTERNS, DROPDOWN_CHOICE_PATTERNS,
                       TEXT_FIELD_FLAG_PATTERNS, WIDGET_ALIGNMENT_PATTERNS,
                       WIDGET_KEY_PATTERNS, WIDGET_TYPE_PATTERNS)
from .utils import find_pattern_match, stream_to_io, traverse_pattern


def get_widgets_by_page(pdf: bytes) -> Dict[int, List[dict]]:
    """Iterates through a PDF and returns all widgets found grouped by page."""

    pdf = PdfReader(stream_to_io(pdf))

    result = {}

    for i, page in enumerate(pdf.pages):
        widgets = page.annotations
        result[i + 1] = []
        if widgets:
            for widget in widgets:
                widget = dict(widget.get_object())
                for each in WIDGET_TYPE_PATTERNS:
                    patterns = each[0]
                    check = True
                    for pattern in patterns:
                        check = check and find_pattern_match(pattern, widget)
                    if check:
                        result[i + 1].append(widget)
                        break

    return result


def get_widget_key(widget: dict) -> Union[str, None]:
    """Finds a PDF widget's annotated key by pattern matching."""

    result = None
    for pattern in WIDGET_KEY_PATTERNS:
        value = traverse_pattern(pattern, widget)
        if value:
            result = value
            break
    return result


def get_widget_alignment(widget: dict) -> Union[str, None]:
    """Finds a PDF widget's alignment by pattern matching."""

    result = None
    for pattern in WIDGET_ALIGNMENT_PATTERNS:
        value = traverse_pattern(pattern, widget)
        if value:
            result = value
            break
    return result


def construct_widget(widget: dict, key: str) -> Union[WIDGET_TYPES, None]:
    """Finds a PDF widget's annotated type by pattern matching."""

    result = None
    for each in WIDGET_TYPE_PATTERNS:
        patterns, _type = each
        check = True
        for pattern in patterns:
            check = check and find_pattern_match(pattern, widget)
        if check:
            result = _type(key)
            break
    return result


def get_text_field_max_length(widget: dict) -> Union[int, None]:
    """Returns the max length of the text field if presented or None."""

    return (
        int(widget[TEXT_FIELD_MAX_LENGTH_KEY]) or None
        if TEXT_FIELD_MAX_LENGTH_KEY in widget
        else None
    )


def check_field_flag_bit(widget: dict, bit: int) -> bool:
    """Checks if a bit is set in a widget's field flag."""

    field_flag = None
    for pattern in TEXT_FIELD_FLAG_PATTERNS:
        field_flag = traverse_pattern(pattern, widget)
        if field_flag is not None:
            break

    if field_flag is None:
        return False

    return bool(int(field_flag) & bit)


def is_text_field_comb(widget: dict) -> bool:
    """Returns true if characters in a text field needs to be formatted into combs."""

    return check_field_flag_bit(widget, COMB)


def is_text_multiline(widget: dict) -> bool:
    """Returns true if a text field is a paragraph field."""

    return check_field_flag_bit(widget, MULTILINE)


def get_dropdown_choices(widget: dict) -> Union[Tuple[str], None]:
    """Returns string options of a dropdown field."""

    result = None
    for pattern in DROPDOWN_CHOICE_PATTERNS:
        choices = traverse_pattern(pattern, widget)
        if choices:
            result = tuple(
                (each if isinstance(each, str) else str(each[1])) for each in choices
            )
            break

    return result


def get_button_style(widget: dict) -> Union[str, None]:
    """Returns the button style of a checkbox or radiobutton."""

    for pattern in BUTTON_STYLE_PATTERNS:
        style = traverse_pattern(pattern, widget)
        if style is not None:
            return str(style)

    return None


def get_char_rect_width(widget: dict, widget_middleware: Text) -> float:
    """Returns rectangular width of each character for combed text fields."""

    rect_width = abs(
        float(widget[ANNOTATION_RECTANGLE_KEY][0])
        - float(widget[ANNOTATION_RECTANGLE_KEY][2])
    )
    return rect_width / widget_middleware.max_length


def get_character_x_paddings(widget: dict, widget_middleware: Text) -> List[float]:
    """Returns paddings between characters for combed text fields."""

    length = min(len(widget_middleware.value or ""), widget_middleware.max_length)
    char_rect_width = get_char_rect_width(widget, widget_middleware)

    result = []

    current_x = 0
    for char in (widget_middleware.value or "")[:length]:
        current_mid_point = current_x + char_rect_width / 2
        result.append(
            current_mid_point
            - stringWidth(char, widget_middleware.font, widget_middleware.font_size) / 2
        )
        current_x += char_rect_width

    return result


def calculate_wrap_length(widget: dict, widget_middleware: Text, v: str) -> int:
    """Increments the substring until reaching maximum horizontal width."""

    width = abs(
        float(widget[ANNOTATION_RECTANGLE_KEY][0])
        - float(widget[ANNOTATION_RECTANGLE_KEY][2])
    )
    value = widget_middleware.value or ""
    value = value.replace(NEW_LINE_SYMBOL, " ")

    counter = 0
    _width = 0
    while _width <= width and counter < len(value):
        counter += 1
        _width = stringWidth(
            v[:counter],
            widget_middleware.font,
            widget_middleware.font_size,
        )
    return counter - 1


def get_paragraph_lines(widget: dict, widget_middleware: Text) -> List[str]:
    """Splits the paragraph field's text to a list of lines."""

    # pylint: disable=R0912
    lines = []
    result = []
    text_wrap_length = widget_middleware.text_wrap_length
    value = widget_middleware.value or ""
    if widget_middleware.max_length is not None:
        value = value[: widget_middleware.max_length]

    width = abs(
        float(widget[ANNOTATION_RECTANGLE_KEY][0])
        - float(widget[ANNOTATION_RECTANGLE_KEY][2])
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
        while (
            stringWidth(
                line[:text_wrap_length],
                widget_middleware.font,
                widget_middleware.font_size,
            )
            > width
        ):
            text_wrap_length -= 1

    for each in lines:
        while len(each) > text_wrap_length:
            result.append(each[:text_wrap_length])
            each = each[text_wrap_length:]
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


def get_paragraph_auto_wrap_length(widget: dict, widget_middleware: Text) -> int:
    """Calculates the text wrap length of a paragraph field."""

    value = widget_middleware.value or ""
    value = value.replace(NEW_LINE_SYMBOL, " ")
    width = abs(
        float(widget[ANNOTATION_RECTANGLE_KEY][0])
        - float(widget[ANNOTATION_RECTANGLE_KEY][2])
    )
    text_width = stringWidth(
        value,
        widget_middleware.font,
        widget_middleware.font_size,
    )

    lines = text_width / width
    if lines > 1:
        current_min = 0
        while len(value) and current_min < len(value):
            result = calculate_wrap_length(widget, widget_middleware, value)
            value = value[result:]
            if current_min == 0:
                current_min = result
            elif result < current_min:
                current_min = result
        return current_min

    return len(value) + 1
