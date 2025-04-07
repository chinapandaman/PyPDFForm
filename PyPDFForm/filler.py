# -*- coding: utf-8 -*-
"""Provides core functionality for filling PDF form fields.

This module handles:
- Drawing text, images, borders and other elements onto PDF forms
- Managing widget states and appearances
- Supporting different filling modes (simple vs watermark-based)
- Handling special cases like checkboxes, radio buttons and signatures

The main functions are:
- fill(): Uses watermark technique for complex form filling
- simple_fill(): Directly modifies form fields for simpler cases
"""

from io import BytesIO
from typing import Dict, Tuple, Union, cast

from pypdf import PdfReader, PdfWriter
from pypdf.generic import BooleanObject, DictionaryObject, NameObject

from .constants import (BUTTON_STYLES, DEFAULT_RADIO_STYLE, WIDGET_TYPES,
                        AcroForm, Annots, NeedAppearances, Root, U)
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
from .patterns import (WIDGET_KEY_PATTERNS, simple_flatten_generic,
                       simple_flatten_radio, simple_update_checkbox_value,
                       simple_update_dropdown_value, simple_update_radio_value,
                       simple_update_text_value)
from .template import get_widgets_by_page
from .utils import (checkbox_radio_to_draw, extract_widget_property,
                    stream_to_io)
from .watermark import create_watermarks_and_draw, merge_watermarks_with_pdf


def check_radio_handler(
    widget: dict, middleware: Union[Checkbox, Radio], radio_button_tracker: dict
) -> Tuple[Text, Union[float, int], Union[float, int], bool]:
    """Calculates drawing parameters for checkbox and radio button widgets.

    Args:
        widget: PDF form widget dictionary containing Rect coordinates
        middleware: Checkbox or Radio middleware instance
        radio_button_tracker: Dictionary tracking radio button group states

    Returns:
        Tuple containing:
        - Text: Prepared text object for drawing the symbol
        - float/int: x coordinate for drawing
        - float/int: y coordinate for drawing
        - bool: Whether the symbol needs to be drawn
    """

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
    """Prepares image data for signature and image widgets.

    Args:
        widget: PDF form widget dictionary containing Rect coordinates
        middleware: Signature or Image middleware instance
        images_to_draw: List to append image drawing parameters to

    Returns:
        bool: True if an image needs to be drawn, False otherwise
    """

    stream = middleware.stream
    any_image_to_draw = False
    if stream is not None:
        any_image_to_draw = True
        image_width, image_height = get_image_dimensions(stream)
        x, y, width, height = get_draw_image_coordinates_resolutions(
            widget, middleware.preserve_aspect_ratio, image_width, image_height
        )
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
    """Prepares text field drawing parameters.

    Args:
        widget: PDF form widget dictionary containing Rect and properties
        middleware: Text middleware instance with text properties

    Returns:
        Tuple containing:
        - Text: The text middleware to draw
        - float/int: x coordinate for drawing
        - float/int: y coordinate for drawing
        - bool: Always True for text fields (they always need drawing)
    """

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
    """Prepares border drawing parameters for widgets.

    Args:
        widget: PDF form widget dictionary containing Rect coordinates
        middleware: Any widget middleware instance
        rect_borders_to_draw: List to append rectangle border parameters to
        ellipse_borders_to_draw: List to append ellipse border parameters to
        line_borders_to_draw: List to append line border parameters to
    """

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
        get_draw_border_coordinates(widget, shape)
        + [
            middleware.border_color,
            middleware.background_color,
            middleware.border_width,
            middleware.dash_array,
        ]
    )

    if shape == "line":
        rect_borders_to_draw.append(
            get_draw_border_coordinates(widget, "rect")
            + [None, middleware.background_color, 0, None]
        )


def get_drawn_stream(to_draw: dict, stream: bytes, action: str) -> bytes:
    """Applies drawing operations to a PDF stream.

    Args:
        to_draw: Dictionary mapping page numbers to drawing parameters
        stream: Input PDF as bytes
        action: Type of drawing operation ('text', 'image', 'rect', etc.)

    Returns:
        bytes: Modified PDF with drawings applied
    """

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
    """Fills a PDF form using watermark technique for complex rendering.

    This method:
    - Handles text, images, borders for all widget types
    - Preserves original form fields while adding visual elements
    - Supports complex cases like multiline text and image scaling

    Args:
        template_stream: Input PDF form as bytes
        widgets: Dictionary mapping field names to widget middleware

    Returns:
        bytes: Filled PDF form as bytes
    """

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
            key = extract_widget_property(widget_dict, WIDGET_KEY_PATTERNS, None, str)
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
                    [
                        to_draw,
                        x,
                        y,
                    ]
                )

    result = template_stream
    result = get_drawn_stream(rect_borders_to_draw, result, "rect")
    result = get_drawn_stream(ellipse_borders_to_draw, result, "ellipse")
    result = get_drawn_stream(line_borders_to_draw, result, "line")
    result = get_drawn_stream(texts_to_draw, result, "text")

    if any_image_to_draw:
        result = get_drawn_stream(images_to_draw, result, "image")

    return result


def enable_adobe_mode(pdf: PdfReader, adobe_mode: bool) -> None:
    """Configures PDF for Adobe Acrobat compatibility.

    Args:
        pdf: PdfReader instance of the PDF
        adobe_mode: If True, sets NeedAppearances flag for Acrobat
    """

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
    """Fills a PDF form by directly modifying form fields.

    This method:
    - Updates field values directly in the PDF
    - Supports flattening to make fields read-only
    - Works with Adobe Acrobat compatibility mode

    Args:
        template: Input PDF form as bytes
        widgets: Dictionary mapping field names to widget middleware
        flatten: If True, makes form fields read-only
        adobe_mode: If True, enables Adobe Acrobat compatibility

    Returns:
        bytes: Filled PDF form as bytes
    """

    pdf = PdfReader(stream_to_io(template))
    enable_adobe_mode(pdf, adobe_mode)
    out = PdfWriter()
    out.append(pdf)

    radio_button_tracker = {}

    for page in out.pages:
        for annot in page.get(Annots, []):  # noqa
            annot = cast(DictionaryObject, annot.get_object())
            key = extract_widget_property(
                annot.get_object(), WIDGET_KEY_PATTERNS, None, str
            )

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
