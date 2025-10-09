# -*- coding: utf-8 -*-
"""
This module defines widget hooks that allow for dynamic modification of PDF form fields.

It provides functions to trigger these hooks, enabling changes to text field properties
like font, font size, color, alignment, and multiline settings, as well as the size
of checkbox and radio button widgets. It also provides functions for flattening
generic and radio button widgets. These hooks are triggered during the PDF form
filling process, allowing for customization of the form's appearance and behavior.
"""

import sys
from io import BytesIO
from typing import cast

from pypdf import PdfReader, PdfWriter
from pypdf.generic import (ArrayObject, DictionaryObject, FloatObject,
                           NameObject, NumberObject, TextStringObject)

from .constants import (COMB, DA, FONT_COLOR_IDENTIFIER, FONT_SIZE_IDENTIFIER,
                        MULTILINE, READ_ONLY, REQUIRED, TU, Annots, Ff, MaxLen,
                        Opt, Parent, Q, Rect)
from .template import get_widget_key
from .utils import stream_to_io


def trigger_widget_hooks(
    pdf: bytes,
    widgets: dict,
    use_full_widget_name: bool,
) -> bytes:
    """
    Triggers widget hooks to apply dynamic changes to PDF form fields.

    This function iterates through the annotations on each page of the PDF and,
    if a widget is associated with an annotation and has hooks to trigger,
    it executes those hooks. Hooks are functions defined in this module that
    modify the annotation dictionary, allowing for dynamic changes to the form field's
    appearance or behavior.

    Args:
        pdf (bytes): The PDF file data as bytes.
        widgets (dict): A dictionary of widgets, where keys are widget identifiers
            and values are widget objects containing information about the widget
            and its associated hooks.
        use_full_widget_name (bool): Whether to use the full widget name when
            looking up widgets in the widgets dictionary.

    Returns:
        bytes: The modified PDF data as bytes, with the widget hooks applied.
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
    """
    Updates the font of a text field annotation.

    This function modifies the appearance string (DA) in the annotation dictionary
    to change the font used for the text field. It ensures that the provided font
    name is a proper PDF font by checking if it starts with a slash "/".
    The function then correctly identifies and updates the font in the appearance
    stream by locating the existing font identifier (which also starts with a slash).

    Args:
        annot (DictionaryObject): The annotation dictionary for the text field.
        val (str): The new font name to use for the text field. Must start with "/".
    """
    if not val.startswith("/"):
        return
    if Parent in annot and DA not in annot:
        text_appearance = annot[Parent][DA]
    else:
        text_appearance = annot[DA]

    text_appearance = text_appearance.split(" ")

    index_to_update = 0
    for i, each in enumerate(text_appearance):
        if each.startswith("/"):
            index_to_update = i
            break

    text_appearance[index_to_update] = val
    new_text_appearance = " ".join(text_appearance)

    if Parent in annot and DA not in annot:
        annot[NameObject(Parent)][NameObject(DA)] = TextStringObject(
            new_text_appearance
        )
    else:
        annot[NameObject(DA)] = TextStringObject(new_text_appearance)


def update_text_field_font_size(annot: DictionaryObject, val: float) -> None:
    """
    Updates the font size of a text field annotation.

    This function modifies the appearance string (DA) in the annotation dictionary
    to change the font size used for the text field.

    Args:
        annot (DictionaryObject): The annotation dictionary for the text field.
        val (float): The new font size to use for the text field.
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
    """
    Updates the font color of a text field annotation.

    This function modifies the appearance string (DA) in the annotation dictionary
    to change the font color used for the text field.

    Args:
        annot (DictionaryObject): The annotation dictionary for the text field.
        val (tuple): The new font color as an RGB tuple (e.g., (1, 0, 0) for red).
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
    """
    Updates the text alignment of a text field annotation.

    This function modifies the Q entry in the annotation dictionary to change
    the text alignment of the text field.

    Args:
        annot (DictionaryObject): The annotation dictionary for the text field.
        val (int): The new alignment value (0=Left, 1=Center, 2=Right).
    """
    annot[NameObject(Q)] = NumberObject(val)


def update_text_field_multiline(annot: DictionaryObject, val: bool) -> None:
    """
    Updates the multiline property of a text field annotation.

    This function modifies the Ff (flags) entry in the annotation dictionary to
    enable or disable the multiline property of the text field.

    Args:
        annot (DictionaryObject): The annotation dictionary for the text field.
        val (bool): True to enable multiline, False to disable.
    """
    if val:
        # Ff in annot[Parent] only in hooks.py, or when editing instead of retrieving
        if Parent in annot and Ff in annot[Parent]:
            annot[NameObject(Parent)][NameObject(Ff)] = NumberObject(
                int(
                    annot[NameObject(Parent)][NameObject(Ff)]
                    if Ff in annot[NameObject(Parent)]
                    else 0
                )
                | MULTILINE
            )
        else:
            annot[NameObject(Ff)] = NumberObject(
                int(annot[NameObject(Ff)] if Ff in annot else 0) | MULTILINE
            )


def update_text_field_comb(annot: DictionaryObject, val: bool) -> None:
    """
    Updates the comb property of a text field annotation.

    This function modifies the Ff (flags) entry in the annotation dictionary to
    enable or disable the comb property of the text field, which limits the
    number of characters that can be entered in each line.

    Args:
        annot (DictionaryObject): The annotation dictionary for the text field.
        val (bool): True to enable comb, False to disable.
    """
    if val:
        if Parent in annot and Ff in annot[Parent]:
            annot[NameObject(Parent)][NameObject(Ff)] = NumberObject(
                int(
                    annot[NameObject(Parent)][NameObject(Ff)]
                    if Ff in annot[NameObject(Parent)]
                    else 0
                )
                | COMB
            )
        else:
            annot[NameObject(Ff)] = NumberObject(
                int(annot[NameObject(Ff)] if Ff in annot else 0) | COMB
            )


def update_text_field_max_length(annot: DictionaryObject, val: int) -> None:
    """
    Updates the maximum length of a text field annotation.

    This function sets the 'MaxLen' entry in the annotation dictionary, which
    specifies the maximum number of characters that can be entered into the text field.

    Args:
        annot (DictionaryObject): The annotation dictionary for the text field.
        val (int): The maximum number of characters allowed in the text field.
    """
    annot[NameObject(MaxLen)] = NumberObject(val)


def update_check_radio_size(annot: DictionaryObject, val: float) -> None:
    """
    Updates the size of a check box or radio button annotation.

    This function modifies the Rect entry in the annotation dictionary to change
    the size of the check box or radio button.

    Args:
        annot (DictionaryObject): The annotation dictionary for the check box or
            radio button.
        val (float): The new size (width and height) for the check box or radio button.
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


def update_dropdown_choices(annot: DictionaryObject, val: list) -> None:
    """
    Updates the choices in a dropdown field annotation.

    This function modifies the Opt entry in the annotation dictionary to change
    the available choices in the dropdown field.

    Args:
        annot (DictionaryObject): The annotation dictionary for the dropdown field.
        val (list): A list of strings or tuples representing the new choices for the dropdown.
    """
    annot[NameObject(Opt)] = ArrayObject(
        [
            (
                ArrayObject([TextStringObject(each[1]), TextStringObject(each[0])])
                if isinstance(each, tuple)
                else ArrayObject([TextStringObject(each), TextStringObject(each)])
            )
            for each in val
        ]
    )


def flatten_radio(annot: DictionaryObject, val: bool) -> None:
    """
    Flattens a radio button annotation by setting or unsetting the ReadOnly flag,
    making it non-editable or editable based on the `val` parameter.

    This function modifies the Ff (flags) entry in the radio button's annotation
    dictionary or its parent dictionary if `Parent` exists in `annot`, to set or
    unset the ReadOnly flag, preventing or allowing the user from changing the
    selected option.

    Args:
        annot (DictionaryObject): The radio button annotation dictionary.
        val (bool): True to flatten (make read-only), False to unflatten (make editable).
    """
    if Parent in annot:
        annot[NameObject(Parent)][NameObject(Ff)] = NumberObject(
            (
                int(annot[NameObject(Parent)].get(NameObject(Ff), 0)) | READ_ONLY
                if val
                else int(annot[NameObject(Parent)].get(NameObject(Ff), 0)) & ~READ_ONLY
            )
        )
    else:
        annot[NameObject(Ff)] = NumberObject(
            (
                int(annot.get(NameObject(Ff), 0)) | READ_ONLY
                if val
                else int(annot.get(NameObject(Ff), 0)) & ~READ_ONLY
            )
        )


def flatten_generic(annot: DictionaryObject, val: bool) -> None:
    """
    Flattens a generic annotation by setting or unsetting the ReadOnly flag,
    making it non-editable or editable based on the `val` parameter.

    This function modifies the Ff (flags) entry in the annotation dictionary to
    set or unset the ReadOnly flag, preventing or allowing the user from
    interacting with the form field.

    Args:
        annot (DictionaryObject): The annotation dictionary.
        val (bool): True to flatten (make read-only), False to unflatten (make editable).
    """
    if Parent in annot and (Ff in annot[Parent] or Ff not in annot):
        annot[NameObject(Parent)][NameObject(Ff)] = NumberObject(
            (
                int(annot.get(NameObject(Ff), 0)) | READ_ONLY
                if val
                else int(annot.get(NameObject(Ff), 0)) & ~READ_ONLY
            )
        )
    else:
        annot[NameObject(Ff)] = NumberObject(
            (
                int(annot.get(NameObject(Ff), 0)) | READ_ONLY
                if val
                else int(annot.get(NameObject(Ff), 0)) & ~READ_ONLY
            )
        )


def update_field_tooltip(annot: DictionaryObject, val: str) -> None:
    """
    Updates the tooltip (alternate field name) of a form field annotation.

    This function sets the 'TU' entry in the annotation dictionary, which
    provides a text string that can be used as a tooltip for the field.

    Args:
        annot (DictionaryObject): The annotation dictionary for the form field.
        val (str): The new tooltip string for the field.
    """
    if val:
        annot[NameObject(TU)] = TextStringObject(val)


def update_field_required(annot: DictionaryObject, val: bool) -> None:
    """
    Updates the 'Required' flag of a form field annotation.

    This function modifies the Ff (flags) entry in the annotation dictionary
    (or its parent if applicable) to set or unset the 'Required' flag,
    making the field mandatory or optional.

    Args:
        annot (DictionaryObject): The annotation dictionary for the form field.
        val (bool): True to set the field as required, False to make it optional.
    """
    if Parent in annot and Ff in annot[Parent]:
        annot[NameObject(Parent)][NameObject(Ff)] = NumberObject(
            (
                int(annot.get(NameObject(Ff), 0)) | REQUIRED
                if val
                else int(annot.get(NameObject(Ff), 0)) & ~REQUIRED
            )
        )
    else:
        annot[NameObject(Ff)] = NumberObject(
            (
                int(annot.get(NameObject(Ff), 0)) | REQUIRED
                if val
                else int(annot.get(NameObject(Ff), 0)) & ~REQUIRED
            )
        )
