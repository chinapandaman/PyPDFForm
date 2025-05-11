# -*- coding: utf-8 -*-
"""Provides watermark generation, annotation copying, and merging functionality for PDF forms.

This module handles:
- Drawing text, images, shapes, and lines onto PDF watermarks
- Managing watermark styles and properties
- Merging watermarks with PDF documents
- Copying annotation widgets (form fields) from watermark PDFs onto base PDFs
- Supporting various drawing operations needed for form filling
"""

from io import BytesIO
from typing import List, Union

from pypdf import PdfReader, PdfWriter
from pypdf.generic import ArrayObject, NameObject
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen.canvas import Canvas

from .constants import Annots
from .template import get_widget_key
from .utils import stream_to_io


def draw_text(canvas: Canvas, **kwargs) -> None:
    """Draws text onto a watermark canvas with proper formatting.

    Handles:
    - Comb fields (fixed character spacing)
    - Multiline text with wrapping
    - Font and color styling
    - Text alignment

    Args:
        canvas: Canvas object to draw on
        **kwargs: Additional arguments including:
            widget: Text widget with content and properties
            x: X coordinate for drawing
            y: Y coordinate for drawing
    """

    widget = kwargs["widget"]
    coordinate_x = kwargs["x"]
    coordinate_y = kwargs["y"]

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
            canvas.drawString(
                coordinate_x + widget.character_paddings[i],
                coordinate_y,
                char,
            )
    elif (
        widget.text_wrap_length is None or len(text_to_draw) < widget.text_wrap_length
    ) and widget.text_lines is None:
        canvas.drawString(
            coordinate_x,
            coordinate_y,
            text_to_draw,
        )
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

        canvas.saveState()
        canvas.translate(
            coordinate_x,
            coordinate_y,
        )
        canvas.drawText(text_obj)
        canvas.restoreState()


def draw_rect(canvas: Canvas, **kwargs) -> None:
    """Draws a rectangle onto a watermark canvas.

    Args:
        canvas: Canvas object to draw on
        **kwargs: Additional arguments including:
            x: X coordinate of bottom-left corner
            y: Y coordinate of bottom-left corner
            width: Width of rectangle
            height: Height of rectangle
            border_color: Border color
            background_color: Background color
            border_width: Border width
            dash_array: Dash pattern for border
    """

    x = kwargs["x"]
    y = kwargs["y"]
    width = kwargs["width"]
    height = kwargs["height"]

    canvas.saveState()
    stroke, fill = set_border_and_background_styles(canvas, **kwargs)
    canvas.rect(x, y, width, height, stroke=stroke, fill=fill)
    canvas.restoreState()


def draw_ellipse(canvas: Canvas, **kwargs) -> None:
    """Draws an ellipse onto a watermark canvas.

    Args:
        canvas: Canvas object to draw on
        **kwargs: Additional arguments including:
            x1: X coordinate of first bounding point
            y1: Y coordinate of first bounding point
            x2: X coordinate of second bounding point
            y2: Y coordinate of second bounding point
            border_color: Border color
            background_color: Background color
            border_width: Border width
            dash_array: Dash pattern for border
    """

    x1 = kwargs["x1"]
    y1 = kwargs["y1"]
    x2 = kwargs["x2"]
    y2 = kwargs["y2"]

    canvas.saveState()
    stroke, fill = set_border_and_background_styles(canvas, **kwargs)
    canvas.ellipse(x1, y1, x2, y2, stroke=stroke, fill=fill)
    canvas.restoreState()


def draw_line(canvas: Canvas, **kwargs) -> None:
    """Draws a line onto a watermark canvas.

    Args:
        canvas: Canvas object to draw on
        **kwargs: Additional arguments including:
            src_x: X coordinate of start point
            src_y: Y coordinate of start point
            dest_x: X coordinate of end point
            dest_y: Y coordinate of end point
            border_color: Line color
            border_width: Line width
            dash_array: Dash pattern for line
    """

    src_x = kwargs["src_x"]
    src_y = kwargs["src_y"]
    dest_x = kwargs["dest_x"]
    dest_y = kwargs["dest_y"]

    canvas.saveState()
    set_border_and_background_styles(canvas, **kwargs)
    canvas.line(src_x, src_y, dest_x, dest_y)
    canvas.restoreState()


def set_border_and_background_styles(canvas: Canvas, **kwargs) -> tuple:
    """Configures stroke and fill styles for drawing operations.

    Args:
        canvas: Canvas object to configure
        **kwargs: Additional arguments including:
            border_color: Border color
            background_color: Background color
            border_width: Border width
            dash_array: Dash pattern for border

    Returns:
        tuple: (stroke_flag, fill_flag) indicating which styles were set
    """

    border_color = kwargs["border_color"]
    background_color = kwargs["background_color"]
    border_width = kwargs["border_width"]
    dash_array = kwargs["dash_array"]

    stroke = 0
    fill = 0
    if border_color is not None and border_width:
        canvas.setStrokeColor(border_color)
        canvas.setLineWidth(border_width)
        stroke = 1
    if background_color is not None:
        canvas.setFillColor(background_color)
        fill = 1

    if dash_array is not None:
        canvas.setDash(array=dash_array)

    return stroke, fill


def draw_image(canvas: Canvas, **kwargs) -> None:
    """Draws an image onto a watermark canvas.

    Args:
        canvas: Canvas object to draw on
        **kwargs: Additional arguments including:
            stream: Image data as bytes
            x: X coordinate for drawing
            y: Y coordinate for drawing
            width: Width of drawn image
            height: Height of drawn image
    """

    image_stream = kwargs["stream"]
    coordinate_x = kwargs["x"]
    coordinate_y = kwargs["y"]
    width = kwargs["width"]
    height = kwargs["height"]

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
    actions: List[dict],
) -> List[bytes]:
    """Creates watermarks for each page with specified drawing operations.

    Args:
        pdf: PDF document as bytes
        page_number: Page number to create watermark for (1-based)
        action_type: Type of drawing operation ('text', 'image', 'line', etc.)
        actions: List of drawing operations to perform

    Returns:
        List[bytes]: Watermark data for each page (empty for non-target pages)
    """

    pdf_file = PdfReader(stream_to_io(pdf))
    buff = BytesIO()

    canvas = Canvas(
        buff,
        pagesize=(
            float(pdf_file.pages[page_number - 1].mediabox[2]),
            float(pdf_file.pages[page_number - 1].mediabox[3]),
        ),
    )

    action_type_to_func = {
        "image": draw_image,
        "text": draw_text,
        "line": draw_line,
        "rect": draw_rect,
        "ellipse": draw_ellipse,
    }

    if action_type_to_func.get(action_type):
        for each in actions:
            action_type_to_func[action_type](canvas, **each)

    canvas.save()
    buff.seek(0)

    watermark = buff.read()
    buff.close()

    return [
        watermark if i == page_number - 1 else b"" for i in range(len(pdf_file.pages))
    ]


def merge_watermarks_with_pdf(
    pdf: bytes,
    watermarks: List[bytes],
) -> bytes:
    """Combines watermarks with their corresponding PDF pages.

    Args:
        pdf: Original PDF document as bytes
        watermarks: List of watermark data for each page

    Returns:
        bytes: Merged PDF document with watermarks applied
    """

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


def copy_watermark_widgets(
    pdf: bytes,
    watermarks: Union[List[bytes], bytes],
    keys: Union[List[str], None],
    page_num: Union[int, None],
) -> bytes:
    """Copies annotation widgets (form fields) from watermark PDFs onto the corresponding pages of a base PDF.

    This function selectively copies annotation widgets (form fields) from watermark PDFs to a base PDF.
    It allows specifying which widgets to copy based on their keys, and optionally restricts the operation
    to a specific page number.

    The function can handle either a list of watermarks (one per page) or a single watermark PDF applied to all pages.
    Widgets are only copied if their key is present in the provided keys list.

    Args:
        pdf: The original PDF document as bytes.
        watermarks: Either a list of watermark PDF data (as bytes, one per page) or a single watermark PDF as bytes.
                   Empty or None entries are skipped.
        keys: List of widget keys (str). Only widgets whose key is in this list will be copied.
              If None, all widgets will be copied.
        page_num: Optional page number (0-based) to restrict widget copying to. If None, widgets are copied
                  across all pages.

    Returns:
        bytes: The resulting PDF document with selected annotation widgets from watermarks copied onto their respective pages.
    """

    pdf_file = PdfReader(stream_to_io(pdf))
    out = PdfWriter()
    out.append(pdf_file)

    widgets_to_copy_watermarks = {}
    widgets_to_copy_pdf = {}

    widgets_to_copy = widgets_to_copy_watermarks
    if isinstance(watermarks, bytes):
        watermarks = [watermarks]
        widgets_to_copy = widgets_to_copy_pdf

    if page_num is not None:
        widgets_to_copy = widgets_to_copy_watermarks

    for i, watermark in enumerate(watermarks):
        if not watermark:
            continue

        widgets_to_copy_watermarks[i] = []
        watermark_file = PdfReader(stream_to_io(watermark))
        for j, page in enumerate(watermark_file.pages):
            widgets_to_copy_pdf[j] = []
            for annot in page.get(Annots, []):
                key = get_widget_key(annot.get_object(), False)
                if (keys is None or key in keys) and (
                    page_num is None or page_num == j
                ):
                    widgets_to_copy_watermarks[i].append(annot.clone(out))
                    widgets_to_copy_pdf[j].append(annot.clone(out))

    for i, page in enumerate(out.pages):
        if i in widgets_to_copy:
            page[NameObject(Annots)] = (
                (page[NameObject(Annots)] + ArrayObject(widgets_to_copy[i]))
                if Annots in page
                else ArrayObject(widgets_to_copy[i])
            )

    with BytesIO() as f:
        out.write(f)
        f.seek(0)
        return f.read()
