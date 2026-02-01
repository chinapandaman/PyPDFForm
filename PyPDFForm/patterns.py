# -*- coding: utf-8 -*-
"""
This module defines patterns and utility functions for interacting with PDF form fields.

It includes patterns for identifying different types of widgets (e.g., text fields,
checkboxes, radio buttons, dropdowns, images, and signatures) based on their
properties in the PDF's annotation dictionary. It also provides utility functions
for updating these widgets.
"""

from typing import Tuple, Union

from pypdf.generic import (ArrayObject, DictionaryObject, NameObject,
                           NumberObject, TextStringObject)

from .constants import (AP, AS, DV, FT, HIDDEN, IMAGE_FIELD_IDENTIFIER, JS,
                        SLASH, TU, A, Btn, Ch, F, Ff, I, MaxLen, N, Off, Opt,
                        Parent, Q, Rect, Sig, Subtype, T, Tx, V, Widget, Yes)
from .middleware.checkbox import Checkbox
from .middleware.dropdown import Dropdown
from .middleware.image import Image
from .middleware.radio import Radio
from .middleware.signature import Signature
from .middleware.text import Text
from .utils import extract_widget_property

WIDGET_TYPE_PATTERNS = [
    (
        (
            {Subtype: Widget},
            {A: {JS: IMAGE_FIELD_IDENTIFIER}},
        ),
        Image,
    ),
    (
        (
            {Subtype: Widget},
            {FT: Sig},
        ),
        Signature,
    ),
    (
        (
            {Subtype: Widget},
            {Parent: {FT: Sig}},
        ),
        Signature,
    ),
    (
        (
            {Subtype: Widget},
            {FT: Tx},
        ),
        Text,
    ),
    (
        # reportlab creation pattern
        (
            {Subtype: Widget},
            {FT: Btn},
            {Parent: {FT: Btn}},
            {AS: (Yes, Off, SLASH)},
        ),
        Radio,
    ),
    (
        (
            {Subtype: Widget},
            {FT: Btn},
            {AS: (Yes, Off)},
        ),
        Checkbox,
    ),
    (
        (
            {Subtype: Widget},
            {FT: Ch},
        ),
        Dropdown,
    ),
    (
        (
            {Subtype: Widget},
            {Parent: {FT: Ch}},
        ),
        Dropdown,
    ),
    (
        (
            {Subtype: Widget},
            {Parent: {FT: Tx}},
        ),
        Text,
    ),
    (
        (
            {Subtype: Widget},
            {Parent: {FT: Btn}},
            {Parent: {DV: (Yes, Off)}},
            {AS: (Yes, Off)},
        ),
        Checkbox,
    ),
    (
        (
            {Subtype: Widget},
            {Parent: {FT: Btn}},
            {AS: (Yes, Off, SLASH)},
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


def check_field_flag(annot: DictionaryObject, flag: int) -> bool:
    """
    Checks if a specific flag is set for a field annotation.

    This function inspects the 'Ff' (field flags) entry of the annotation
    dictionary (or its parent if it's a child annotation) to determine if the
    provided flag is set.

    Args:
        annot (DictionaryObject): The annotation dictionary.
        flag (int): The bit flag to check for.

    Returns:
        bool: True if the flag is set, False otherwise.
    """
    if Parent in annot and Ff not in annot:
        return bool(
            int(
                annot[NameObject(Parent)][NameObject(Ff)]
                if Ff in annot[NameObject(Parent)]
                else 0
            )
            & flag
        )
    return bool(int(annot[NameObject(Ff)] if Ff in annot else 0) & flag)


def get_widget_key(widget: dict, use_full_widget_name: bool) -> str:
    """
    Extracts the widget key from a widget dictionary.

    This function extracts the widget key from a widget dictionary based on
    predefined patterns. If `use_full_widget_name` is True, it recursively
    constructs the full widget name by concatenating the parent widget keys.

    Args:
        widget (dict): The widget dictionary to extract the key from.
        use_full_widget_name (bool): Whether to use the full widget name
            (including parent names) as the widget key.

    Returns:
        str: The extracted widget key.
    """
    if not use_full_widget_name:
        return extract_widget_property(widget, WIDGET_KEY_PATTERNS, None, str)

    key = widget.get(T)
    if (
        Parent in widget
        and T in widget[Parent].get_object()
        and widget[Parent].get_object()[T] != key  # sejda case
    ):
        if key is None:
            return get_widget_key(widget[Parent].get_object(), use_full_widget_name)

        return (
            f"{get_widget_key(widget[Parent].get_object(), use_full_widget_name)}.{key}"
        )

    return key or ""


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


def get_checkbox_value(annot: DictionaryObject) -> Union[bool, None]:
    """
    Retrieves the boolean value of a checkbox annotation.

    This function checks the value (V) of the checkbox annotation. If the value
    is not 'Off', it means the checkbox is checked, and True is returned.
    Otherwise, if the value is 'Off' or not present, None is returned.

    Args:
        annot (DictionaryObject): The checkbox annotation dictionary.

    Returns:
        Union[bool, None]: True if the checkbox is checked, None otherwise.
    """
    return True if annot.get(V, Off) != Off else None


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


def get_radio_value(annot: DictionaryObject) -> bool:
    """
    Retrieves the boolean value of a radio button annotation.

    This function iterates through the appearance states (AP) of the radio button
    annotation. If the value (V) of the parent dictionary matches any of these
    appearance states, it means the radio button is selected, and True is returned.
    Otherwise, False is returned.

    Args:
        annot (DictionaryObject): The radio button annotation dictionary.

    Returns:
        bool: True if the radio button is selected, False otherwise.
    """
    for each in annot.get(AP, {}).get(N, []):
        if annot.get(Parent, {}).get(V) == each:
            return True

    return False


def update_dropdown_value(
    annot: DictionaryObject, widget: Dropdown, need_appearances: bool
) -> None:
    """
    Updates the value of a dropdown annotation, selecting an option from the list.

    This function modifies the value (V) and appearance (AP) of the dropdown
    annotation to reflect the selected option. It also updates the index (I)
    of the selected option.

    Args:
        annot (DictionaryObject): The dropdown annotation dictionary.
        widget (Dropdown): The Dropdown widget object containing the selected value.
        need_appearances (bool): If True, skips updating the appearance stream (AP) to
            maintain compatibility with Adobe Reader's behavior for certain fields.
    """
    choices = widget.choices or []
    if Parent in annot and T not in annot:
        annot[NameObject(Parent)][NameObject(V)] = TextStringObject(
            choices[widget.value]
        )
        if not need_appearances:
            annot[NameObject(AP)] = TextStringObject(choices[widget.value])
    else:
        annot[NameObject(V)] = TextStringObject(choices[widget.value])
        annot[NameObject(I)] = ArrayObject([NumberObject(widget.value)])
        if not need_appearances:
            annot[NameObject(AP)] = TextStringObject(choices[widget.value])


def get_dropdown_value(annot: DictionaryObject, widget: Dropdown) -> None:
    """
    Retrieves the selected value of a dropdown annotation and updates the widget.

    This function determines the current value of the dropdown, considering
    whether it's a child annotation or a top-level one. It then iterates
    through the widget's choices to find a match and sets the widget's
    value to the index of the matched choice.

    Args:
        annot (DictionaryObject): The dropdown annotation dictionary.
        widget (Dropdown): The Dropdown widget object to update with the retrieved value.
    """
    if Parent in annot and T not in annot:
        to_compare = annot.get(Parent, {}).get(V)
    else:
        to_compare = annot.get(V)

    for i, each in enumerate(widget.choices):
        if each == to_compare:
            widget.value = i or None  # set None when 0


def update_text_value(
    annot: DictionaryObject, widget: Text, need_appearances: bool
) -> None:
    """
    Updates the value of a text annotation, setting the text content.

    This function modifies the value (V) and appearance (AP) of the text
    annotation to reflect the new text content.

    Args:
        annot (DictionaryObject): The text annotation dictionary.
        widget (Text): The Text widget object containing the text value.
        need_appearances (bool): If True, skips updating the appearance stream (AP) to
            maintain compatibility with Adobe Reader's behavior for certain fields.
    """
    if Parent in annot and T not in annot:
        annot[NameObject(Parent)][NameObject(V)] = TextStringObject(widget.value)
        if not need_appearances:
            annot[NameObject(AP)] = TextStringObject(widget.value)
    else:
        annot[NameObject(V)] = TextStringObject(widget.value)
        if not need_appearances:
            annot[NameObject(AP)] = TextStringObject(widget.value)


def get_text_value(annot: DictionaryObject, widget: Text) -> None:
    """
    Retrieves the text value of a text annotation and updates the widget.

    This function determines the current text value of the annotation, considering
    whether it's a child annotation or a top-level one, and then sets the
    widget's value accordingly.

    Args:
        annot (DictionaryObject): The text annotation dictionary.
        widget (Text): The Text widget object to update with the retrieved value.
    """
    if Parent in annot and T not in annot:
        widget.value = annot[Parent].get(V)
    else:
        widget.value = annot.get(V)


def get_text_field_max_length(widget: dict) -> Union[int, None]:
    """
    Extracts the maximum length of a text field from a widget dictionary.

    Args:
        widget (dict): The widget dictionary to extract the max length from.

    Returns:
        Union[int, None]: The maximum length of the text field, or None
            if the max length is not specified.
    """
    return int(widget[MaxLen]) or None if MaxLen in widget else None


def get_text_field_alignment(widget: dict) -> Union[int, None]:
    """
    Extracts the alignment (quadding) of a text field from a widget dictionary.

    Args:
        widget (dict): The widget dictionary to extract the alignment from.

    Returns:
        Union[int, None]: The alignment of the text field, or None if the
            alignment is not specified or is the default (left-justified).
    """
    return int(widget.get(Q, 0)) or None


def get_dropdown_choices(widget: dict) -> Union[Tuple[str, ...], None]:
    """
    Extracts the choices from a dropdown widget dictionary.

    This function extracts the choices from a dropdown widget dictionary.

    Args:
        widget (dict): The widget dictionary to extract the choices from.

    Returns:
        Union[Tuple[str, ...], None]: A tuple of strings representing the choices in the dropdown, or None if the choices are not specified.
    """
    return tuple(
        (
            each.get_object()
            if isinstance(each.get_object(), str)
            else str(each.get_object()[1])
        )
        for each in extract_widget_property(
            widget, DROPDOWN_CHOICE_PATTERNS, None, None
        )
    )


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


def get_field_rect(annot: DictionaryObject) -> Tuple[float, float, float, float]:
    """
    Retrieves the normalized rectangular bounding box of a field annotation.

    The PDF 'Rect' entry contains [llx, lly, urx, ury] (lower-left x, y, upper-right x, y).
    This function converts it to a normalized tuple of (x, y, width, height) in float format.

    Args:
        annot (DictionaryObject): The annotation dictionary containing the 'Rect' key.

    Returns:
        tuple: A tuple (x, y, width, height) representing the field's bounding box.
    """
    rect = annot[Rect]

    return (
        float(rect[0].get_object()),
        float(rect[1].get_object()),
        float(abs(rect[2].get_object() - rect[0].get_object())),
        float(abs(rect[3].get_object() - rect[1].get_object())),
    )


def get_field_hidden(annot: DictionaryObject) -> bool:
    """
    Checks if a field annotation is hidden.

    This function inspects the 'F' (flags) entry of the annotation
    dictionary to determine if the Hidden flag is set.

    Args:
        annot (DictionaryObject): The annotation dictionary.

    Returns:
        bool: True if the field is hidden, False otherwise.
    """
    return bool(int(annot[NameObject(F)] if F in annot else 0) & HIDDEN)
