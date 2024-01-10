# -*- coding: utf-8 -*-
"""Contains helpers for coordinates calculations."""

from copy import deepcopy
from typing import List, Tuple, Union

from reportlab.pdfbase.pdfmetrics import stringWidth

from ..middleware.text import Text
from .constants import ANNOTATION_RECTANGLE_KEY
from .template import (get_char_rect_width, get_widget_alignment,
                       is_text_multiline)


def get_draw_checkbox_radio_coordinates(
    widget: dict,
    widget_middleware: Text,
) -> Tuple[Union[float, int], Union[float, int]]:
    """Returns coordinates to draw at given a PDF form checkbox/radio widget."""

    string_height = widget_middleware.font_size * 96 / 72
    width_mid_point = (
        float(widget[ANNOTATION_RECTANGLE_KEY][0])
        + float(widget[ANNOTATION_RECTANGLE_KEY][2])
    ) / 2
    height_mid_point = (
        float(widget[ANNOTATION_RECTANGLE_KEY][1])
        + float(widget[ANNOTATION_RECTANGLE_KEY][3])
    ) / 2

    return (
        width_mid_point
        - stringWidth(
            widget_middleware.value,
            widget_middleware.font,
            widget_middleware.font_size,
        )
        / 2,
        (height_mid_point - string_height / 2 + height_mid_point) / 2,
    )


def get_draw_text_coordinates(
    widget: dict, widget_middleware: Text
) -> Tuple[Union[float, int], Union[float, int]]:
    """Returns coordinates to draw text at given a PDF form text widget."""

    if widget_middleware.preview:
        return (
            float(widget[ANNOTATION_RECTANGLE_KEY][0]),
            float(widget[ANNOTATION_RECTANGLE_KEY][3]) + 5,
        )

    text_value = widget_middleware.value or ""
    length = (
        min(len(text_value), widget_middleware.max_length)
        if widget_middleware.max_length is not None
        else len(text_value)
    )
    text_value = text_value[:length]

    if widget_middleware.text_wrap_length is not None:
        text_value = text_value[: widget_middleware.text_wrap_length]

    character_paddings = (
        widget_middleware.character_paddings[:length]
        if widget_middleware.character_paddings is not None
        else widget_middleware.character_paddings
    )

    alignment = get_widget_alignment(widget) or 0
    x = float(widget[ANNOTATION_RECTANGLE_KEY][0])

    if int(alignment) != 0:
        width_mid_point = (
            float(widget[ANNOTATION_RECTANGLE_KEY][0])
            + float(widget[ANNOTATION_RECTANGLE_KEY][2])
        ) / 2
        string_width = stringWidth(
            text_value,
            widget_middleware.font,
            widget_middleware.font_size,
        )
        if widget_middleware.comb is True and length:
            string_width = character_paddings[-1] + stringWidth(
                text_value[-1],
                widget_middleware.font,
                widget_middleware.font_size,
            )

        if int(alignment) == 1:
            x = width_mid_point - string_width / 2
        elif int(alignment) == 2:
            x = float(widget[ANNOTATION_RECTANGLE_KEY][2]) - string_width
            if length > 0 and widget_middleware.comb is True:
                x -= (
                    get_char_rect_width(widget, widget_middleware)
                    - stringWidth(
                        text_value[-1],
                        widget_middleware.font,
                        widget_middleware.font_size,
                    )
                ) / 2

    string_height = widget_middleware.font_size * 96 / 72
    height_mid_point = (
        float(widget[ANNOTATION_RECTANGLE_KEY][1])
        + float(widget[ANNOTATION_RECTANGLE_KEY][3])
    ) / 2
    y = (height_mid_point - string_height / 2 + height_mid_point) / 2
    if is_text_multiline(widget):
        y = float(widget[ANNOTATION_RECTANGLE_KEY][3]) - string_height / 1.5

    if int(alignment) == 1 and widget_middleware.comb is True and length != 0:
        x -= character_paddings[0] / 2
        if length % 2 == 0:
            x -= (
                character_paddings[0]
                + stringWidth(
                    text_value[:1],
                    widget_middleware.font,
                    widget_middleware.font_size,
                )
                / 2
            )

    return x, y


def get_text_line_x_coordinates(
    widget: dict, widget_middleware: Text
) -> Union[List[float], None]:
    """
    Returns the x coordinates to draw lines
    of the text at given a PDF form paragraph widget.
    """

    if (
        widget_middleware.text_wrap_length is not None
        and widget_middleware.text_lines is not None
        and len(widget_middleware.text_lines)
        and isinstance(widget_middleware.value, str)
        and len(widget_middleware.value) > widget_middleware.text_wrap_length
    ):
        result = []
        _widget = deepcopy(widget_middleware)
        for each in widget_middleware.text_lines:
            _widget.value = each
            _widget.text_wrap_length = None
            result.append(get_draw_text_coordinates(widget, _widget)[0])

        return result

    return None
