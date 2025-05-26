# -*- coding: utf-8 -*-
"""
Module containing patterns and utility functions for interacting with PDF form fields.
"""

from pypdf.generic import (ArrayObject, DictionaryObject, NameObject,
                           NumberObject, TextStringObject)

from .constants import (AP, AS, DV, FT, IMAGE_FIELD_IDENTIFIER, JS, READ_ONLY,
                        TU, A, Btn, Ch, Ff, I, N, Off, Opt, Parent, Sig, T, Tx,
                        V, Yes)
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


def simple_update_checkbox_value(annot: DictionaryObject, check: bool = False) -> None:
    """
    Update the value of a checkbox annotation.

    Args:
        annot: The checkbox annotation dictionary.
        check: A boolean indicating whether to check or uncheck the checkbox.
    """
    for each in annot[AP][N]:
        if (check and str(each) != Off) or (not check and str(each) == Off):
            annot[NameObject(AS)] = NameObject(each)
            annot[NameObject(V)] = NameObject(each)
            break


def simple_update_radio_value(annot: DictionaryObject) -> None:
    """
    Update the value of a radio button annotation.

    Args:
        annot: The radio button annotation dictionary.
    """
    if Opt in annot[Parent]:
        del annot[Parent][Opt]

    for each in annot[AP][N]:
        if str(each) != Off:
            annot[NameObject(AS)] = NameObject(each)
            annot[NameObject(Parent)][NameObject(V)] = NameObject(each)
            break


def simple_update_dropdown_value(annot: DictionaryObject, widget: Dropdown) -> None:
    """
    Update the value of a dropdown annotation.

    Args:
        annot: The dropdown annotation dictionary.
        widget: The Dropdown widget object.
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
    """
    Update the value of a text annotation.

    Args:
        annot: The text annotation dictionary.
        widget: The Text widget object.
    """
    if Parent in annot and T not in annot:
        annot[NameObject(Parent)][NameObject(V)] = TextStringObject(widget.value)
        annot[NameObject(AP)] = TextStringObject(widget.value)
    else:
        annot[NameObject(V)] = TextStringObject(widget.value)
        annot[NameObject(AP)] = TextStringObject(widget.value)


def simple_flatten_radio(annot: DictionaryObject) -> None:
    """
    Flatten a radio button annotation by setting the ReadOnly flag.

    Args:
        annot: The radio button annotation dictionary.
    """
    annot[NameObject(Parent)][NameObject(Ff)] = NumberObject(
        int(annot[NameObject(Parent)].get(NameObject(Ff), 0)) | READ_ONLY
    )


def simple_flatten_generic(annot: DictionaryObject) -> None:
    """
    Flatten a generic annotation by setting the ReadOnly flag.

    Args:
        annot: The annotation dictionary.
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
    """
    Update the name of an annotation.

    Args:
        annot: The annotation dictionary.
        val: The new name for the annotation.
    """
    if Parent in annot and T not in annot:
        annot[NameObject(Parent)][NameObject(T)] = TextStringObject(val)
    else:
        annot[NameObject(T)] = TextStringObject(val)
