# -*- coding: utf-8 -*-
"""Module related to widget hooks handling."""

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
    """Triggers widget hooks to apply dynamic changes.

    Args:
        pdf (bytes): The PDF file data.
        widgets (dict): A dictionary of widgets.
        use_full_widget_name (bool): Whether to use the full widget name.

    Returns:
        bytes: The modified PDF data.
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


def update_text_field_font(annot: DictionaryObject, val: str) -> None:
    """Updates the font of a text field.

    Args:
        annot (DictionaryObject): The annotation dictionary.
        val (str): The new font.
    """
    if Parent in annot and DA not in annot:
        text_appearance = annot[Parent][DA]
    else:
        text_appearance = annot[DA]

    text_appearance = text_appearance.split(" ")
    text_appearance[0] = val
    new_text_appearance = " ".join(text_appearance)

    if Parent in annot and DA not in annot:
        annot[NameObject(Parent)][NameObject(DA)] = TextStringObject(
            new_text_appearance
        )
    else:
        annot[NameObject(DA)] = TextStringObject(new_text_appearance)


def update_text_field_font_size(annot: DictionaryObject, val: float) -> None:
    """Updates the font size of a text field.

    Args:
        annot (DictionaryObject): The annotation dictionary.
        val (float): The new font size.
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
    """Updates the font color of a text field.

    Args:
        annot (DictionaryObject): The annotation dictionary.
        val (tuple): The new font color (RGB).
    """
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
        + [str(each) for each in val]
    )
    new_text_appearance = " ".join(new_text_appearance) + FONT_COLOR_IDENTIFIER

    if Parent in annot and DA not in annot:
        annot[NameObject(Parent)][NameObject(DA)] = TextStringObject(
            new_text_appearance
        )
    else:
        annot[NameObject(DA)] = TextStringObject(new_text_appearance)


def update_text_field_alignment(annot: DictionaryObject, val: int) -> None:
    """Updates the alignment of a text field.

    Args:
        annot (DictionaryObject): The annotation dictionary.
        val (int): The new alignment (0=Left, 1=Center, 2=Right).
    """
    annot[NameObject(Q)] = NumberObject(val)


def update_text_field_multiline(annot: DictionaryObject, val: bool) -> None:
    """Updates the multiline property of a text field.

    Args:
        annot (DictionaryObject): The annotation dictionary.
        val (bool): Whether the field is multiline.
    """
    if val:
        annot[NameObject(Ff)] = NumberObject(int(annot[NameObject(Ff)]) | MULTILINE)


def update_text_field_comb(annot: DictionaryObject, val: bool) -> None:
    """Updates the comb property of a text field.

    Args:
        annot (DictionaryObject): The annotation dictionary.
        val (bool): Whether the field is a comb field.
    """
    if val:
        annot[NameObject(Ff)] = NumberObject(int(annot[NameObject(Ff)]) | COMB)


def update_check_radio_size(annot: DictionaryObject, val: float) -> None:
    """Updates the size of a check or radio button.

    Args:
        annot (DictionaryObject): The annotation dictionary.
        val (float): The new size.
    """
    rect = annot[Rect]
    # scale from bottom left
    new_rect = [
        rect[0],
        rect[1],
        FloatObject(rect[0] + val),
        FloatObject(rect[1] + val),
    ]
    annot[NameObject(Rect)] = ArrayObject(new_rect)
