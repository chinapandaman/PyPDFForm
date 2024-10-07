# -*- coding: utf-8 -*-
"""Contains patterns used for identifying properties of widgets."""

from pypdf.generic import (DictionaryObject, NameObject, NumberObject,
                           TextStringObject)

from .constants import (AP, AS, CA, DA, DV, FT, IMAGE_FIELD_IDENTIFIER, JS, MK,
                        MULTILINE, READ_ONLY, A, Btn, Ch, Ff, N, Off, Opt,
                        Parent, Q, Sig, T, Tx, V, Yes, Type, Action, S, JavaScript)
from .middleware.checkbox import Checkbox
from .middleware.dropdown import Dropdown
from .middleware.image import Image
from .middleware.pushbutton import Pushbutton
from .middleware.radio import Radio
from .middleware.signature import Signature
from .middleware.text import Text

WIDGET_TYPE_PATTERNS = [
    (
        ({A: {JS: IMAGE_FIELD_IDENTIFIER}},),
        Image,
    ),
    (
        (
            {FT: Btn},
            {Ff: 17},
        ),
        Pushbutton,
    ),
    (
        ({FT: Sig},),
        Signature,
    ),
    (
        ({FT: Tx},),
        Text,
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


def simple_update_checkbox_value(annot: DictionaryObject, check: bool = False) -> None:
    """Patterns to update values for checkbox annotations."""

    for each in annot[AP][N]:  # noqa
        if (check and str(each) != Off) or (not check and str(each) == Off):
            annot[NameObject(AS)] = NameObject(each)
            annot[NameObject(V)] = NameObject(each)
            break


def simple_update_radio_value(annot: DictionaryObject) -> None:
    """Patterns to update values for radio annotations."""

    for each in annot[AP][N]:  # noqa
        if str(each) != Off:
            annot[NameObject(AS)] = NameObject(each)
            annot[NameObject(Parent)][NameObject(V)] = NameObject(each)  # noqa
            break


def simple_update_dropdown_value(annot: DictionaryObject, widget: Dropdown) -> None:
    """Patterns to update values for dropdown annotations."""

    if Parent in annot and T not in annot:
        annot[NameObject(Parent)][NameObject(V)] = TextStringObject(  # noqa
            widget.choices[widget.value]
        )
        annot[NameObject(AP)] = TextStringObject(widget.choices[widget.value])
    else:
        annot[NameObject(V)] = TextStringObject(widget.choices[widget.value])
        annot[NameObject(AP)] = TextStringObject(widget.choices[widget.value])


def simple_update_text_value(annot: DictionaryObject, widget: Text) -> None:
    """Patterns to update values for text annotations."""

    if Parent in annot and T not in annot:
        annot[NameObject(Parent)][NameObject(V)] = TextStringObject(  # noqa
            widget.value
        )
        annot[NameObject(AP)] = TextStringObject(widget.value)
    else:
        annot[NameObject(V)] = TextStringObject(widget.value)
        annot[NameObject(AP)] = TextStringObject(widget.value)


def simple_set_image_field(annot: DictionaryObject) -> None:
    """Patterns to set for an image field."""

    annot[NameObject(A)] = DictionaryObject({
        NameObject(Type): NameObject(Action),
        NameObject(S): NameObject(JavaScript),
        NameObject(JS): TextStringObject(IMAGE_FIELD_IDENTIFIER),
    })

def simple_flatten_radio(annot: DictionaryObject) -> None:
    """Patterns to flatten checkbox annotations."""

    annot[NameObject(Parent)][NameObject(Ff)] = NumberObject(  # noqa
        int(annot[NameObject(Parent)].get(NameObject(Ff), 0)) | READ_ONLY  # noqa
    )


def simple_flatten_generic(annot: DictionaryObject) -> None:
    """Patterns to flatten generic annotations."""

    if Parent in annot and Ff not in annot:
        annot[NameObject(Parent)][NameObject(Ff)] = NumberObject(  # noqa
            int(annot.get(NameObject(Ff), 0)) | READ_ONLY  # noqa
        )
    else:
        annot[NameObject(Ff)] = NumberObject(
            int(annot.get(NameObject(Ff), 0)) | READ_ONLY  # noqa
        )


def update_created_text_field_alignment(annot: DictionaryObject, val: int) -> None:
    """Patterns to update text alignment for text annotations created by the library."""

    annot[NameObject(Q)] = NumberObject(val)


def update_created_text_field_multiline(annot: DictionaryObject, val: bool) -> None:
    """Patterns to update to multiline for text annotations created by the library."""

    if val:
        annot[NameObject(Ff)] = NumberObject(
            int(annot[NameObject(Ff)]) | MULTILINE  # noqa
        )


NON_ACRO_FORM_PARAM_TO_FUNC = {
    ("TextWidget", "alignment"): update_created_text_field_alignment,
    ("TextWidget", "multiline"): update_created_text_field_multiline,
}
