# -*- coding: utf-8 -*-
"""
Module containing functions to fill PDF forms.

This module provides the core functionality for filling PDF forms programmatically.
It includes functions for handling various form field types, such as text fields,
checkboxes, radio buttons, dropdowns, images, and signatures. The module also
supports flattening the filled form to prevent further modifications.
"""

from io import BytesIO
from typing import Dict, Union, cast

from pypdf import PdfReader, PdfWriter
from pypdf.generic import DictionaryObject

from .constants import WIDGET_TYPES, Annots
from .hooks import flatten_generic, flatten_radio
from .image import get_draw_image_resolutions, get_image_dimensions
from .middleware.checkbox import Checkbox
from .middleware.dropdown import Dropdown
from .middleware.image import Image
from .middleware.radio import Radio
from .middleware.signature import Signature
from .middleware.text import Text
from .patterns import (update_checkbox_value, update_dropdown_value,
                       update_radio_value, update_text_value)
from .template import get_widget_key
from .utils import stream_to_io
from .watermark import create_watermarks_and_draw, merge_watermarks_with_pdf


def signature_image_handler(
    widget: dict, middleware: Union[Signature, Image], images_to_draw: list
) -> bool:
    """Handles signature and image widgets by extracting image data and preparing it for drawing.

    This function processes signature and image widgets found in a PDF form. It extracts the
    image data from the widget's middleware and prepares it for drawing on the form. The
    function calculates the position and dimensions of the image based on the widget's
    properties and the `preserve_aspect_ratio` setting. The image data is then stored in a
    list for later drawing.

    Args:
        widget (dict): The widget dictionary representing the signature or image field.
        middleware (Union[Signature, Image]): The middleware object containing the image data and properties.
        images_to_draw (list): A list to store image data for drawing.

    Returns:
        bool: True if any image is to be drawn, False otherwise.
    """
    stream = middleware.stream
    any_image_to_draw = False
    if stream is not None:
        any_image_to_draw = True
        image_width, image_height = get_image_dimensions(stream)
        x, y, width, height = get_draw_image_resolutions(
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
    """Applies watermarks to specific pages of a PDF based on the provided drawing instructions.

    This function takes a dictionary of drawing instructions and applies watermarks to the
    specified pages of a PDF. It iterates through the drawing instructions, creates watermarks
    for each page, and merges the watermarks with the original PDF content. The function
    supports various drawing actions, such as adding images or text.

    Args:
        to_draw (dict): A dictionary containing page numbers as keys and lists of drawing instructions as values.
                         Each drawing instruction specifies the type of drawing, position, dimensions, and content.
        stream (bytes): The PDF content as bytes.
        action (str): The type of action to perform (e.g., "image", "text").

    Returns:
        bytes: The modified PDF content with watermarks applied.
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
    template: bytes,
    widgets: Dict[str, WIDGET_TYPES],
    need_appearances: bool,
    use_full_widget_name: bool,
    flatten: bool = False,
) -> tuple:
    """Fills a PDF template with the given widgets.

    This function fills a PDF template with the provided widget values. It iterates through the
    widgets on each page of the PDF and updates their values based on the provided `widgets`
    dictionary. The function supports various widget types, including text fields, checkboxes,
    radio buttons, dropdowns, images, and signatures. It also supports flattening the filled
    form to prevent further modifications.

    Args:
        template (bytes): The PDF template as bytes.
        widgets (Dict[str, WIDGET_TYPES]): A dictionary of widgets to fill, where the keys are the
                                            widget names and the values are the widget objects.
        need_appearances (bool): If True, skips updating the appearance stream (AP) for
            text and dropdown fields to maintain compatibility with Adobe Reader's
            behavior for certain fields.
        use_full_widget_name (bool): Whether to use the full widget name when looking up widgets
                                      in the `widgets` dictionary.
        flatten (bool): Whether to flatten the filled PDF. Defaults to False.

    Returns:
        tuple: A tuple containing the filled PDF as bytes and the image drawn stream as bytes, if any.
               The image drawn stream is only returned if there are any image or signature widgets
               in the form.
    """
    pdf = PdfReader(stream_to_io(template))
    out = PdfWriter()
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
            if widget is None:
                continue

            # flatten all
            if flatten:
                (flatten_radio if isinstance(widget, Radio) else flatten_generic)(
                    annot, True
                )
            if widget.value is None:
                continue

            if isinstance(widgets[key], (Signature, Image)):
                any_image_to_draw |= signature_image_handler(
                    annot, widgets[key], images_to_draw[page_num + 1]
                )
            elif type(widget) is Checkbox:
                update_checkbox_value(annot, widget.value)
            elif isinstance(widget, Radio):
                if key not in radio_button_tracker:
                    radio_button_tracker[key] = 0
                radio_button_tracker[key] += 1
                if widget.value == radio_button_tracker[key] - 1:
                    update_radio_value(annot)
            elif isinstance(widget, Dropdown):
                update_dropdown_value(annot, widget, need_appearances)
            elif isinstance(widget, Text):
                update_text_value(annot, widget, need_appearances)

    with BytesIO() as f:
        out.write(f)
        f.seek(0)
        result = f.read()

    return result, (
        get_drawn_stream(images_to_draw, result, "image") if any_image_to_draw else None
    )
