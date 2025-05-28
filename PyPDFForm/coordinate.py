# -*- coding: utf-8 -*-
"""
Module for generating coordinate grids on PDFs.

This module provides functionality to generate coordinate grids on existing PDF documents.
It allows developers to visualize the coordinate system of each page in a PDF, which can be helpful
for debugging and precisely positioning elements when filling or drawing on PDF forms.
"""

from typing import Tuple

from pypdf import PdfReader
from reportlab.pdfbase.pdfmetrics import stringWidth

from .constants import COORDINATE_GRID_FONT_SIZE_MARGIN_RATIO, DEFAULT_FONT
from .middleware.text import Text
from .utils import stream_to_io
from .watermark import create_watermarks_and_draw, merge_watermarks_with_pdf


def generate_coordinate_grid(
    pdf: bytes, color: Tuple[float, float, float], margin: float
) -> bytes:
    """
    Generates a coordinate grid overlay on a PDF document.

    This function takes a PDF file as bytes, along with a color and margin, and generates
    a coordinate grid on each page of the PDF. The grid consists of lines and text indicating
    the X and Y coordinates. This can be useful for visualizing the layout and positioning
    elements on the PDF.

    Args:
        pdf (bytes): The PDF file as bytes.
        color (Tuple[float, float, float]): The color of the grid lines and text as a tuple of RGB values (0.0-1.0).
                                            For example, (0.0, 0.0, 0.0) represents black.
        margin (float): The margin between the grid lines and the edge of the page, in points.
                        This value determines the spacing of the grid.

    Returns:
        bytes: The PDF file with the coordinate grid overlay as bytes.
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

        current = margin
        while current < width:
            lines_by_page[i + 1].append(
                {
                    "src_x": current,
                    "src_y": 0,
                    "dest_x": current,
                    "dest_y": height,
                    "color": color,
                }
            )
            current += margin

        current = margin
        while current < height:
            lines_by_page[i + 1].append(
                {
                    "src_x": 0,
                    "src_y": current,
                    "dest_x": width,
                    "dest_y": current,
                    "color": color,
                }
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
                    {
                        "widget": text,
                        "x": x - stringWidth(value, DEFAULT_FONT, font_size),
                        "y": y - font_size,
                    }
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
