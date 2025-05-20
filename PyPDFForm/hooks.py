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
from pypdf.generic import (ArrayObject, DictionaryObject, FloatObject,
                           NameObject, NumberObject, TextStringObject)

from .constants import (COMB, DA, FONT_COLOR_IDENTIFIER, FONT_SIZE_IDENTIFIER,
                        MULTILINE, Annots, Ff, Parent, Q, Rect)
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

    for widget in widgets.values():
        widget.hooks_to_trigger = []

    with BytesIO() as f:
        output.write(f)
        f.seek(0)
        return f.read()


def update_text_field_font_size(annot: DictionaryObject, val: float) -> None:
    """Update the font size of a text field widget.

    Args:
        annot: The PDF annotation (widget) dictionary object
        val: The new font size value to apply

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
    for i, value in enumerate(text_appearance):
        if value.startswith(FONT_SIZE_IDENTIFIER):
            font_size_index = i - 1
            break

    text_appearance[font_size_index] = str(val)
    new_text_appearance = " ".join(text_appearance)

    if Parent in annot and DA not in annot:
        annot[NameObject(Parent)][NameObject(DA)] = TextStringObject(
            new_text_appearance
        )
    else:
        annot[NameObject(DA)] = TextStringObject(new_text_appearance)


def update_text_field_font_color(annot: DictionaryObject, val: tuple) -> None:
    if Parent in annot and DA not in annot:
        text_appearance = annot[Parent][DA]
    else:
        text_appearance = annot[DA]

    text_appearance = text_appearance.split(" ")
    font_size_identifier_index = 0
    for i, value in enumerate(text_appearance):
        if value == FONT_SIZE_IDENTIFIER:
            font_size_identifier_index = i
            break

    new_text_appearance = (
        text_appearance[:font_size_identifier_index]
        + [FONT_SIZE_IDENTIFIER]
        + list(str(each) for each in val)
    )
    new_text_appearance = " ".join(new_text_appearance) + FONT_COLOR_IDENTIFIER

    if Parent in annot and DA not in annot:
        annot[NameObject(Parent)][NameObject(DA)] = TextStringObject(
            new_text_appearance
        )
    else:
        annot[NameObject(DA)] = TextStringObject(new_text_appearance)


def update_text_field_alignment(annot: DictionaryObject, val: int) -> None:
    """Update text alignment for text field annotations.

    Modifies the alignment (Q) field of a text field annotation to set the
    specified text alignment.

    Args:
        annot: PDF text field annotation dictionary to modify
        val: Alignment value to set (typically 0=left, 1=center, 2=right)
    """

    annot[NameObject(Q)] = NumberObject(val)


def update_text_field_multiline(annot: DictionaryObject, val: bool) -> None:
    """Update multiline flag for text field annotations.

    Modifies the field flags (Ff) of a text field annotation to set or
    clear the multiline flag based on the input value.

    Args:
        annot: PDF text field annotation dictionary to modify
        val: Whether to enable multiline (True) or disable (False)
    """

    if val:
        annot[NameObject(Ff)] = NumberObject(int(annot[NameObject(Ff)]) | MULTILINE)


def update_text_field_comb(annot: DictionaryObject, val: bool) -> None:
    """Update comb formatting flag for text field annotations.

    Modifies the field flags (Ff) of a text field annotation to set or
    clear the comb flag which enables/disables comb formatting.

    Args:
        annot: PDF text field annotation dictionary to modify
        val: Whether to enable comb formatting (True) or disable (False)
    """

    if val:
        annot[NameObject(Ff)] = NumberObject(int(annot[NameObject(Ff)]) | COMB)


def update_check_radio_size(annot: DictionaryObject, val: float) -> None:
    """Update the size of a checkbox or radio button widget while maintaining center position.

    Args:
        annot: PDF annotation dictionary containing the widget to modify
        val: New size value (width and height) for the widget

    Note:
        The widget will be resized symmetrically around its center point,
        maintaining the same center position while changing its dimensions.
    """

    rect = annot[Rect]
    center_x = (rect[0] + rect[2]) / 2
    center_y = (rect[1] + rect[3]) / 2
    new_rect = [
        FloatObject(center_x - val / 2),
        FloatObject(center_y - val / 2),
        FloatObject(center_x + val / 2),
        FloatObject(center_y + val / 2),
    ]
    annot[NameObject(Rect)] = ArrayObject(new_rect)


# TODO: remove this and switch to hooks
NON_ACRO_FORM_PARAM_TO_FUNC = {
    ("TextWidget", "alignment"): update_text_field_alignment,
    ("TextWidget", "multiline"): update_text_field_multiline,
    ("TextWidget", "comb"): update_text_field_comb,
}
