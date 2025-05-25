# -*- coding: utf-8 -*-

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
    for each in annot[AP][N]:
        if (check and str(each) != Off) or (not check and str(each) == Off):
            annot[NameObject(AS)] = NameObject(each)
            annot[NameObject(V)] = NameObject(each)
            break


def simple_update_radio_value(annot: DictionaryObject) -> None:
    if Opt in annot[Parent]:
        del annot[Parent][Opt]

    for each in annot[AP][N]:
        if str(each) != Off:
            annot[NameObject(AS)] = NameObject(each)
            annot[NameObject(Parent)][NameObject(V)] = NameObject(each)
            break


def simple_update_dropdown_value(annot: DictionaryObject, widget: Dropdown) -> None:
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
    if Parent in annot and T not in annot:
        annot[NameObject(Parent)][NameObject(V)] = TextStringObject(widget.value)
        annot[NameObject(AP)] = TextStringObject(widget.value)
    else:
        annot[NameObject(V)] = TextStringObject(widget.value)
        annot[NameObject(AP)] = TextStringObject(widget.value)


def simple_flatten_radio(annot: DictionaryObject) -> None:
    annot[NameObject(Parent)][NameObject(Ff)] = NumberObject(
        int(annot[NameObject(Parent)].get(NameObject(Ff), 0)) | READ_ONLY
    )


def simple_flatten_generic(annot: DictionaryObject) -> None:
    if Parent in annot and Ff not in annot:
        annot[NameObject(Parent)][NameObject(Ff)] = NumberObject(
            int(annot.get(NameObject(Ff), 0)) | READ_ONLY
        )
    else:
        annot[NameObject(Ff)] = NumberObject(
            int(annot.get(NameObject(Ff), 0)) | READ_ONLY
        )


def update_annotation_name(annot: DictionaryObject, val: str) -> None:
    if Parent in annot and T not in annot:
        annot[NameObject(Parent)][NameObject(T)] = TextStringObject(val)
    else:
        annot[NameObject(T)] = TextStringObject(val)
