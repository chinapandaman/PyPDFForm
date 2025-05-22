# -*- coding: utf-8 -*-

from io import BytesIO
from typing import Dict, Union, cast

from pypdf import PdfReader, PdfWriter
from pypdf.generic import (ArrayObject, BooleanObject, DictionaryObject,
                           IndirectObject, NameObject)

from .constants import (WIDGET_TYPES, AcroForm, Annots, Fields,
                        NeedAppearances, Root)
from .coordinate import get_draw_image_coordinates_resolutions
from .image import get_image_dimensions
from .middleware.checkbox import Checkbox
from .middleware.dropdown import Dropdown
from .middleware.image import Image
from .middleware.radio import Radio
from .middleware.signature import Signature
from .middleware.text import Text
from .patterns import (simple_flatten_generic, simple_flatten_radio,
                       simple_update_checkbox_value,
                       simple_update_dropdown_value, simple_update_radio_value,
                       simple_update_text_value)
from .template import get_widget_key
from .utils import stream_to_io
from .watermark import create_watermarks_and_draw, merge_watermarks_with_pdf


def signature_image_handler(
    widget: dict, middleware: Union[Signature, Image], images_to_draw: list
) -> bool:
    stream = middleware.stream
    any_image_to_draw = False
    if stream is not None:
        any_image_to_draw = True
        image_width, image_height = get_image_dimensions(stream)
        x, y, width, height = get_draw_image_coordinates_resolutions(
            widget, middleware.preserve_aspect_ratio, image_width, image_height
        )
        images_to_draw.append(
            {
                "stream": stream,
                "x": x,
                "y": y,
                "width": width,
                "height": height,
            }
        )

    return any_image_to_draw


def get_drawn_stream(to_draw: dict, stream: bytes, action: str) -> bytes:
    watermark_list = []
    for page, stuffs in to_draw.items():
        watermark_list.append(b"")
        watermarks = create_watermarks_and_draw(stream, page, action, stuffs)
        for i, watermark in enumerate(watermarks):
            if watermark:
                watermark_list[i] = watermark

    return merge_watermarks_with_pdf(stream, watermark_list)


def enable_adobe_mode(reader: PdfReader, writer: PdfWriter, adobe_mode: bool) -> None:
    if not adobe_mode:
        return

    # https://stackoverflow.com/questions/47288578/pdf-form-filled-with-pypdf2-does-not-show-in-print
    if AcroForm in reader.trailer[Root]:
        reader.trailer[Root][AcroForm].update(
            {NameObject(NeedAppearances): BooleanObject(True)}
        )

    if AcroForm not in writer.root_object:
        writer.root_object.update(
            {NameObject(AcroForm): IndirectObject(len(writer.root_object), 0, writer)}
        )
    writer.root_object[AcroForm][NameObject(NeedAppearances)] = BooleanObject(True)
    writer.root_object[AcroForm][NameObject(Fields)] = ArrayObject()


def simple_fill(
    template: bytes,
    widgets: Dict[str, WIDGET_TYPES],
    use_full_widget_name: bool,
    flatten: bool = False,
    adobe_mode: bool = False,
) -> tuple:
    # pylint: disable=R0912
    pdf = PdfReader(stream_to_io(template))
    out = PdfWriter()
    enable_adobe_mode(pdf, out, adobe_mode)
    out.append(pdf)

    radio_button_tracker = {}
    images_to_draw = {}
    any_image_to_draw = False

    for page_num, page in enumerate(out.pages):
        images_to_draw[page_num + 1] = []
        for annot in page.get(Annots, []):
            annot = cast(DictionaryObject, annot.get_object())
            key = get_widget_key(annot.get_object(), use_full_widget_name)

            widget = widgets.get(key)
            if widget is None or widget.value is None:
                continue

            if isinstance(widgets[key], (Signature, Image)):
                any_image_to_draw |= signature_image_handler(
                    annot, widgets[key], images_to_draw[page_num + 1]
                )
            elif type(widget) is Checkbox:
                simple_update_checkbox_value(annot, widget.value)
            elif isinstance(widget, Radio):
                if key not in radio_button_tracker:
                    radio_button_tracker[key] = 0
                radio_button_tracker[key] += 1
                if widget.value == radio_button_tracker[key] - 1:
                    simple_update_radio_value(annot)
            elif isinstance(widget, Dropdown):
                simple_update_dropdown_value(annot, widget)
            elif isinstance(widget, Text):
                simple_update_text_value(annot, widget)

            if flatten:
                if isinstance(widget, Radio):
                    simple_flatten_radio(annot)
                else:
                    simple_flatten_generic(annot)

    with BytesIO() as f:
        out.write(f)
        f.seek(0)
        result = f.read()

    image_drawn_stream = None
    if any_image_to_draw:
        image_drawn_stream = get_drawn_stream(images_to_draw, result, "image")

    return result, image_drawn_stream
