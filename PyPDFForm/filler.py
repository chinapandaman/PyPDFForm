# -*- coding: utf-8 -*-
"""Contains helpers for filling a PDF form."""

from io import BytesIO
from typing import Dict, Tuple, Union, cast

from pypdf import PdfReader, PdfWriter
from pypdf.generic import BooleanObject, DictionaryObject, NameObject

from .constants import WIDGET_TYPES, AcroForm, Annots, NeedAppearances, Root
from .coordinate import (get_draw_checkbox_radio_coordinates,
                         get_draw_image_coordinates_resolutions,
                         get_draw_text_coordinates,
                         get_text_line_x_coordinates)
from .font import checkbox_radio_font_size
from .image import any_image_to_jpg
from .middleware.checkbox import Checkbox
from .middleware.dropdown import Dropdown
from .middleware.pushbutton import Pushbutton
from .middleware.radio import Radio
from .middleware.signature import Signature
from .middleware.text import Text
from .patterns import (simple_flatten_generic, simple_flatten_radio,
                       simple_update_checkbox_value,
                       simple_update_dropdown_value, simple_update_radio_value,
                       simple_update_text_value)
from .template import get_widget_key, get_widgets_by_page
from .utils import checkbox_radio_to_draw, stream_to_io
from .watermark import create_watermarks_and_draw, merge_watermarks_with_pdf


def check_radio_handler(
    widget: dict, middleware: Union[Checkbox, Radio], radio_button_tracker: dict
) -> Tuple[Text, Union[float, int], Union[float, int], bool]:
    """Handles draw parameters for checkbox and radio button widgets."""

    font_size = (
        checkbox_radio_font_size(widget) if middleware.size is None else middleware.size
    )
    to_draw = checkbox_radio_to_draw(middleware, font_size)
    x, y = get_draw_checkbox_radio_coordinates(widget, to_draw)
    text_needs_to_be_drawn = False
    if type(middleware) is Checkbox and middleware.value:
        text_needs_to_be_drawn = True
    elif isinstance(middleware, Radio):
        if middleware.name not in radio_button_tracker:
            radio_button_tracker[middleware.name] = 0
        radio_button_tracker[middleware.name] += 1
        if middleware.value == radio_button_tracker[middleware.name] - 1:
            text_needs_to_be_drawn = True

    return to_draw, x, y, text_needs_to_be_drawn


def signature_image_handler(
    widget: dict, middleware: Union[Signature, Pushbutton], images_to_draw: list
) -> bool:
    """Handles draw parameters for signature and image widgets."""

    stream = middleware.stream
    any_image_to_draw = False
    if stream is not None:
        any_image_to_draw = True
        stream = any_image_to_jpg(stream)
        x, y, width, height = get_draw_image_coordinates_resolutions(widget)
        images_to_draw.append(
            [
                stream,
                x,
                y,
                width,
                height,
            ]
        )

    return any_image_to_draw


def text_handler(
    widget: dict, middleware: Text
) -> Tuple[Text, Union[float, int], Union[float, int], bool]:
    """Handles draw parameters for text field widgets."""

    middleware.text_line_x_coordinates = get_text_line_x_coordinates(widget, middleware)
    x, y = get_draw_text_coordinates(widget, middleware)
    to_draw = middleware
    text_needs_to_be_drawn = True

    return to_draw, x, y, text_needs_to_be_drawn


def get_drawn_stream(to_draw: dict, stream: bytes, action: str) -> bytes:
    """Generates a stream of an input PDF stream with stuff drawn on it."""

    watermark_list = []
    for page, stuffs in to_draw.items():
        watermark_list.append(b"")
        watermarks = create_watermarks_and_draw(stream, page, action, stuffs)
        for i, watermark in enumerate(watermarks):
            if watermark:
                watermark_list[i] = watermark

    return merge_watermarks_with_pdf(stream, watermark_list)


def fill(
    template_stream: bytes,
    widgets: Dict[str, WIDGET_TYPES],
) -> bytes:
    """Fills a PDF using watermarks."""

    texts_to_draw = {}
    images_to_draw = {}
    any_image_to_draw = False

    radio_button_tracker = {}

    for page, widget_dicts in get_widgets_by_page(template_stream).items():
        texts_to_draw[page] = []
        images_to_draw[page] = []
        for widget_dict in widget_dicts:
            key = get_widget_key(widget_dict)
            text_needs_to_be_drawn = False
            to_draw = x = y = None

            if isinstance(widgets[key], (Checkbox, Radio)):
                to_draw, x, y, text_needs_to_be_drawn = check_radio_handler(
                    widget_dict, widgets[key], radio_button_tracker
                )
            elif isinstance(widgets[key], (Signature, Pushbutton)):
                any_image_to_draw = signature_image_handler(
                    widget_dict, widgets[key], images_to_draw[page]
                )
            else:
                to_draw, x, y, text_needs_to_be_drawn = text_handler(
                    widget_dict, widgets[key]
                )

            if all(
                [
                    text_needs_to_be_drawn,
                    to_draw is not None,
                    x is not None,
                    y is not None,
                ]
            ):
                texts_to_draw[page].append(
                    [
                        to_draw,
                        x,
                        y,
                    ]
                )

    result = get_drawn_stream(texts_to_draw, template_stream, "text")

    if any_image_to_draw:
        result = get_drawn_stream(images_to_draw, result, "image")

    return result


def enable_adobe_mode(pdf: PdfReader, adobe_mode: bool) -> None:
    """Enables Adobe mode so that texts filled can show up in Acrobat."""

    if adobe_mode and AcroForm in pdf.trailer[Root]:
        pdf.trailer[Root][AcroForm].update(
            {NameObject(NeedAppearances): BooleanObject(True)}
        )


def simple_fill(
    template: bytes,
    widgets: Dict[str, WIDGET_TYPES],
    flatten: bool = False,
    adobe_mode: bool = False,
) -> bytes:
    """Fills a PDF form in place."""

    pdf = PdfReader(stream_to_io(template))
    enable_adobe_mode(pdf, adobe_mode)
    out = PdfWriter()
    out.append(pdf)

    radio_button_tracker = {}

    for page in out.pages:
        for annot in page.get(Annots, []):  # noqa
            annot = cast(DictionaryObject, annot.get_object())
            key = get_widget_key(annot.get_object())

            widget = widgets.get(key)
            if widget is None or widget.value is None:
                continue

            if type(widget) is Checkbox:
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
        return f.read()
