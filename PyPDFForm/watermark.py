# -*- coding: utf-8 -*-
"""
Module related to adding watermarks to a PDF.

This module provides functionalities to add watermarks to existing PDF documents.
It supports drawing text, lines, and images as watermarks.
The module also includes functions to merge these watermarks with the original PDF content
and to copy specific widgets from the watermarks to the original PDF.
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
    """
    Draws a text string on the given canvas using the specified font, size, and color.
    Supports multiline text by splitting the input string by newline characters.

    Args:
        canvas (Canvas): The ReportLab Canvas object to draw on.
        **kwargs: Keyword arguments containing the text's properties and coordinates.
            - widget: The widget object containing font, font_size, font_color, and value.
            - x (float): The x-coordinate of the text's starting point.
            - y (float): The y-coordinate of the text's starting point.

    Returns:
        None
    """
    widget = kwargs["widget"]
    coordinate_x = kwargs["x"]
    coordinate_y = kwargs["y"]

    text_to_draw = widget.value
    canvas.setFont(widget.font, widget.font_size)
    canvas.setFillColorRGB(
        widget.font_color[0], widget.font_color[1], widget.font_color[2]
    )
    text_obj = canvas.beginText(coordinate_x, coordinate_y)
    for line in text_to_draw.split("\n"):
        text_obj.textLine(line)
    canvas.drawText(text_obj)


def draw_line(canvas: Canvas, **kwargs) -> None:
    """
    Draws a line on the given canvas with the specified source and destination coordinates, and color.

    Args:
        canvas (Canvas): The ReportLab Canvas object to draw on.
        **kwargs: Keyword arguments containing the line's properties and coordinates.
            - src_x (float): The x-coordinate of the line's starting point.
            - src_y (float): The y-coordinate of the line's starting point.
            - dest_x (float): The x-coordinate of the line's ending point.
            - dest_y (float): The y-coordinate of the line's ending point.
            - color (tuple): A tuple representing the RGB color of the line.

    Returns:
        None
    """
    src_x = kwargs["src_x"]
    src_y = kwargs["src_y"]
    dest_x = kwargs["dest_x"]
    dest_y = kwargs["dest_y"]
    color = kwargs["color"]

    canvas.setStrokeColorRGB(*(color))
    canvas.line(src_x, src_y, dest_x, dest_y)


def draw_image(canvas: Canvas, **kwargs) -> None:
    """
    Draws an image on the given canvas, scaling it to fit within the specified width and height.

    Args:
        canvas (Canvas): The ReportLab Canvas object to draw on.
        **kwargs: Keyword arguments containing the image's properties and coordinates.
            - stream (bytes): The image data as a byte stream.
            - x (float): The x-coordinate of the image's bottom-left corner.
            - y (float): The y-coordinate of the image's bottom-left corner.
            - width (float): The desired width of the image.
            - height (float): The desired height of the image.

    Returns:
        None
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
    """
    Creates watermarks for a specific page in the PDF based on the provided actions and draws them.

    This function takes a PDF file, a page number, an action type, and a list of actions as input.
    It then creates a watermark for the specified page by drawing the specified actions on a Canvas object.

    Args:
        pdf (bytes): The PDF file as a byte stream.
        page_number (int): The page number to which the watermark should be applied (1-indexed).
        action_type (str): The type of action to perform when creating the watermark (e.g., "image", "text", "line").
        actions (List[dict]): A list of dictionaries, where each dictionary represents an action to be performed on the watermark.

    Returns:
        List[bytes]: A list of byte streams, where the element at index (page_number - 1) contains the watermark for the specified page,
                     and all other elements are empty byte streams.
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
    """
    Merges the generated watermarks with the original PDF content.

    This function takes a PDF file and a list of watermarks as input.
    It then merges each watermark with its corresponding page in the PDF.

    Args:
        pdf (bytes): The PDF file as a byte stream.
        watermarks (List[bytes]): A list of byte streams, where each element represents the watermark for a specific page.

    Returns:
        bytes: A byte stream representing the merged PDF with watermarks applied.
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
    """
    Copies specific widgets from the watermarks to the original PDF.

    This function allows you to selectively copy widgets (e.g., form fields) from the watermarks to the original PDF.
    You can specify which widgets to copy by providing a list of keys.

    Args:
        pdf (bytes): The PDF file as a byte stream.
        watermarks (Union[List[bytes], bytes]): A list of byte streams, where each element represents the watermark for a specific page.
        keys (Union[List[str], None]): A list of keys identifying the widgets to copy from the watermarks. If None, all widgets are copied.
        page_num (Union[int, None]): The page number to copy the widgets from. If None, widgets are copied from all pages.

    Returns:
        bytes: A byte stream representing the modified PDF with the specified widgets copied from the watermarks.
    """
    pdf_file = PdfReader(stream_to_io(pdf))
    out = PdfWriter()
    out.append(pdf_file)

    # TODO: refactor duplicate logic with merge_two_pdfs
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

                # cannot be watermarks when page_num not None
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
