# -*- coding: utf-8 -*-
"""
This module defines patterns and utility functions for interacting with PDF form fields.

It includes patterns for identifying different types of widgets (e.g., text fields,
checkboxes, radio buttons, dropdowns, images, and signatures) based on their
properties in the PDF's annotation dictionary. It also provides utility functions
for updating these widgets, and resolves the entries that a field inherits from
its ancestors and the AcroForm, such as its default appearance and flags.
"""

from typing import Any, NamedTuple, Optional, Tuple, cast

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
    DA,
    DV,
    FT,
    HIDDEN,
    IMAGE_IMPORT_JAVASCRIPT,
    JS,
    PUSHBUTTON,
    RADIO,
    TU,
    A,
    Btn,
    Ch,
    F,
    Ff,
    I,
    Kids,
    MaxLen,
    N,
    Off,
    Opt,
    Parent,
    Q,
    Rect,
    Sig,
    Subtype,
    T,
    Tx,
    V,
    Widget,
    Yes,
)
from .default_appearance import TextStyle, read_default_appearance
from .middleware.checkbox import Checkbox
from .middleware.dropdown import Dropdown, DropdownOption
from .middleware.image import Image
from .middleware.radio import Radio
from .middleware.signature import Signature
from .middleware.text import Text
from .utils import extract_widget_property, get_dictionary, get_entry, has_name

# get_widget_type reads /AS as /Off, so an /AS pattern requires an appearance
# state, whichever it is, and a field's type doesn't change as it is filled
WIDGET_TYPE_PATTERNS = [
    (
        (
            {Subtype: Widget},
            {A: {JS: IMAGE_IMPORT_JAVASCRIPT}},
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
            {AS: (Yes, Off)},
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
        # a radio group's /DV can be /Yes or /Off too, so check it before the /DV rule
        (
            {Subtype: Widget},
            {Parent: {FT: Btn}},
            {AS: (Yes, Off)},
            # the radio flag is resolved from the shared field and its ancestors,
            # not a widget's own /Ff, so every option of a group has one type
            {Parent: lambda parent: check_field_flag(parent, RADIO)},
        ),
        Radio,
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
            {AS: (Yes, Off)},
        ),
        Radio,
    ),
]

WIDGET_DESCRIPTION_PATTERNS = [{TU: True}, {Parent: {TU: True}}]

DROPDOWN_CHOICE_PATTERNS = [
    {Opt: True},
    {Parent: {Opt: True}},
]


def get_widget_key(widget: dict, use_full_widget_name: bool) -> str:
    """
    Extracts the widget key from a widget dictionary.

    The short key is the widget's name (`/T`), or its parent's when the widget
    has none. If `use_full_widget_name` is True, it constructs the full widget
    name by joining the names along the widget's `/Parent` chain with dots,
    outermost first, while handling child annotations that inherit the parent
    name. The chain ends at a parent without a name, at a parent with the same
    name as its child, and before a dictionary is reached a second time, the
    widget included, so each field in a `/Parent` cycle is named once and a
    widget without a name gets its field's key. Dictionaries are recognized by
    identity, so the widget must be the PDF's own object, not a copy of it. A
    null name is absent, as `has_name` describes.

    Args:
        widget (dict): The widget dictionary to extract the key from.
        use_full_widget_name (bool): Whether to use the full widget name
            (including parent names) as the widget key.

    Returns:
        str: The extracted widget key. Without full names, it is None when
            neither the widget nor its parent has a name.
    """
    key = get_entry(widget, T)
    parent = get_dictionary(widget, Parent)
    if not use_full_widget_name:
        if not key and parent is not None:
            key = get_entry(parent, T)
        # None when neither has a name
        return cast(str, str(key) if key else None)

    names = []
    seen = {id(widget)}
    while (
        parent is not None
        and id(parent) not in seen
        and has_name(parent)
        and get_entry(parent, T) != key  # sejda case
    ):
        if key is not None:
            names.append(str(key))
        seen.add(id(parent))
        key = get_entry(parent, T)
        parent = get_dictionary(parent, Parent)

    names.append(str(key) if key else "")
    return ".".join(reversed(names))


def _get_widget_field(annot: DictionaryObject) -> DictionaryObject:
    """
    Gets the field that a widget belongs to, which holds its value (`/V`) and
    name (`/T`).

    It is the widget's parent when the widget has no name, as `has_name`
    describes, and its `/Parent` is a dictionary. Otherwise it is the widget
    itself, which is merged with its field, so a null `/Parent`, or one that
    isn't a dictionary, is absent.

    Args:
        annot (DictionaryObject): The widget annotation dictionary.

    Returns:
        DictionaryObject: The parent field or the widget.
    """
    parent = get_dictionary(annot, Parent)
    return parent if parent is not None and not has_name(annot) else annot


def update_checkbox_value(annot: DictionaryObject, check: bool = False) -> None:
    """
    Updates the value of a checkbox annotation, setting it to checked or unchecked.

    This function modifies the appearance state (AS) and value (V) of the checkbox
    annotation to reflect the desired state. For a checked value, it selects the
    first non-`/Off` appearance state. For an unchecked value, it selects `/Off`.

    Args:
        annot (DictionaryObject): The checkbox annotation dictionary.
        check (bool): True to check the checkbox, False to uncheck it. Defaults to False.
    """
    for each in annot[AP][N]:
        if (check and str(each) != Off) or (not check and str(each) == Off):
            annot[NameObject(AS)] = NameObject(each)
            annot[NameObject(V)] = NameObject(each)
            break


def get_checkbox_value(annot: DictionaryObject) -> bool | None:
    """
    Retrieves the boolean value of a checkbox annotation.

    This function checks the value (V) of the checkbox annotation. If the value
    is not `/Off`, it means the checkbox is checked, and True is returned.
    Otherwise, if the value is `/Off` or not present, None is returned rather
    than False so unspecified fill data can be distinguished from an explicit
    unchecked value. A widget without a value of its own, such as a separate
    widget of its field, takes its field's value, inherited from the fields
    above it, when that names one of the widget's appearance states, since
    other widgets of the field can have other on states. A `/Parent` cycle
    before a value is found reads as no value.

    Args:
        annot (DictionaryObject): The checkbox annotation dictionary.

    Returns:
        bool | None: True if the checkbox is checked, None otherwise.
    """
    value = annot.get(V)
    if value is None:
        value = _get_inherited_value(annot, V)
        appearance = get_dictionary(annot, AP)
        states = get_dictionary(appearance, N) if appearance is not None else None
        if not isinstance(value, NameObject) or states is None or value not in states:
            value = None

    return True if value not in (None, Off) else None


def update_radio_value(annot: DictionaryObject) -> None:
    """
    Selects a radio button and clears every other widget in its group.

    The selected widget's non-Off normal appearance supplies the parent value
    (V) and selected appearance state (AS). All other children, including those
    on other pages, receive /Off. The parent's Opt export mapping is preserved.

    Args:
        annot (DictionaryObject): The radio button annotation dictionary.
    """
    for each in annot[AP][N]:
        if str(each) != Off:
            parent = annot[Parent]
            parent[NameObject(V)] = NameObject(each)
            for reference in parent[Kids]:
                child = reference.get_object()
                child[NameObject(AS)] = NameObject(each if child is annot else Off)
            break


def get_radio_value(annot: DictionaryObject) -> bool:
    """
    Retrieves the boolean value of a radio button annotation.

    This function iterates through the appearance states (AP) of the radio button
    annotation. If the value (V) of the parent dictionary matches any of these
    appearance states other than `/Off`, it means the radio button is selected, and
    True is returned. Otherwise, False is returned.

    Args:
        annot (DictionaryObject): The radio button annotation dictionary.

    Returns:
        bool: True if the radio button is selected, False otherwise.
    """
    for each in annot.get(AP, {}).get(N, []):
        if each != Off and annot.get(Parent, {}).get(V) == each:
            return True

    return False


def update_dropdown_value(
    annot: DictionaryObject, widget: Dropdown, need_appearances: bool
) -> None:
    """
    Updates the value of a dropdown annotation, selecting an option from the list.

    This function sets the field's value (V) to the selected option's export
    value and its selected index (I), and sets the annotation's appearance (AP)
    to the option's displayed text. Child annotations write V and I to their
    parent field dictionary. Appearance updates are skipped when
    `need_appearances` is enabled.

    Args:
        annot (DictionaryObject): The dropdown annotation dictionary.
        widget (Dropdown): The Dropdown widget object containing the selected value.
        need_appearances (bool): If True, skips updating the appearance stream (AP) to
            maintain compatibility with Adobe Reader's behavior for certain fields.
    """
    option = widget.options[widget.value]
    field = _get_widget_field(annot)
    field[NameObject(V)] = TextStringObject(option.export)
    field[NameObject(I)] = ArrayObject([NumberObject(widget.value)])
    if not need_appearances:
        annot[NameObject(AP)] = TextStringObject(option.display)


def get_dropdown_value(annot: DictionaryObject, widget: Dropdown) -> None:
    """
    Retrieves the selected value of a dropdown annotation and updates the widget.

    This function reads the field's value (V) and selected indices (I), from the
    parent field dictionary for child annotations. V is matched against export
    values, then displayed text, and I chooses among options with the same
    value. A matching option sets the widget's value to its index, including
    zero for the first option. If no option matches, the widget's value is left
    unchanged; an initially unselected widget remains None.

    Args:
        annot (DictionaryObject): The dropdown annotation dictionary.
        widget (Dropdown): The Dropdown widget object to update with the retrieved value.
    """
    field = _get_widget_field(annot)
    # discovered annotations are plain dictionaries, so entries can be references
    value = field[NameObject(V)].get_object() if V in field else None
    indices = field[NameObject(I)].get_object() if I in field else None
    index = widget.get_selected_index(value, indices)
    if index is not None:
        widget.value = index


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
    _get_widget_field(annot)[NameObject(V)] = TextStringObject(widget.value)
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
    widget.value = _get_widget_field(annot).get(V)


def get_text_field_max_length(widget: dict) -> int | None:
    """
    Extracts the maximum length of a text field from a widget dictionary.

    The maximum length (`/MaxLen`) is resolved from the widget and the fields
    along its `/Parent` chain, so the value of the widget or a lower field
    takes precedence over the ones above it. A `/Parent` cycle before it is
    found reads as no maximum length, and so does a value that
    `parse_max_length` rejects.

    Args:
        widget (dict): The widget dictionary to extract the max length from.

    Returns:
        int | None: The maximum length of the text field, or None
            if the max length is not specified.
    """
    return parse_max_length(_get_inherited_value(widget, MaxLen))


def get_text_field_alignment(widget: dict) -> int | None:
    """
    Extracts the alignment (quadding) of a text field from a widget dictionary.

    The alignment (`/Q`) is resolved from the widget and the fields along its
    `/Parent` chain, so the value of the widget or a lower field takes
    precedence over the ones above it. The AcroForm's default isn't read, so
    None means that no field sets an alignment and the form's default
    applies. A `/Parent` cycle before it is found reads as no alignment, and
    so does a value that `parse_alignment` rejects.

    Args:
        widget (dict): The widget dictionary to extract the alignment from.

    Returns:
        int | None: The alignment of the text field, or None if no field
            sets one.
    """
    return parse_alignment(_get_inherited_value(widget, Q))


def get_text_field_style(
    widget: dict, acroform: Optional[DictionaryObject]
) -> TextStyle:
    """
    Reads the font, font size, and font color of a text field or dropdown.

    They are read from the default appearance (`/DA`) that a change to them
    edits: the widget's own, or else the one of the nearest field along its
    `/Parent` chain, or else the AcroForm's, which is the document's default,
    as `read_default_appearance` describes. A `/Parent` cycle before a `/DA`
    is found reads as no `/DA`, so a PDF with one can still be opened;
    changing the style of such a field raises instead.

    Args:
        widget (dict): The widget dictionary.
        acroform (Optional[DictionaryObject]): The AcroForm dictionary, or
            None when the PDF has none.

    Returns:
        TextStyle: The font, font size, and font color, each None when the
            `/DA` doesn't set it.
    """
    try:
        default_appearance = resolve_inherited_entry(widget, DA, acroform).value
    except ValueError:
        default_appearance = None

    return read_default_appearance(default_appearance)


def parse_max_length(value: Any) -> int | None:
    """
    Reads a resolved `/MaxLen` as a maximum length.

    The first `/MaxLen` found decides, as viewers such as Poppler use it, so a
    malformed one isn't skipped for a valid one above it: it means that the
    field has no maximum length.

    Args:
        value (Any): The resolved `/MaxLen`, or None.

    Returns:
        int | None: The maximum length, or None unless the value is a whole
            number of at least 1.
    """
    max_length = _get_whole_number(value)
    return max_length if max_length is not None and max_length >= 1 else None


def parse_alignment(value: Any) -> int | None:
    """
    Reads a resolved `/Q` as an alignment.

    The first `/Q` found decides, as viewers such as Poppler use it, so a
    malformed one isn't skipped for a valid one above it: it means that the
    field has no alignment.

    Args:
        value (Any): The resolved `/Q`, or None.

    Returns:
        int | None: The alignment, or None unless the value is a whole number
            from 0 (left) to 2 (right).
    """
    alignment = _get_whole_number(value)
    return alignment if alignment is not None and 0 <= alignment <= 2 else None


def _get_whole_number(value: Any) -> int | None:
    """
    Converts a PDF number with a whole value, such as `2` or `2.0`, to an int.

    Args:
        value (Any): The value to convert.

    Returns:
        int | None: The number, or None for any other value, such as a name,
            a string, or a number with a fraction.
    """
    # a PDF boolean is a BooleanObject, which isn't an int
    if isinstance(value, int):
        return int(value)
    if isinstance(value, float) and value.is_integer():
        return int(value)
    return None


def get_dropdown_choices(widget: dict) -> Tuple[str | Tuple[str, str], ...]:
    """
    Extracts the choices from a dropdown widget dictionary.

    This function extracts the choices from a dropdown widget dictionary. Each
    option is returned as a string when its displayed text and export value are
    equal, or as a `(display, export)` tuple when they differ. Empty or missing
    options produce an empty tuple. An explicitly empty widget option array is
    preserved even when its parent has options.

    Args:
        widget (dict): The widget dictionary to extract the choices from.

    Returns:
        Tuple[str | Tuple[str, str], ...]: The dropdown choices, or an empty
            tuple when none exist.
    """
    choices = (
        widget[Opt]
        if Opt in widget
        else extract_widget_property(widget, DROPDOWN_CHOICE_PATTERNS, (), None)
    )
    return tuple(DropdownOption.from_pdf(each).choice for each in choices)


def update_annotation_name(annot: DictionaryObject, val: str) -> None:
    """
    Updates the name of an annotation, setting the T (title) entry.

    This function modifies the T (title) entry in the annotation dictionary to
    change the field name. For child annotations that inherit their name from a
    parent field dictionary, the parent name is updated instead.

    Args:
        annot (DictionaryObject): The annotation dictionary.
        val (str): The new name for the annotation.
    """
    _get_widget_field(annot)[NameObject(T)] = TextStringObject(val)


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


class InheritedEntry(NamedTuple):
    """
    An inheritable field entry resolved for a widget.

    Attributes:
        value (Any): The resolved value, or None when nothing sets the entry.
        target (DictionaryObject): Where a changed value for the widget is
            written: the dictionary that holds the value when it is the widget
            or below the widget's own field, or the widget's own field
            otherwise, so that fields shared with other fields and the AcroForm
            default are never changed. The widget's own field is the first
            dictionary along its `/Parent` chain, starting with the widget
            itself, that has a name (`T`), or the widget when none has one.
    """

    value: Any
    target: DictionaryObject


def resolve_inherited_entry(
    widget: DictionaryObject, key: str, acroform: Optional[DictionaryObject]
) -> InheritedEntry:
    """
    Resolves an inheritable field entry, such as `/DA`, for a widget.

    The entry is looked up on the widget, then on each field along its
    `/Parent` chain, then in the AcroForm, whose entry is the document's
    default. A value of its own on the widget or a lower field takes
    precedence over the ones above it. A null entry is treated as absent, as
    ISO 32000-1 specifies, so the lookup continues past it, and a null `/T`
    doesn't make a dictionary the widget's own field. Not every entry is
    inherited, or has an AcroForm default, so callers choose the entries they
    resolve.

    Args:
        widget (DictionaryObject): The widget annotation.
        key (str): The entry to resolve, such as `/DA`.
        acroform (Optional[DictionaryObject]): The AcroForm dictionary, or
            None for an entry without a document default.

    Returns:
        InheritedEntry: The resolved value and where to write a changed value.

    Raises:
        ValueError: If the `/Parent` chain has a cycle before the entry is
            found.
    """
    own_field = None
    seen = set()
    node = widget
    while node is not None:
        if id(node) in seen:
            msg = f"Cannot resolve {key}: the /Parent chain of the field has a cycle."
            raise ValueError(msg)
        seen.add(id(node))

        if own_field is None and has_name(node):
            own_field = node
        value = get_entry(node, key)
        if value is not None:
            return InheritedEntry(
                value, node if own_field is None or own_field is node else own_field
            )
        node = get_dictionary(node, Parent)

    return InheritedEntry(
        get_entry(acroform, key) if acroform is not None else None,
        own_field if own_field is not None else widget,
    )


def check_field_flag(widget: DictionaryObject, flag: int) -> bool:
    """
    Checks whether a field flag, such as `READ_ONLY`, is set for a widget.

    The field flags (`/Ff`) are resolved from the widget and the fields along
    its `/Parent` chain, so the flags of the widget or a lower field take
    precedence over the ones above it. The AcroForm has no default for them.
    A cycle in the chain before any flags are found reads as no flags, so a
    PDF with one can still be opened; changing a flag of such a field raises
    instead. Missing or null flags read as no flags; flags that aren't a
    number raise when converted.

    Args:
        widget (DictionaryObject): The widget annotation.
        flag (int): The bit flag to check.

    Returns:
        bool: True if the flag is set.
    """
    flags = _get_inherited_value(widget, Ff)
    return bool(int(flags if flags is not None else 0) & flag)


def is_pushbutton(widget: DictionaryObject) -> bool:
    """
    Checks whether the field of a widget annotation is a pushbutton.

    The flag is read from the field the widget belongs to, as
    `_get_widget_field` describes, and the fields above it, as the radio flag
    is, so every widget of a field has the same type. When that field is an
    empty parent, which has no flags, it is read from the widget instead.

    Args:
        widget (DictionaryObject): The widget annotation.

    Returns:
        bool: True if the field sets the Pushbutton flag.
    """
    # an empty parent is falsy, so the widget's own flags are read
    return check_field_flag(_get_widget_field(widget) or widget, PUSHBUTTON)


def _get_inherited_value(widget: DictionaryObject, key: str) -> Any:
    """
    Reads an inheritable entry of a widget without an AcroForm default.

    A `/Parent` cycle reached before the entry is found reads as no entry, so
    a PDF with one can still be opened; changing such an entry raises instead.

    Args:
        widget (DictionaryObject): The widget annotation.
        key (str): The entry to read, such as `/Ff`.

    Returns:
        Any: The resolved value, or None when nothing sets the entry.
    """
    try:
        return resolve_inherited_entry(widget, key, None).value
    except ValueError:
        return None
