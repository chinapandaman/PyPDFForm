# -*- coding: utf-8 -*-
"""Contains helpers for watermark."""

from io import BytesIO
from typing import List, Union

from pypdf import PdfReader, PdfWriter
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen.canvas import Canvas
from reportlab.pdfgen.textobject import PDFTextObject

from .utils import stream_to_io


def translate_and_draw_text(canvas: Canvas, text: Union[str, PDFTextObject], x: float, y: float) -> None:
    """Draws the text on the canvas by centering at the coordinates it should be drawn at."""

    if isinstance(text, str):
        text_obj = canvas.beginText(0, 0)
        text_obj.textLine(text)
    else:
        text_obj = text

    canvas.saveState()
    canvas.translate(x, y)
    canvas.drawText(text_obj)
    canvas.restoreState()


def draw_text(*args) -> None:
    """Draws a text on the watermark."""

    canvas = args[0]
    widget = args[1]
    coordinate_x = args[2]
    coordinate_y = args[3]

    text_to_draw = widget.value

    if not text_to_draw:
        text_to_draw = ""

    if widget.max_length is not None:
        text_to_draw = text_to_draw[: widget.max_length]

    canvas.setFont(widget.font, widget.font_size)
    canvas.setFillColorRGB(
        widget.font_color[0], widget.font_color[1], widget.font_color[2]
    )

    if widget.comb is True:
        for i, char in enumerate(text_to_draw):
            translate_and_draw_text(canvas, char, coordinate_x + widget.character_paddings[i], coordinate_y)
    elif (
        widget.text_wrap_length is None or len(text_to_draw) < widget.text_wrap_length
    ) and widget.text_lines is None:
        translate_and_draw_text(canvas, text_to_draw, coordinate_x, coordinate_y)
    else:
        text_obj = canvas.beginText(0, 0)
        for i, line in enumerate(widget.text_lines):
            cursor_moved = False
            if (
                widget.text_line_x_coordinates is not None
                and widget.text_line_x_coordinates[i] - coordinate_x != 0
            ):
                text_obj.moveCursor(widget.text_line_x_coordinates[i] - coordinate_x, 0)
                cursor_moved = True
            text_obj.textLine(line)
            if cursor_moved:
                text_obj.moveCursor(
                    -1 * (widget.text_line_x_coordinates[i] - coordinate_x), 0
                )

        translate_and_draw_text(canvas, text_obj, coordinate_x, coordinate_y)


def draw_line(*args) -> None:
    """Draws a line on the watermark."""

    canvas = args[0]
    src_x = args[1]
    src_y = args[2]
    dest_x = args[3]
    dest_y = args[4]
    r = args[5]
    g = args[6]
    b = args[7]

    canvas.saveState()
    canvas.setStrokeColorRGB(r, g, b)
    canvas.line(src_x, src_y, dest_x, dest_y)
    canvas.restoreState()


def draw_rect(*args) -> None:
    """Draws a rectangle on the watermark."""

    canvas = args[0]
    x = args[1]
    y = args[2]
    width = args[3]
    height = args[4]

    canvas.rect(x, y, width, height)


def draw_image(*args) -> None:
    """Draws an image on the watermark."""

    canvas = args[0]
    image_stream = args[1]
    coordinate_x = args[2]
    coordinate_y = args[3]
    width = args[4]
    height = args[5]

    image_buff = BytesIO()
    image_buff.write(image_stream)
    image_buff.seek(0)

    canvas.drawImage(
        ImageReader(image_buff),
        coordinate_x,
        coordinate_y,
        width=width,
        height=height,
        mask="auto",
    )

    image_buff.close()


def create_watermarks_and_draw(
    pdf: bytes,
    page_number: int,
    action_type: str,
    actions: List[list],
) -> List[bytes]:
    """Creates a canvas watermark and draw some stuffs on it."""

    pdf_file = PdfReader(stream_to_io(pdf))
    buff = BytesIO()

    canvas = Canvas(
        buff,
        pagesize=(
            float(pdf_file.pages[page_number - 1].mediabox[2]),
            float(pdf_file.pages[page_number - 1].mediabox[3]),
        ),
    )

    if action_type == "image":
        for each in actions:
            draw_image(*([canvas, *each]))
    elif action_type == "text":
        for each in actions:
            draw_text(*([canvas, *each]))
    elif action_type == "line":
        for each in actions:
            draw_line(*([canvas, *each]))
    elif action_type == "rect":
        for each in actions:
            draw_rect(*([canvas, *each]))

    canvas.save()
    buff.seek(0)

    watermark = buff.read()
    buff.close()

    return [
        watermark if i == page_number - 1 else b"" for i in range(len(pdf_file.pages))
    ]


def merge_watermarks_with_pdf(
    pdf: bytes,
    watermarks: list,
) -> bytes:
    """Merges watermarks with PDF."""

    result = BytesIO()
    pdf_file = PdfReader(stream_to_io(pdf))
    output = PdfWriter()

    for i, page in enumerate(pdf_file.pages):
        if watermarks[i]:
            watermark = PdfReader(stream_to_io(watermarks[i]))
            if watermark.pages:
                page.merge_page(watermark.pages[0])
        output.add_page(page)

    output.write(result)
    result.seek(0)
    return result.read()
