# -*- coding: utf-8 -*-

from io import BytesIO
from typing import Dict, Tuple, Union, cast

from pypdf import PdfReader, PdfWriter
from pypdf.generic import (ArrayObject, BooleanObject, DictionaryObject,
                           IndirectObject, NameObject)

from .constants import (BUTTON_STYLES, DEFAULT_RADIO_STYLE, WIDGET_TYPES,
                        AcroForm, Annots, Fields, NeedAppearances, Root, U)
from .coordinate import (get_draw_border_coordinates,
                         get_draw_checkbox_radio_coordinates,
                         get_draw_image_coordinates_resolutions,
                         get_draw_text_coordinates,
                         get_text_line_x_coordinates)
from .font import checkbox_radio_font_size
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
from .template import get_widget_key, get_widgets_by_page
from .utils import checkbox_radio_to_draw, stream_to_io
from .watermark import create_watermarks_and_draw, merge_watermarks_with_pdf


def check_radio_handler(
    widget: dict, middleware: Union[Checkbox, Radio], radio_button_tracker: dict
) -> Tuple[Text, Union[float, int], Union[float, int], bool]:
    font_size = (
        checkbox_radio_font_size(widget) if middleware.size is None else middleware.size
    )
    to_draw = checkbox_radio_to_draw(middleware, font_size)
    x, y = get_draw_checkbox_radio_coordinates(
        widget, to_draw, border_width=middleware.border_width
    )
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


def text_handler(
    widget: dict, middleware: Text
) -> Tuple[Text, Union[float, int], Union[float, int], bool]:
    middleware.text_line_x_coordinates = get_text_line_x_coordinates(widget, middleware)
    x, y = get_draw_text_coordinates(widget, middleware)
    to_draw = middleware
    text_needs_to_be_drawn = True

    return to_draw, x, y, text_needs_to_be_drawn


def border_handler(
    widget: dict,
    middleware: WIDGET_TYPES,
    rect_borders_to_draw: list,
    ellipse_borders_to_draw: list,
    line_borders_to_draw: list,
) -> None:
    if (
        isinstance(middleware, Radio)
        and BUTTON_STYLES.get(middleware.button_style) == DEFAULT_RADIO_STYLE
    ):
        list_to_append = ellipse_borders_to_draw
        shape = "ellipse"
    elif middleware.border_style == U:
        list_to_append = line_borders_to_draw
        shape = "line"
    else:
        list_to_append = rect_borders_to_draw
        shape = "rect"

    list_to_append.append(
        {
            **get_draw_border_coordinates(widget, shape),
            "border_color": middleware.border_color,
            "background_color": middleware.background_color,
            "border_width": middleware.border_width,
            "dash_array": middleware.dash_array,
        }
    )

    if shape == "line":
        rect_borders_to_draw.append(
            {
                **get_draw_border_coordinates(widget, "rect"),
                "border_color": None,
                "background_color": middleware.background_color,
                "border_width": 0,
                "dash_array": None,
            }
        )


def get_drawn_stream(to_draw: dict, stream: bytes, action: str) -> bytes:
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
    use_full_widget_name: bool,
) -> bytes:
    texts_to_draw = {}
    images_to_draw = {}
    rect_borders_to_draw = {}
    ellipse_borders_to_draw = {}
    line_borders_to_draw = {}
    any_image_to_draw = False

    radio_button_tracker = {}

    for page, widget_dicts in get_widgets_by_page(template_stream).items():
        texts_to_draw[page] = []
        images_to_draw[page] = []
        rect_borders_to_draw[page] = []
        ellipse_borders_to_draw[page] = []
        line_borders_to_draw[page] = []
        for widget_dict in widget_dicts:
            key = get_widget_key(widget_dict, use_full_widget_name)
            text_needs_to_be_drawn = False
            to_draw = x = y = None

            if widgets[key].render_widget:
                border_handler(
                    widget_dict,
                    widgets[key],
                    rect_borders_to_draw[page],
                    ellipse_borders_to_draw[page],
                    line_borders_to_draw[page],
                )

            if isinstance(widgets[key], (Checkbox, Radio)):
                to_draw, x, y, text_needs_to_be_drawn = check_radio_handler(
                    widget_dict, widgets[key], radio_button_tracker
                )
            elif isinstance(widgets[key], (Signature, Image)):
                any_image_to_draw |= signature_image_handler(
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
                    {
                        "widget": to_draw,
                        "x": x,
                        "y": y,
                    }
                )

    result = template_stream
    result = get_drawn_stream(rect_borders_to_draw, result, "rect")
    result = get_drawn_stream(ellipse_borders_to_draw, result, "ellipse")
    result = get_drawn_stream(line_borders_to_draw, result, "line")
    result = get_drawn_stream(texts_to_draw, result, "text")

    if any_image_to_draw:
        result = get_drawn_stream(images_to_draw, result, "image")

    return result


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
) -> bytes:
    pdf = PdfReader(stream_to_io(template))
    out = PdfWriter()
    enable_adobe_mode(pdf, out, adobe_mode)
    out.append(pdf)

    radio_button_tracker = {}

    for page in out.pages:
        for annot in page.get(Annots, []):
            annot = cast(DictionaryObject, annot.get_object())
            key = get_widget_key(annot.get_object(), use_full_widget_name)

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
