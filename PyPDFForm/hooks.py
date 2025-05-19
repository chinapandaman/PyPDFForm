# -*- coding: utf-8 -*-
"""Module containing hook functions for PDF form widget manipulation.

This module provides functions to apply various transformations and modifications
to PDF form widgets through a hook system. It allows dynamic modification of
widget properties like font sizes and other attributes.
"""

import sys
from io import BytesIO
from typing import cast

from pypdf import PdfReader, PdfWriter
from pypdf.generic import DictionaryObject, NameObject, TextStringObject

from .constants import DA, FONT_SIZE_IDENTIFIER, Annots, Parent
from .template import get_widget_key
from .utils import stream_to_io


def trigger_widget_hooks(
    pdf: bytes,
    widgets: dict,
    use_full_widget_name: bool,
) -> bytes:
    """Apply all registered widget hooks to a PDF document.

    Args:
        pdf: The input PDF document as bytes
        widgets: Dictionary mapping widget names to widget objects
        use_full_widget_name: Whether to use full widget names including parent hierarchy

    Returns:
        The modified PDF document as bytes

    Note:
        This function processes all pages and annotations in the PDF, applying
        any hooks registered in the widget objects.
    """

    pdf_file = PdfReader(stream_to_io(pdf))
    output = PdfWriter()
    output.append(pdf_file)

    for page in output.pages:
        for annot in page.get(Annots, []):
            annot = cast(DictionaryObject, annot.get_object())
            key = get_widget_key(annot.get_object(), use_full_widget_name)

            widget = widgets.get(key)
            if widget is None or not widget.hooks_to_trigger:
                continue

            for hook in widget.hooks_to_trigger:
                getattr(sys.modules[__name__], hook[0])(annot, hook[1])

            widget.hooks_to_trigger = []

    with BytesIO() as f:
        output.write(f)
        f.seek(0)
        return f.read()


def update_text_field_font_size(annot: DictionaryObject, value: float) -> None:
    """Update the font size of a text field widget.

    Args:
        annot: The PDF annotation (widget) dictionary object
        value: The new font size value to apply

    Note:
        Handles both direct font size specification and inherited font sizes
        from parent objects. Modifies the DA (default appearance) string.
    """

    if Parent in annot and DA not in annot:
        text_appearance = annot[Parent][DA]
    else:
        text_appearance = annot[DA]

    text_appearance = text_appearance.split(" ")
    font_size_index = 0
    for i, val in enumerate(text_appearance):
        if val.startswith(FONT_SIZE_IDENTIFIER):
            font_size_index = i - 1
            break

    text_appearance[font_size_index] = str(value)
    new_text_appearance = " ".join(text_appearance)

    if Parent in annot and DA not in annot:
        annot[NameObject(Parent)][NameObject(DA)] = TextStringObject(
            new_text_appearance
        )
    else:
        annot[NameObject(DA)] = TextStringObject(new_text_appearance)
