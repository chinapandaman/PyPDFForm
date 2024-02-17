# -*- coding: utf-8 -*-
"""Contains helpers for coordinates calculations."""

from copy import deepcopy
from typing import List, Tuple, Union

from pypdf import PdfReader
from reportlab.pdfbase.pdfmetrics import stringWidth

from .constants import (ANNOTATION_RECTANGLE_KEY,
                        COORDINATE_GRID_FONT_SIZE_MARGIN_RATIO, DEFAULT_FONT)
from .middleware.text import Text
from .template import (get_char_rect_width, get_widget_alignment,
                       is_text_multiline)
from .utils import stream_to_io
from .watermark import create_watermarks_and_draw, merge_watermarks_with_pdf


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


def get_draw_sig_coordinates_resolutions(
    widget: dict,
) -> Tuple[float, float, float, float]:
    """
    Returns coordinates and resolutions to draw signature at given a PDF form signature widget.
    """

    x = float(widget[ANNOTATION_RECTANGLE_KEY][0])
    y = float(widget[ANNOTATION_RECTANGLE_KEY][1])
    width = abs(
        float(widget[ANNOTATION_RECTANGLE_KEY][0])
        - float(widget[ANNOTATION_RECTANGLE_KEY][2])
    )
    height = abs(
        float(widget[ANNOTATION_RECTANGLE_KEY][1])
        - float(widget[ANNOTATION_RECTANGLE_KEY][3])
    )

    return x, y, width, height


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


def generate_coordinate_grid(
    pdf: bytes, color: Tuple[float, float, float], margin: float
) -> bytes:
    """Creates a grid view for the coordinates of a PDF."""

    pdf_file = PdfReader(stream_to_io(pdf))
    lines_by_page = {}
    texts_by_page = {}
    watermarks = []

    for i, page in enumerate(pdf_file.pages):
        lines_by_page[i + 1] = []
        texts_by_page[i + 1] = []
        width = float(page.mediabox[2])
        height = float(page.mediabox[3])

        r, g, b = color

        current = margin
        while current < width:
            lines_by_page[i + 1].append([current, 0, current, height, r, g, b])
            current += margin

        current = margin
        while current < height:
            lines_by_page[i + 1].append([0, current, width, current, r, g, b])
            current += margin

        x = margin
        while x < width:
            y = margin
            while y < height:
                value = f"({x}, {y})"
                font_size = margin * COORDINATE_GRID_FONT_SIZE_MARGIN_RATIO
                text = Text("new_coordinate", value)
                text.font = DEFAULT_FONT
                text.font_size = font_size
                text.font_color = color
                texts_by_page[i + 1].append(
                    [
                        text,
                        x - stringWidth(value, DEFAULT_FONT, font_size),
                        y - font_size,
                    ]
                )
                y += margin
            x += margin

    for page, lines in lines_by_page.items():
        watermarks.append(
            create_watermarks_and_draw(pdf, page, "line", lines)[page - 1]
        )

    result = merge_watermarks_with_pdf(pdf, watermarks)
    watermarks = []
    for page, texts in texts_by_page.items():
        watermarks.append(
            create_watermarks_and_draw(pdf, page, "text", texts)[page - 1]
        )

    return merge_watermarks_with_pdf(result, watermarks)
