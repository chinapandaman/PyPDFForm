# -*- coding: utf-8 -*-
"""
Module related to adding watermarks to a PDF.

This module provides functionalities to add watermarks to existing PDF documents.
It supports drawing text, lines, and images as watermarks.
The module also includes functions to merge these watermarks with the original PDF content
and to copy specific widgets from the watermarks to the original PDF.
"""

from collections import defaultdict
from io import BytesIO
from typing import Any, Dict, List, Optional, Union

from pypdf import PageObject, PdfReader, PdfWriter
from pypdf.generic import ArrayObject, NameObject
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen.canvas import Canvas

from .constants import Annots
from .patterns import get_widget_key
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


def draw_rect(canvas: Canvas, **kwargs) -> None:
    """
    Draws a rectangle on the given canvas with the specified coordinates, dimensions, and color.

    Args:
        canvas (Canvas): The ReportLab Canvas object to draw on.
        **kwargs: Keyword arguments containing the rectangle's properties and coordinates.
            - x (float): The x-coordinate of the rectangle's bottom-left corner.
            - y (float): The y-coordinate of the rectangle's bottom-left corner.
            - width (float): The width of the rectangle.
            - height (float): The height of the rectangle.
            - color (tuple): A tuple representing the RGB color of the rectangle's outline.
            - fill_color (tuple): A tuple representing the RGB color of the rectangle's fill.

    Returns:
        None
    """
    x = kwargs["x"]
    y = kwargs["y"]
    width = kwargs["width"]
    height = kwargs["height"]
    color = kwargs["color"]
    fill_color = kwargs["fill_color"]

    canvas.setStrokeColorRGB(*(color))

    fill = 0
    canvas.saveState()
    if fill_color:
        canvas.setFillColorRGB(*(fill_color))
        fill = 1

    canvas.rect(x, y, width, height, fill=fill)
    canvas.restoreState()


def draw_circle(canvas: Canvas, **kwargs) -> None:
    """
    Draws a circle on the given canvas with the specified center coordinates, radius, and color.

    Args:
        canvas (Canvas): The ReportLab Canvas object to draw on.
        **kwargs: Keyword arguments containing the circle's properties and coordinates.
            - center_x (float): The x-coordinate of the circle's center.
            - center_y (float): The y-coordinate of the circle's center.
            - radius (float): The radius of the circle.
            - color (tuple): A tuple representing the RGB color of the circle's outline.
            - fill_color (tuple): A tuple representing the RGB color of the circle's fill.

    Returns:
        None
    """
    center_x = kwargs["center_x"]
    center_y = kwargs["center_y"]
    radius = kwargs["radius"]
    color = kwargs["color"]
    fill_color = kwargs["fill_color"]

    canvas.setStrokeColorRGB(*(color))

    fill = 0
    canvas.saveState()
    if fill_color:
        canvas.setFillColorRGB(*(fill_color))
        fill = 1

    canvas.circle(center_x, center_y, radius, fill=fill)
    canvas.restoreState()


def draw_ellipse(canvas: Canvas, **kwargs) -> None:
    """
    Draws an ellipse on the given canvas defined by its bounding box coordinates and color.

    Args:
        canvas (Canvas): The ReportLab Canvas object to draw on.
        **kwargs: Keyword arguments containing the ellipse's properties and coordinates.
            - x1 (float): The x-coordinate of the first corner of the bounding box.
            - y1 (float): The y-coordinate of the first corner of the bounding box.
            - x2 (float): The x-coordinate of the second corner of the bounding box.
            - y2 (float): The y-coordinate of the second corner of the bounding box.
            - color (tuple): A tuple representing the RGB color of the ellipse's outline.
            - fill_color (tuple): A tuple representing the RGB color of the ellipse's fill.

    Returns:
        None
    """
    x1 = kwargs["x1"]
    y1 = kwargs["y1"]
    x2 = kwargs["x2"]
    y2 = kwargs["y2"]
    color = kwargs["color"]
    fill_color = kwargs["fill_color"]

    canvas.setStrokeColorRGB(*(color))

    fill = 0
    canvas.saveState()
    if fill_color:
        canvas.setFillColorRGB(*(fill_color))
        fill = 1

    canvas.ellipse(x1, y1, x2, y2, fill=fill)
    canvas.restoreState()


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


def create_watermarks_and_draw(pdf: bytes, to_draw: List[dict]) -> List[bytes]:
    """
    Creates a watermark PDF for each page of the input PDF based on the drawing instructions.

    This function reads the input PDF to determine page sizes, then uses ReportLab
    to create a separate, single-page PDF (a watermark) for each page that has
    drawing instructions.

    Args:
        pdf (bytes): The original PDF file as a byte stream.
        to_draw (List[dict]): A list of drawing instructions, where each dictionary
            must contain a "page_number" key (1-based) and a "type" key ("image", "text", or "line")
            along with type-specific parameters.

    Returns:
        List[bytes]: A list of watermark PDF byte streams. An empty byte string (b"")
            is used for pages without any drawing instructions.
    """
    type_to_func = {
        "image": draw_image,
        "text": draw_text,
        "line": draw_line,
        "rect": draw_rect,
        "circle": draw_circle,
        "ellipse": draw_ellipse,
    }

    result = []

    page_to_to_draw = defaultdict(list)
    for each in to_draw:
        page_to_to_draw[each["page_number"]].append(each)

    pdf_file = PdfReader(stream_to_io(pdf))
    buff = BytesIO()

    for i, page in enumerate(pdf_file.pages):
        elements = page_to_to_draw[i + 1]
        if not elements:
            result.append(b"")
            continue

        buff.seek(0)
        buff.flush()

        canvas = Canvas(
            buff,
            pagesize=(
                float(page.mediabox[2]),
                float(page.mediabox[3]),
            ),
        )

        for element in elements:
            type_to_func[element["type"]](canvas, **element)

        canvas.save()
        buff.seek(0)
        result.append(buff.read())

    return result


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
    output.append(pdf_file)

    for i, page in enumerate(output.pages):
        if watermarks[i]:
            watermark = PdfReader(stream_to_io(watermarks[i]))
            if watermark.pages:
                page.merge_page(watermark.pages[0])

    output.write(result)
    result.seek(0)
    return result.read()


def _clone_page_widgets(
    writer: PdfWriter,
    page: PageObject,
    keys: Optional[List[str]],
) -> List[Any]:
    """
    Clones matching widgets from a single PDF page.

    Args:
        writer (PdfWriter): The PdfWriter for cloning.
        page (PageObject): The source PDF page object.
        keys (Optional[List[str]]): Keys of widgets to clone.

    Returns:
        List[Any]: A list of cloned widget objects.
    """
    cloned_widgets = []
    for annot in page.get(Annots, []):
        key = get_widget_key(annot.get_object(), False)
        if keys is None or key in keys:
            cloned_widgets.append(annot.clone(writer))
    return cloned_widgets


def _collect_from_single_watermark_specific_page(
    writer: PdfWriter,
    watermark: bytes,
    keys: Optional[List[str]],
    page_num: int,
) -> Dict[int, List[Any]]:
    """
    Extracts widgets from a specific page of a single watermark PDF.

    Args:
        writer (PdfWriter): The PdfWriter for cloning.
        watermark (bytes): The watermark PDF byte stream.
        keys (Optional[List[str]]): Keys of widgets to clone.
        page_num (int): The page index within the watermark PDF.

    Returns:
        Dict[int, List[Any]]: A dictionary mapping the first output page (index 0) to cloned widgets.
    """
    widgets_to_copy = defaultdict(list)
    watermark_reader = PdfReader(stream_to_io(watermark))
    if page_num < len(watermark_reader.pages):
        widgets_to_copy[0] = _clone_page_widgets(
            writer, watermark_reader.pages[page_num], keys
        )
    return widgets_to_copy


def _collect_from_single_watermark_1_to_1(
    writer: PdfWriter,
    watermark: bytes,
    keys: Optional[List[str]],
) -> Dict[int, List[Any]]:
    """
    Maps pages 1:1 between a single watermark PDF and the output PDF.

    Args:
        writer (PdfWriter): The PdfWriter for cloning.
        watermark (bytes): The watermark PDF byte stream.
        keys (Optional[List[str]]): Keys of widgets to clone.

    Returns:
        Dict[int, List[Any]]: A dictionary mapping output page indices to cloned widgets.
    """
    widgets_to_copy = defaultdict(list)
    watermark_reader = PdfReader(stream_to_io(watermark))
    for i, page in enumerate(watermark_reader.pages):
        widgets_to_copy[i] = _clone_page_widgets(writer, page, keys)
    return widgets_to_copy


def _collect_from_multiple_watermarks(
    writer: PdfWriter,
    watermarks: List[bytes],
    keys: Optional[List[str]],
    page_num: Optional[int],
) -> Dict[int, List[Any]]:
    """
    Collects widgets from a list of watermark PDFs.

    Args:
        writer (PdfWriter): The PdfWriter for cloning.
        watermarks (List[bytes]): A list of watermark PDF byte streams.
        keys (Optional[List[str]]): Keys of widgets to clone.
        page_num (Optional[int]): The page index within each watermark PDF.

    Returns:
        Dict[int, List[Any]]: A dictionary mapping output page indices to cloned widgets.
    """
    widgets_to_copy = defaultdict(list)
    for i, watermark_stream in enumerate(watermarks):
        if not watermark_stream:
            continue
        watermark_reader = PdfReader(stream_to_io(watermark_stream))
        for j, page in enumerate(watermark_reader.pages):
            if page_num is None or j == page_num:
                widgets_to_copy[i].extend(_clone_page_widgets(writer, page, keys))
    return widgets_to_copy


def _collect_widgets_to_copy(
    writer: PdfWriter,
    watermarks: Union[List[bytes], bytes],
    keys: Optional[List[str]],
    page_num: Optional[int],
) -> Dict[int, List[Any]]:
    """
    Identifies and clones widgets from watermarks to be copied.

    Args:
        writer (PdfWriter): The PdfWriter for the output PDF.
        watermarks (Union[List[bytes], bytes]): Watermark(s) to copy from.
        keys (Optional[List[str]]): Keys of widgets to copy.
        page_num (Optional[int]): Specific page index to copy from.

    Returns:
        Dict[int, List[Any]]: A dictionary mapping output page indices to lists of cloned widgets.
    """
    if isinstance(watermarks, bytes):
        if page_num is not None:
            # Case: Single watermark PDF, extracting a specific page to the first output page.
            return _collect_from_single_watermark_specific_page(
                writer, watermarks, keys, page_num
            )
        # Case: Single watermark PDF, mapping pages 1:1 to output pages.
        return _collect_from_single_watermark_1_to_1(writer, watermarks, keys)

    # Case: List of watermark PDFs, each corresponding to an output page.
    return _collect_from_multiple_watermarks(writer, watermarks, keys, page_num)


def _apply_widgets_to_pages(
    out: PdfWriter,
    widgets_to_copy: Dict[int, List[Any]],
) -> None:
    """
    Applies the collected widgets to the corresponding pages in the output PDF.

    Args:
        out (PdfWriter): The PdfWriter object for the output PDF.
        widgets_to_copy (Dict[int, List[Any]]): A dictionary mapping page indices to lists of widgets.

    Returns:
        None
    """
    for i, page in enumerate(out.pages):
        if i in widgets_to_copy:
            page[NameObject(Annots)] = (
                (page[NameObject(Annots)] + ArrayObject(widgets_to_copy[i]))
                if Annots in page
                else ArrayObject(widgets_to_copy[i])
            )


def copy_watermark_widgets(
    pdf: bytes,
    watermarks: Union[List[bytes], bytes],
    keys: Optional[List[str]],
    page_num: Optional[int],
) -> bytes:
    """
    Copies specific widgets from the watermarks to the original PDF.

    This function selectively copies widgets (e.g., form fields) from watermark PDFs
    to the original PDF. It handles both a single watermark PDF (which can be mapped
    1:1 or have a specific page extracted) and a list of watermark PDFs (where each
    element corresponds to a page in the original PDF).

    Args:
        pdf (bytes): The original PDF file as a byte stream.
        watermarks (Union[List[bytes], bytes]): Either a single PDF byte stream or
            a list of PDF byte streams.
        keys (Optional[List[str]]): A list of widget keys to copy. If None,
            all widgets are copied.
        page_num (Optional[int]): The page number index (0-based) within the
            watermark(s) to copy from. If None, all pages are considered.

    Returns:
        bytes: The modified PDF byte stream with copied widgets.
    """
    pdf_writer = PdfWriter()
    pdf_writer.append(PdfReader(stream_to_io(pdf)))

    widgets_to_copy = _collect_widgets_to_copy(pdf_writer, watermarks, keys, page_num)
    _apply_widgets_to_pages(pdf_writer, widgets_to_copy)

    with BytesIO() as f:
        pdf_writer.write(f)
        f.seek(0)
        return f.read()
