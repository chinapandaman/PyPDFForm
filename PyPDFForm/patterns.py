# -*- coding: utf-8 -*-
"""
This module defines patterns and utility functions for interacting with PDF form fields.

It includes patterns for identifying different types of widgets (e.g., text fields,
checkboxes, radio buttons, dropdowns, images, and signatures) based on their
properties in the PDF's annotation dictionary. It also provides utility functions
for updating these widgets.
"""

from pypdf.generic import (ArrayObject, DictionaryObject, NameObject,
                           NumberObject, TextStringObject)

from .constants import (AP, AS, DV, FT, IMAGE_FIELD_IDENTIFIER, JS, TU, A, Btn,
                        Ch, I, N, Off, Opt, Parent, Sig, T, Tx, V, Yes)
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


def update_checkbox_value(annot: DictionaryObject, check: bool = False) -> None:
    """
    Updates the value of a checkbox annotation, setting it to checked or unchecked.

    This function modifies the appearance state (AS) and value (V) of the checkbox
    annotation to reflect the desired state (checked or unchecked).

    Args:
        annot (DictionaryObject): The checkbox annotation dictionary.
        check (bool): True to check the checkbox, False to uncheck it. Defaults to False.
    """
    for each in annot[AP][N]:
        if (check and str(each) != Off) or (not check and str(each) == Off):
            annot[NameObject(AS)] = NameObject(each)
            annot[NameObject(V)] = NameObject(each)
            break


def get_checkbox_value(annot: DictionaryObject) -> bool:
    return True if annot[V] != Off else False


def update_radio_value(annot: DictionaryObject) -> None:
    """
    Updates the value of a radio button annotation, selecting it.

    This function modifies the appearance state (AS) and value (V) of the radio button's
    parent dictionary to reflect the selected state.

    Args:
        annot (DictionaryObject): The radio button annotation dictionary.
    """
    if Opt in annot[Parent]:
        del annot[Parent][Opt]

    for each in annot[AP][N]:
        if str(each) != Off:
            annot[NameObject(AS)] = NameObject(each)
            annot[NameObject(Parent)][NameObject(V)] = NameObject(each)
            break


def update_dropdown_value(annot: DictionaryObject, widget: Dropdown) -> None:
    """
    Updates the value of a dropdown annotation, selecting an option from the list.

    This function modifies the value (V) and appearance (AP) of the dropdown
    annotation to reflect the selected option. It also updates the index (I)
    of the selected option.

    Args:
        annot (DictionaryObject): The dropdown annotation dictionary.
        widget (Dropdown): The Dropdown widget object containing the selected value.
    """
    choices = widget.choices or []
    if Parent in annot and T not in annot:
        annot[NameObject(Parent)][NameObject(V)] = TextStringObject(
            choices[widget.value]
        )
        annot[NameObject(AP)] = TextStringObject(choices[widget.value])
    else:
        annot[NameObject(V)] = TextStringObject(choices[widget.value])
        annot[NameObject(AP)] = TextStringObject(choices[widget.value])
        annot[NameObject(I)] = ArrayObject([NumberObject(widget.value)])


def update_text_value(annot: DictionaryObject, widget: Text) -> None:
    """
    Updates the value of a text annotation, setting the text content.

    This function modifies the value (V) and appearance (AP) of the text
    annotation to reflect the new text content.

    Args:
        annot (DictionaryObject): The text annotation dictionary.
        widget (Text): The Text widget object containing the text value.
    """
    if Parent in annot and T not in annot:
        annot[NameObject(Parent)][NameObject(V)] = TextStringObject(widget.value)
        annot[NameObject(AP)] = TextStringObject(widget.value)
    else:
        annot[NameObject(V)] = TextStringObject(widget.value)
        annot[NameObject(AP)] = TextStringObject(widget.value)


def get_text_value(annot: DictionaryObject, widget: Text) -> None:
    if Parent in annot and T not in annot:
        widget.value = annot[Parent].get(V)
    else:
        widget.value = annot.get(V)



def update_annotation_name(annot: DictionaryObject, val: str) -> None:
    """
    Updates the name of an annotation, setting the T (title) entry.

    This function modifies the T (title) entry in the annotation dictionary to
    change the name or title of the annotation.

    Args:
        annot (DictionaryObject): The annotation dictionary.
        val (str): The new name for the annotation.
    """
    if Parent in annot and T not in annot:
        annot[NameObject(Parent)][NameObject(T)] = TextStringObject(val)
    else:
        annot[NameObject(T)] = TextStringObject(val)
