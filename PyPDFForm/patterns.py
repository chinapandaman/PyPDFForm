# -*- coding: utf-8 -*-
"""
This module defines patterns and utility functions for interacting with PDF form fields.

It includes patterns for identifying different types of widgets (e.g., text fields,
checkboxes, radio buttons, dropdowns, images, and signatures) based on their
properties in the PDF's annotation dictionary. It also provides utility functions
for updating these widgets.
"""
# TODO: The `WIDGET_TYPE_PATTERNS` list is iterated through to determine widget types. For very large numbers of annotations or complex pattern matching, consider optimizing this lookup, perhaps by pre-compiling regexes or using a more efficient data structure if the patterns allow.
# TODO: In `update_checkbox_value` and `update_radio_value`, iterating through `annot[AP][N]` to find the correct appearance state might be slow if `N` contains many entries. If possible, a direct lookup or a more optimized search could improve performance.
# TODO: In `update_dropdown_value`, the list comprehension for `ArrayObject` can be computationally intensive for dropdowns with many choices, as it creates new `TextStringObject` and `ArrayObject` instances for each choice. Consider optimizing this if dropdowns have a very large number of options.
# TODO: The `get_checkbox_value` and `get_radio_value` functions involve dictionary lookups and comparisons. While generally fast, repeated calls in a tight loop for many widgets could accumulate overhead.

from typing import Union

from pypdf.generic import (
    ArrayObject,
    DictionaryObject,
    NameObject,
    NumberObject,
    TextStringObject,
)

from .constants import (
    AP,
    AS,
    DV,
    FT,
    IMAGE_FIELD_IDENTIFIER,
    JS,
    SLASH,
    TU,
    A,
    Btn,
    Ch,
    I,
    N,
    Off,
    Opt,
    Parent,
    Sig,
    T,
    Tx,
    V,
    Yes,
)
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
            {AS: (Yes, Off, SLASH)},
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
            {AS: (Yes, Off, SLASH)},
        ),
        Radio,
    ),
]

WIDGET_KEY_PATTERNS = [
    {T: True},
    {Parent: {T: True}},
]

WIDGET_KEY_PATTERN_NO_PARENT = [{T: True}]

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
