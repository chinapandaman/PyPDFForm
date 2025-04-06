# -*- coding: utf-8 -*-
"""Provides coordinate calculation utilities for PDF form elements.

This module contains functions for calculating positions and dimensions
for drawing various PDF form elements including:
- Text fields and paragraphs
- Checkboxes and radio buttons
- Images and signatures
- Borders and decorative elements

All calculations work in PDF coordinate space where:
- Origin (0,0) is at bottom-left corner
- Units are in PDF points (1/72 inch)
"""

from copy import deepcopy
from typing import List, Tuple, Union

from pypdf import PdfReader
from reportlab.pdfbase.pdfmetrics import stringWidth

from .constants import (COORDINATE_GRID_FONT_SIZE_MARGIN_RATIO, DEFAULT_FONT,
                        Rect)
from .middleware.text import Text
from .patterns import WIDGET_ALIGNMENT_PATTERNS
from .template import get_char_rect_width, is_text_multiline
from .utils import extract_widget_property, handle_color, stream_to_io
from .watermark import create_watermarks_and_draw, merge_watermarks_with_pdf


def get_draw_border_coordinates(widget: dict, shape: str) -> List[float]:
    """Calculates coordinates for drawing widget borders.

    Args:
        widget: PDF form widget dictionary containing Rect coordinates
        shape: Type of border to draw ("rectangle", "ellipse" or "line")

    Returns:
        List[float]: Coordinates in format [x1, y1, x2, y2] for the border
            For ellipses: [center_x, center_y, radius_x, radius_y]
            For lines: [x1, y1, x2, y2] endpoints
    """

    result = [
        float(widget[Rect][0]),
        float(widget[Rect][1]),
        abs(float(widget[Rect][0]) - float(widget[Rect][2])),
        abs(float(widget[Rect][1]) - float(widget[Rect][3])),
    ]

    if shape == "ellipse":
        width = abs(float(widget[Rect][0]) - float(widget[Rect][2]))
        height = abs(float(widget[Rect][1]) - float(widget[Rect][3]))

        width_mid = (float(widget[Rect][0]) + float(widget[Rect][2])) / 2
        height_mid = (float(widget[Rect][1]) + float(widget[Rect][3])) / 2

        less = min(width, height)

        result = [
            width_mid - less / 2,
            height_mid - less / 2,
            width_mid + less / 2,
            height_mid + less / 2,
        ]
    elif shape == "line":
        result = [
            float(widget[Rect][0]),
            float(widget[Rect][1]),
            float(widget[Rect][2]),
            float(widget[Rect][1]),
        ]

    return result


def get_draw_checkbox_radio_coordinates(
    widget: dict,
    widget_middleware: Text,
    border_width: int,
) -> Tuple[Union[float, int], Union[float, int]]:
    """Calculates drawing coordinates for checkbox/radio button symbols.

    Args:
        widget: PDF form widget dictionary containing Rect coordinates
        widget_middleware: Text middleware containing font properties
        border_width: Width of widget border in points

    Returns:
        Tuple[Union[float, int], Union[float, int]]: (x, y) coordinates
            for drawing the checkbox/radio symbol
    """

    string_height = widget_middleware.font_size * 72 / 96
    width_mid_point = (float(widget[Rect][0]) + float(widget[Rect][2])) / 2
    half_widget_height = abs(float(widget[Rect][1]) - float(widget[Rect][3])) / 2

    return (
        width_mid_point
        - stringWidth(
            widget_middleware.value,
            widget_middleware.font,
            widget_middleware.font_size,
        )
        / 2,
        float(widget[Rect][1])
        + (half_widget_height - string_height / 2)
        + border_width / 2,
    )


def get_draw_image_coordinates_resolutions(
    widget: dict,
    preserve_aspect_ratio: bool,
    image_width: float,
    image_height: float,
) -> Tuple[float, float, float, float]:
    """Calculates image drawing coordinates and scaling factors.

    Args:
        widget: PDF form widget dictionary containing Rect coordinates
        preserve_aspect_ratio: Whether to maintain image proportions
        image_width: Original width of the image in points
        image_height: Original height of the image in points

    Returns:
        Tuple[float, float, float, float]: (x, y, width, height) where:
            x,y: Bottom-left corner coordinates
            width,height: Scaled dimensions for drawing
    """

    x = float(widget[Rect][0])
    y = float(widget[Rect][1])
    width = abs(float(widget[Rect][0]) - float(widget[Rect][2]))
    height = abs(float(widget[Rect][1]) - float(widget[Rect][3]))

    if preserve_aspect_ratio:
        ratio = max(image_width / width, image_height / height)

        new_width = image_width / ratio
        new_height = image_height / ratio

        x += abs(new_width - width) / 2
        y += abs(new_height - height) / 2

        width = new_width
        height = new_height

    return x, y, width, height


def get_draw_text_coordinates(
    widget: dict, widget_middleware: Text
) -> Tuple[Union[float, int], Union[float, int]]:
    """Calculates text drawing coordinates within a PDF form field.

    Args:
        widget: PDF form widget dictionary containing Rect and alignment
        widget_middleware: Text middleware containing text properties

    Returns:
        Tuple[Union[float, int], Union[float, int]]: (x, y) coordinates
            for drawing the text baseline
    """

    if widget_middleware.preview:
        return (
            float(widget[Rect][0]),
            float(widget[Rect][3]) + 5,
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

    alignment = (
        extract_widget_property(widget, WIDGET_ALIGNMENT_PATTERNS, None, int) or 0
    )
    x = float(widget[Rect][0])

    if int(alignment) != 0:
        width_mid_point = (float(widget[Rect][0]) + float(widget[Rect][2])) / 2
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
            x = float(widget[Rect][2]) - string_width
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
    height_mid_point = (float(widget[Rect][1]) + float(widget[Rect][3])) / 2
    y = (height_mid_point - string_height / 2 + height_mid_point) / 2
    if is_text_multiline(widget):
        y = float(widget[Rect][3]) - string_height / 1.5

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
    """Calculates x-coordinates for each line in a multiline text field.

    Args:
        widget: PDF form widget dictionary
        widget_middleware: Text middleware with text_lines property

    Returns:
        Union[List[float], None]: List of x-coordinates for each text line,
            or None if not a multiline field
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
    """Generates a coordinate grid overlay for a PDF document.

    Args:
        pdf: Input PDF document as bytes
        color: RGB tuple (0-1 range) for grid line color
        margin: Spacing between grid lines in PDF points

    Returns:
        bytes: New PDF with grid overlay as byte stream
    """

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
            lines_by_page[i + 1].append(
                [current, 0, current, height, handle_color([r, g, b]), None, 1, None]
            )
            current += margin

        current = margin
        while current < height:
            lines_by_page[i + 1].append(
                [0, current, width, current, handle_color([r, g, b]), None, 1, None]
            )
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
