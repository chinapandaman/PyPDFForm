# -*- coding: utf-8 -*-

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
    widget = kwargs["widget"]
    coordinate_x = kwargs["x"]
    coordinate_y = kwargs["y"]

    text_to_draw = widget.value
    canvas.setFont(widget.font, widget.font_size)
    canvas.setFillColorRGB(
        widget.font_color[0], widget.font_color[1], widget.font_color[2]
    )
    canvas.drawString(
        coordinate_x,
        coordinate_y,
        text_to_draw,
    )


def draw_line(canvas: Canvas, **kwargs) -> None:
    src_x = kwargs["src_x"]
    src_y = kwargs["src_y"]
    dest_x = kwargs["dest_x"]
    dest_y = kwargs["dest_y"]
    color = kwargs["color"]

    canvas.setStrokeColorRGB(*(color))
    canvas.line(src_x, src_y, dest_x, dest_y)


def draw_image(canvas: Canvas, **kwargs) -> None:
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
