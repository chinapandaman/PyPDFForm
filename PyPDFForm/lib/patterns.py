# -*- coding: utf-8 -*-
"""
This module defines patterns and utility functions for interacting with PDF form fields.

It includes patterns for identifying different types of widgets (e.g., text fields,
checkboxes, radio buttons, dropdowns, images, and signatures) based on their
properties in the PDF's annotation dictionary. It also provides utility functions
for updating these widgets, and resolves the entries that a field inherits from
its ancestors and the AcroForm, such as its default appearance and flags.
"""

from typing import Any, NamedTuple, Optional, Sequence, Tuple, cast

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
from .utils import (
    find_pattern_match,
    get_array,
    get_dictionary,
    get_entry,
    has_name,
)

# an image field is a pushbutton, so it is found by the action that imports
# its image before its field type is read
IMAGE_PATTERN = {A: {JS: IMAGE_IMPORT_JAVASCRIPT}}

# the middleware type of each field type (/FT), except buttons, which
# _get_button_type tells apart
FIELD_TYPES = ((Sig, Signature), (Tx, Text), (Ch, Dropdown))


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


def get_widget_field(annot: DictionaryObject) -> DictionaryObject:
    """
    Gets the field that a widget belongs to, the widget's own field, which
    holds its value (`/V`), name (`/T`), tooltip (`/TU`), and the inherited
    entries changed for it, as `resolve_inherited_entry` describes.

    It is the widget's parent when the widget has no name, as `has_name`
    describes, and its `/Parent` is a dictionary, even when that parent has
    no name either. Otherwise it is the widget itself, which is merged with
    its field, so a null `/Parent`, or one that isn't a dictionary, is
    absent. Fields above it can be shared with other fields, so changing the
    widget never changes them.

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
    widget of its field, takes the value inherited from the fields above it,
    as `resolve_inherited_entry` resolves it, when that names one of the
    widget's appearance states, since other widgets of the field can have
    other on states. A null value is absent, and a `/Parent` cycle before a
    value is found reads as no value.

    Args:
        annot (DictionaryObject): The checkbox annotation dictionary.

    Returns:
        bool | None: True if the checkbox is checked, None otherwise.
    """
    value = get_entry(annot, V)
    if value is None:
        value = _get_inherited_value(annot, V)
        appearance = get_dictionary(annot, AP)
        states = get_dictionary(appearance, N) if appearance is not None else None
        if not isinstance(value, NameObject) or states is None or value not in states:
            value = None

    return True if value not in (None, Off) else None


def update_radio_value(
    annot: DictionaryObject, options: Sequence[DictionaryObject]
) -> None:
    """
    Selects a radio button and clears every other widget in its group.

    The group is the field the widget belongs to, as `get_widget_field`
    describes: its parent, or the widget itself when it has a name. The
    selected widget's non-Off normal appearance supplies the field's value (V)
    and the widget's appearance state (AS), even when the field doesn't list
    the widget in its `/Kids`. The other widgets of the field receive /Off:
    those in its `/Kids`, including those on other pages, but not a kid with
    a name, which is a field of its own, and those among `options` that
    belong to the field, which its `/Kids` may not list. The field's Opt
    export mapping is preserved.

    Args:
        annot (DictionaryObject): The radio button annotation dictionary.
        options (Sequence[DictionaryObject]): Other widgets that may belong
            to the field, such as the options of its group on every page.
    """
    for each in annot[AP][N]:
        if str(each) != Off:
            field = get_widget_field(annot)
            field[NameObject(V)] = NameObject(each)
            kids = [reference.get_object() for reference in get_array(field, Kids)]
            others = [
                kid
                for kid in kids
                if isinstance(kid, DictionaryObject) and not has_name(kid)
            ] + [option for option in options if get_widget_field(option) is field]
            for other in others:
                if other is not annot:
                    other[NameObject(AS)] = NameObject(Off)
            annot[NameObject(AS)] = NameObject(each)
            break


def get_radio_value(annot: DictionaryObject) -> bool:
    """
    Retrieves the boolean value of a radio button annotation.

    This function iterates through the appearance states (AP) of the radio button
    annotation. If the value (V) of the field it belongs to, as
    `get_widget_field` describes, matches any of these appearance states
    other than `/Off`, it means the radio button is selected, and True is
    returned. Otherwise, False is returned. A field without a value of its
    own takes the one inherited from the fields above it, as
    `resolve_inherited_entry` resolves it, and a `/Parent` cycle before a
    value is found reads as no value.

    Args:
        annot (DictionaryObject): The radio button annotation dictionary.

    Returns:
        bool: True if the radio button is selected, False otherwise.
    """
    value = _get_inherited_value(get_widget_field(annot), V)
    return any(each != Off and value == each for each in annot.get(AP, {}).get(N, []))


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
    field = get_widget_field(annot)
    field[NameObject(V)] = TextStringObject(option.export)
    field[NameObject(I)] = ArrayObject([NumberObject(widget.value)])
    if not need_appearances:
        annot[NameObject(AP)] = TextStringObject(option.display)


def get_dropdown_value(annot: DictionaryObject, widget: Dropdown) -> None:
    """
    Retrieves the selected value of a dropdown annotation and updates the widget.

    This function reads the value (V) and selected indices (I) of the field the
    widget belongs to, as `get_widget_field` describes. A field without a
    value of its own takes the one inherited from the fields above it, as
    `resolve_inherited_entry` resolves it, and a `/Parent` cycle before a
    value is found reads as no value. The indices aren't inherited, so they
    are read from the field itself. V is matched against export values, then
    displayed text, and I chooses among options with the same value. A
    matching option sets the widget's value to its index, including zero for
    the first option. If no option matches, the widget's value is left
    unchanged; an initially unselected widget remains None.

    Args:
        annot (DictionaryObject): The dropdown annotation dictionary.
        widget (Dropdown): The Dropdown widget object to update with the retrieved value.
    """
    field = get_widget_field(annot)
    value = _get_inherited_value(field, V)
    indices = get_entry(field, I)
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
    get_widget_field(annot)[NameObject(V)] = TextStringObject(widget.value)
    if not need_appearances:
        annot[NameObject(AP)] = TextStringObject(widget.value)


def get_text_value(annot: DictionaryObject, widget: Text) -> None:
    """
    Retrieves the text value of a text annotation and updates the widget.

    The value (V) is read from the field the widget belongs to, as
    `get_widget_field` describes. A field without a value of its own takes
    the one inherited from the fields above it, as `resolve_inherited_entry`
    resolves it. A null value is absent, and a `/Parent` cycle before a value
    is found reads as no value.

    Args:
        annot (DictionaryObject): The text annotation dictionary.
        widget (Text): The Text widget object to update with the retrieved value.
    """
    widget.value = _get_inherited_value(get_widget_field(annot), V)


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
    equal, or as a `(display, export)` tuple when they differ. The options
    (`/Opt`) are resolved from the widget and the fields along its `/Parent`
    chain, as `resolve_inherited_entry` resolves them, without an AcroForm
    default, so an explicitly empty option array on the widget or a lower
    field is kept even when a field above it has options. Missing or null
    options, options that aren't an array, and a `/Parent` cycle before any
    are found produce an empty tuple.

    Args:
        widget (dict): The widget dictionary to extract the choices from.

    Returns:
        Tuple[str | Tuple[str, str], ...]: The dropdown choices, or an empty
            tuple when none exist.
    """
    choices = _get_inherited_value(cast(DictionaryObject, widget), Opt)
    if not isinstance(choices, ArrayObject):
        return ()

    return tuple(DropdownOption.from_pdf(each).choice for each in choices)


def get_field_tooltip(widget: dict) -> str | None:
    """
    Reads the tooltip (`/TU`) of the field a widget belongs to.

    The tooltip is the field's alternate name, which ISO 32000-1 doesn't let
    a field inherit, so it is read from the widget, as earlier versions wrote
    it there, and then from the field the widget belongs to, as
    `get_widget_field` describes, but never from a field above that. A
    missing, null, or empty tooltip is absent.

    Args:
        widget (dict): The widget annotation dictionary.

    Returns:
        str | None: The tooltip, or None when neither sets one.
    """
    annot = cast(DictionaryObject, widget)
    for node in (annot, get_widget_field(annot)):
        value = get_entry(node, TU)
        if value:
            return str(value)

    return None


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
    get_widget_field(annot)[NameObject(T)] = TextStringObject(val)


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
            written: the widget when the value is its own, and otherwise the
            field the widget belongs to, as `get_widget_field` describes, so
            that the fields above it, which other fields can share, and the
            AcroForm default are never changed.
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
    ISO 32000-1 specifies, so the lookup continues past it. A `/Parent`
    already reached is a cycle, and raises. Otherwise, the chain ends before
    the `/Parent` of a dictionary with a name when that parent is a widget
    annotation: it can't be a field above it, but is a field of its own,
    such as a checkbox whose widget is merged with it, so the two don't share
    entries. A widget without a name still belongs to its parent, as
    `get_widget_field` describes. Not every entry is inherited, or has an
    AcroForm default, so callers choose the entries they resolve.

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
    own_field = get_widget_field(widget)
    seen = {id(widget)}
    node = widget
    while True:
        value = get_entry(node, key)
        if value is not None:
            return InheritedEntry(value, widget if node is widget else own_field)

        parent = get_dictionary(node, Parent)
        if parent is None:
            break
        if id(parent) in seen:
            msg = f"Cannot resolve {key}: the /Parent chain of the field has a cycle."
            raise ValueError(msg)
        if has_name(node) and get_entry(parent, Subtype) == Widget:
            break
        seen.add(id(parent))
        node = parent

    return InheritedEntry(
        get_entry(acroform, key) if acroform is not None else None, own_field
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
    number raise, as `parse_field_flags` describes.

    Args:
        widget (DictionaryObject): The widget annotation.
        flag (int): The bit flag to check.

    Returns:
        bool: True if the flag is set.

    Raises:
        ValueError: If the resolved flags aren't a number.
    """
    return bool(parse_field_flags(_get_inherited_value(widget, Ff)) & flag)


def parse_field_flags(value: Any) -> int:
    """
    Converts resolved field flags (`/Ff`) to an integer.

    Flags that aren't a number aren't read as no flags, since the field's
    actual flags are unknown, so opening the PDF or changing a flag raises
    instead, wherever along the `/Parent` chain they are found.

    Args:
        value (Any): The resolved flags, or None when nothing sets them.

    Returns:
        int: The flags, 0 when nothing sets them.

    Raises:
        ValueError: If the flags aren't a number.
    """
    if value is None:
        return 0
    # a PDF boolean is a BooleanObject, which isn't an int
    if isinstance(value, (int, float)):
        return int(value)

    # malformed PDF data, raised like the other errors of field entries
    msg = f"Cannot read the field flags: /Ff {value!r} is not a number."
    raise ValueError(msg)


def is_pushbutton(widget: DictionaryObject) -> bool:
    """
    Checks whether the field of a widget annotation is a pushbutton.

    The flag is read from the field the widget belongs to, as
    `get_widget_field` describes, and the fields above it, as the radio flag
    is, so every widget of a field has the same type. When that field is an
    empty parent, which has no flags, it is read from the widget instead.

    Args:
        widget (DictionaryObject): The widget annotation.

    Returns:
        bool: True if the field sets the Pushbutton flag.
    """
    # an empty parent is falsy, so the widget's own flags are read
    return check_field_flag(get_widget_field(widget) or widget, PUSHBUTTON)


def get_widget_type(widget: dict) -> type | None:
    """
    Gets the middleware type of a widget annotation from its fixed entries.

    Image fields, which are pushbuttons, are found by their action first.
    Other widgets get the middleware type of their field type (`/FT`), which
    is resolved from the widget and the fields along its `/Parent` chain, so
    the type of the widget or a lower field takes precedence over the ones
    above it. The AcroForm has no default for it, and a `/Parent` cycle before
    it is found reads as no type, as a missing or null one does. Buttons are
    told apart by `_get_button_type`, which doesn't read their appearance
    state (`/AS`), since filling changes it: a checked checkbox whose on state
    isn't `/Yes` is still a checkbox, and a field keeps its type as it is
    filled, rebuilt, or copied.

    Args:
        widget (dict): The widget annotation dictionary.

    Returns:
        type | None: The middleware type, such as `Checkbox`, or None if the
            annotation is not a supported widget.
    """
    if get_entry(widget, Subtype) != Widget:
        return None
    if find_pattern_match(IMAGE_PATTERN, widget):
        return Image

    field_type = _get_inherited_value(widget, FT)
    if field_type == Btn:
        return _get_button_type(widget)
    for value, _type in FIELD_TYPES:
        if field_type == value:
            return _type

    return None


def _get_button_type(widget: DictionaryObject) -> type | None:
    """
    Gets the middleware type of a widget whose field type is `/Btn`.

    A button without an appearance state (`/AS`), or whose field sets the
    Pushbutton flag, has no value, so it is neither a checkbox nor a radio
    button. The state itself isn't read, since filling changes it, so a field
    keeps its type as it is filled, rebuilt, or copied.

    A widget with a name, or without a parent field, is a field of its own,
    as `get_widget_field` describes. It is a radio button with one option
    when its flags, resolved along its `/Parent` chain, set the radio flag,
    and a checkbox otherwise, even when its parent is a button field.

    A widget without a name is an option of its parent field. It is a radio
    button when it repeats the field type, as ReportLab writes options, and
    the field is a button field, or when the field sets the radio flag. That
    flag is resolved from the field and the fields above it, not the option's
    own flags, so every option of a group has one type. Otherwise, since not
    every PDF sets the radio flag, it is a checkbox when the field's default
    value (`/DV`), resolved from the field and the fields above it, is `/Yes`
    or `/Off`, and a radio button when it isn't.

    Args:
        widget (DictionaryObject): The widget annotation.

    Returns:
        type | None: `Checkbox`, `Radio`, or None when the widget is neither.
    """
    if AS not in widget or is_pushbutton(widget):
        return None

    field = get_dictionary(widget, Parent)
    if field is None or has_name(widget):
        return Radio if check_field_flag(widget, RADIO) else Checkbox

    if get_entry(widget, FT) == Btn:
        # reportlab creation pattern
        return Radio if _get_inherited_value(field, FT) == Btn else Checkbox
    if check_field_flag(field, RADIO):
        return Radio
    # a radio group's /DV can be /Yes or /Off too, so the radio flag comes first
    return Checkbox if _get_inherited_value(field, DV) in (Yes, Off) else Radio


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
