# -*- coding: utf-8 -*-
"""Pattern matching utilities for PDF form widgets.

This module provides:
- Pattern definitions for identifying widget types and properties
- Functions for updating widget states and appearances
- Support for common PDF form operations like flattening fields

Patterns are used throughout PyPDFForm to:
- Classify widget types (text, checkbox, radio, etc.)
- Extract widget properties (alignment, colors, flags)
- Modify widget states (values, appearances, flags)

The module also contains utility functions for common PDF form operations
like updating field values and flattening form fields.
"""

from pypdf.generic import (ArrayObject, DictionaryObject, NameObject,
                           NumberObject, TextStringObject)

from .constants import (AP, AS, BC, BG, BS, CA, DA, DV, FT,
                        IMAGE_FIELD_IDENTIFIER, JS, MK, MULTILINE, READ_ONLY,
                        TU, A, Btn, Ch, D, Ff, I, N, Off, Opt, Parent, Q, S,
                        Sig, T, Tx, V, W, Yes)
from .middleware.checkbox import Checkbox
from .middleware.dropdown import Dropdown
from .middleware.image import Image
from .middleware.radio import Radio
from .middleware.signature import Signature
from .middleware.text import Text

WIDGET_TYPE_PATTERNS = [
    (
        ({A: {JS: IMAGE_FIELD_IDENTIFIER}},),
        Image,
    ),
    (
        ({FT: Sig},),
        Signature,
    ),
    (
        ({Parent: {FT: Sig}},),
        Signature,
    ),
    (
        ({FT: Tx},),
        Text,
    ),
    (
        # reportlab creation pattern
        (
            {FT: Btn},
            {Parent: {FT: Btn}},
            {AS: (Yes, Off)},
        ),
        Radio,
    ),
    (
        (
            {FT: Btn},
            {AS: (Yes, Off)},
        ),
        Checkbox,
    ),
    (
        ({FT: Ch},),
        Dropdown,
    ),
    (
        ({Parent: {FT: Ch}},),
        Dropdown,
    ),
    (
        ({Parent: {FT: Tx}},),
        Text,
    ),
    (
        (
            {Parent: {FT: Btn}},
            {Parent: {DV: (Yes, Off)}},
            {AS: (Yes, Off)},
        ),
        Checkbox,
    ),
    (
        (
            {Parent: {FT: Btn}},
            {AS: (Yes, Off)},
        ),
        Radio,
    ),
]

WIDGET_KEY_PATTERNS = [
    {T: True},
    {Parent: {T: True}},
]

WIDGET_DESCRIPTION_PATTERNS = [{TU: True}, {Parent: {TU: True}}]

DROPDOWN_CHOICE_PATTERNS = [
    {Opt: True},
    {Parent: {Opt: True}},
]

WIDGET_ALIGNMENT_PATTERNS = [
    {Q: True},
    {Parent: {Q: True}},
]

TEXT_FIELD_FLAG_PATTERNS = [
    {Ff: True},
    {Parent: {Ff: True}},
]

TEXT_FIELD_APPEARANCE_PATTERNS = [
    {DA: True},
    {Parent: {DA: True}},
]

BUTTON_STYLE_PATTERNS = [
    {MK: {CA: True}},
]

BORDER_COLOR_PATTERNS = [
    {MK: {BC: True}},
]

BACKGROUND_COLOR_PATTERNS = [
    {MK: {BG: True}},
]

BORDER_WIDTH_PATTERNS = [{BS: {W: True}}]

BORDER_STYLE_PATTERNS = [{BS: {S: True}}]

BORDER_DASH_ARRAY_PATTERNS = [{BS: {D: True}}]


def simple_update_checkbox_value(annot: DictionaryObject, check: bool = False) -> None:
    """Update checkbox annotation values based on check state.

    Modifies the appearance state (AS) and value (V) of a checkbox annotation
    to reflect the desired checked/unchecked state. Uses the annotation's
    appearance dictionary (AP/N) to determine valid states.

    Args:
        annot: PDF annotation dictionary to modify
        check: Whether the checkbox should be checked (True) or unchecked (False)
    """

    for each in annot[AP][N]:
        if (check and str(each) != Off) or (not check and str(each) == Off):
            annot[NameObject(AS)] = NameObject(each)
            annot[NameObject(V)] = NameObject(each)
            break


def simple_update_radio_value(annot: DictionaryObject) -> None:
    """Update radio button annotation values to selected state.

    Modifies the appearance state (AS) of a radio button annotation and updates
    the parent's value (V) to reflect the selected state. Removes 'Opt' entry
    from parent dictionary if present. Uses the annotation's appearance
    dictionary (AP/N) to determine valid states.

    Args:
        annot: PDF radio button annotation dictionary to modify
    """

    if Opt in annot[Parent]:
        del annot[Parent][Opt]

    for each in annot[AP][N]:
        if str(each) != Off:
            annot[NameObject(AS)] = NameObject(each)
            annot[NameObject(Parent)][NameObject(V)] = NameObject(each)
            break


def simple_update_dropdown_value(annot: DictionaryObject, widget: Dropdown) -> None:
    """Update dropdown annotation values based on widget selection.

    Modifies the value (V), appearance (AP), and index (I) of a dropdown
    annotation to reflect the currently selected choice from the widget.
    Handles both standalone dropdowns and those with parent annotations.

    Args:
        annot: PDF dropdown annotation dictionary to modify
        widget: Dropdown widget containing the selected value
    """

    if Parent in annot and T not in annot:
        annot[NameObject(Parent)][NameObject(V)] = TextStringObject(
            widget.choices[widget.value]
        )
        annot[NameObject(AP)] = TextStringObject(widget.choices[widget.value])
    else:
        annot[NameObject(V)] = TextStringObject(widget.choices[widget.value])
        annot[NameObject(AP)] = TextStringObject(widget.choices[widget.value])
        annot[NameObject(I)] = ArrayObject([NumberObject(widget.value)])


def simple_update_text_value(annot: DictionaryObject, widget: Text) -> None:
    """Update text field annotation values based on widget content.

    Modifies the value (V) and appearance (AP) of a text field annotation to
    reflect the current value from the text widget. Handles both standalone
    text fields and those with parent annotations.

    Args:
        annot: PDF text field annotation dictionary to modify
        widget: Text widget containing the value to set
    """

    if Parent in annot and T not in annot:
        annot[NameObject(Parent)][NameObject(V)] = TextStringObject(
            widget.value
        )
        annot[NameObject(AP)] = TextStringObject(widget.value)
    else:
        annot[NameObject(V)] = TextStringObject(widget.value)
        annot[NameObject(AP)] = TextStringObject(widget.value)


def simple_flatten_radio(annot: DictionaryObject) -> None:
    """Flatten radio button annotation by making it read-only.

    Modifies the field flags (Ff) of a radio button's parent annotation
    to set the read-only flag, effectively flattening the field and
    preventing further user interaction.

    Args:
        annot: PDF radio button annotation dictionary to flatten
    """

    annot[NameObject(Parent)][NameObject(Ff)] = NumberObject(
        int(annot[NameObject(Parent)].get(NameObject(Ff), 0)) | READ_ONLY
    )


def simple_flatten_generic(annot: DictionaryObject) -> None:
    """Flatten generic annotation by making it read-only.

    Modifies the field flags (Ff) of an annotation to set the read-only flag,
    effectively flattening the field and preventing further user interaction.
    Handles both standalone annotations and those with parent annotations.

    Args:
        annot: PDF annotation dictionary to flatten
    """

    if Parent in annot and Ff not in annot:
        annot[NameObject(Parent)][NameObject(Ff)] = NumberObject(
            int(annot.get(NameObject(Ff), 0)) | READ_ONLY
        )
    else:
        annot[NameObject(Ff)] = NumberObject(
            int(annot.get(NameObject(Ff), 0)) | READ_ONLY
        )


def update_annotation_name(annot: DictionaryObject, val: str) -> None:
    """Update the name/title of a PDF annotation.

    Modifies the title (T) field of an annotation to set a new name.
    Handles both standalone annotations and those with parent annotations.

    Args:
        annot: PDF annotation dictionary to modify
        val: New name/title to set for the annotation
    """

    if Parent in annot and T not in annot:
        annot[NameObject(Parent)][NameObject(T)] = TextStringObject(val)
    else:
        annot[NameObject(T)] = TextStringObject(val)


def update_created_text_field_alignment(annot: DictionaryObject, val: int) -> None:
    """Update text alignment for created text field annotations.

    Modifies the alignment (Q) field of a text field annotation created
    by the library to set the specified text alignment.

    Args:
        annot: PDF text field annotation dictionary to modify
        val: Alignment value to set (typically 0=left, 1=center, 2=right)
    """

    annot[NameObject(Q)] = NumberObject(val)


def update_created_text_field_multiline(annot: DictionaryObject, val: bool) -> None:
    """Update multiline flag for created text field annotations.

    Modifies the field flags (Ff) of a text field annotation created by
    the library to set or clear the multiline flag based on the input value.

    Args:
        annot: PDF text field annotation dictionary to modify
        val: Whether to enable multiline (True) or disable (False)
    """

    if val:
        annot[NameObject(Ff)] = NumberObject(
            int(annot[NameObject(Ff)]) | MULTILINE
        )


NON_ACRO_FORM_PARAM_TO_FUNC = {
    ("TextWidget", "alignment"): update_created_text_field_alignment,
    ("TextWidget", "multiline"): update_created_text_field_multiline,
}
