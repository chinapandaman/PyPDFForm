# -*- coding: utf-8 -*-
"""
This module defines widget hooks that allow for dynamic modification of PDF form fields.

It provides functions to trigger these hooks, enabling changes to text field properties
like font, font size, color, alignment, and multiline settings, as well as the size
of checkbox and radio button widgets. It also provides functions for changing the
editability of generic and radio button widgets. These hooks are triggered during
the PDF form filling process, allowing for customization of the form's appearance
and behavior.
"""

import sys
from collections.abc import Callable
from io import BytesIO
from typing import Any, NamedTuple, Optional, TextIO, cast

from pypdf import PdfWriter
from pypdf.generic import (
    ArrayObject,
    ByteStringObject,
    DictionaryObject,
    FloatObject,
    NameObject,
    NumberObject,
    TextStringObject,
)

from .adapter import fp_or_f_obj_or_f_content_to_content
from .constants import (
    AA,
    COMB,
    DA,
    DEFAULT_APPEARANCE_HOOKS,
    HIDDEN,
    JS,
    MULTILINE,
    READ_ONLY,
    REQUIRED,
    TU,
    AcroForm,
    Action,
    Annots,
    Bl,
    D,
    E,
    F,
    Ff,
    Fo,
    JavaScript,
    MaxLen,
    Opt,
    Q,
    Rect,
    S,
    Type,
    U,
    X,
)
from .default_appearance import (
    change_font,
    change_font_color,
    change_font_size,
    read_default_appearance,
)
from .middleware.dropdown import DropdownOption
from .patterns import (
    check_field_flag,
    get_field_tooltip,
    get_widget_field,
    get_widget_key,
    parse_alignment,
    parse_field_flags,
    parse_max_length,
    resolve_inherited_entry,
)
from .utils import get_dictionary, get_entry


class FontChange(NamedTuple):
    """
    A font assigned to a text field or dropdown, as the wrapper passes it to
    `update_text_field_font`.

    Attributes:
        name (str): The font as assigned, such as `Courier` or `/F1`.
        resource (Optional[str]): The resource name of the registered font or
            the font of the PDF with that name, such as `/F1`, or None when no
            font has it.
    """

    name: str
    resource: Optional[str]


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
    appearance or behavior. Hooks that change the default appearance also get
    the AcroForm dictionary, for its default. Widget hook queues are left
    unchanged, so the caller can clear them once the modified PDF is returned,
    or revert them if a hook or writing the PDF raises.

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
    output = PdfWriter(BytesIO(pdf))
    acroform = get_dictionary(output.root_object, AcroForm) or DictionaryObject()

    for page in output.pages:
        for annot in page.get(Annots, []):
            annot = cast(DictionaryObject, annot.get_object())
            key = get_widget_key(annot.get_object(), use_full_widget_name)

            widget = widgets.get(key)
            if widget is None or not widget.hooks_to_trigger:
                continue

            for hook, value in widget.hooks_to_trigger:
                function = getattr(sys.modules[__name__], hook)
                if hook in DEFAULT_APPEARANCE_HOOKS:
                    function(annot, value, acroform)
                else:
                    function(annot, value)

    with BytesIO() as f:
        output.write(f)
        f.seek(0)
        return f.read()


def _update_field_flag(annot: DictionaryObject, flag: int, should_set: bool) -> None:
    """
    Sets or unsets a bit flag for a form field annotation.

    The field flags (`/Ff`) are resolved from the widget and the fields along
    its `/Parent` chain, so a widget's own flags take precedence. The changed
    flags replace the widget's own, and are otherwise written to the field the
    widget belongs to, as `get_widget_field` describes, with the bits it
    inherited, so fields above it, which other fields can share, are not
    changed. All other bits are preserved. Hooks change a PDF writer that is
    written only when every hook succeeds, so an error leaves the PDF
    unchanged.

    Args:
        annot (DictionaryObject): The annotation dictionary for the form field.
        flag (int): The bit flag to set or unset.
        should_set (bool): True to set the flag, False to unset it.

    Raises:
        ValueError: If the `/Parent` chain has a cycle before any flags are
            found, or the flags found aren't a number.
    """
    entry = resolve_inherited_entry(annot, Ff, None)
    flags = parse_field_flags(entry.value)
    entry.target[NameObject(Ff)] = NumberObject(
        flags | flag if should_set else flags & ~flag
    )


def _set_field_entry(annot: DictionaryObject, key: str, value: NumberObject) -> None:
    """
    Sets an inheritable field entry, such as `/Q`, for a widget.

    The entry is resolved from the widget and the fields along its `/Parent`
    chain, as `resolve_inherited_entry` describes, without an AcroForm
    default. The new value replaces the widget's own, and is otherwise
    written to the field the widget belongs to, as `get_widget_field`
    describes, so fields above it, which other fields can share, are not
    changed. Hooks
    change a PDF writer that is written only when every hook succeeds, so an
    error leaves the PDF unchanged.

    Args:
        annot (DictionaryObject): The widget annotation dictionary.
        key (str): The entry to set, such as `/MaxLen` or `/Q`.
        value (NumberObject): The new value.

    Raises:
        ValueError: If the `/Parent` chain has a cycle before the entry is
            found.
    """
    resolve_inherited_entry(annot, key, None).target[NameObject(key)] = value


def _read_alignment(annot: DictionaryObject) -> int | None:
    """
    Reads the alignment of a widget's field, as `get_text_field_alignment`
    does, except that a `/Parent` cycle raises.

    Args:
        annot (DictionaryObject): The widget annotation dictionary.

    Returns:
        int | None: The alignment, or None if the field has none.

    Raises:
        ValueError: If the `/Parent` chain has a cycle before `/Q` is found.
    """
    return parse_alignment(resolve_inherited_entry(annot, Q, None).value)


def _read_max_length(annot: DictionaryObject) -> int | None:
    """
    Reads the maximum length of a widget's field, as
    `get_text_field_max_length` does, except that a `/Parent` cycle raises.

    Args:
        annot (DictionaryObject): The widget annotation dictionary.

    Returns:
        int | None: The maximum length, or None if the field has none.

    Raises:
        ValueError: If the `/Parent` chain has a cycle before `/MaxLen` is
            found.
    """
    return parse_max_length(resolve_inherited_entry(annot, MaxLen, None).value)


def _remove_field_entry(
    annot: DictionaryObject, key: str, read: Callable[[DictionaryObject], Any]
) -> None:
    """
    Removes a field entry from a widget and its own field.

    The widget's own field is the field it belongs to, as `get_widget_field`
    describes. The entry is removed from the widget and that field, so the
    field no longer has it, even when it was stored on the parent of a widget.
    Fields above the widget's own field can be shared with other fields, so
    they are never changed. If the field still has a value afterwards, one of
    them supplies it, and an error is raised. Hooks change a PDF writer that
    is written only when every hook succeeds, so raising discards the removal.

    Args:
        annot (DictionaryObject): The widget annotation dictionary.
        key (str): The entry to remove, such as `/MaxLen`, `/Q`, or `/TU`.
        read (Callable[[DictionaryObject], Any]): Reads the field's value from
            the widget as its property does, such as `_read_alignment`, None
            when it has none, raising `ValueError` for a `/Parent` cycle.

    Raises:
        ValueError: If a field above the widget's own field supplies a value,
            or the `/Parent` chain has a cycle before one is found.
    """
    for each in (annot, get_widget_field(annot)):
        each.pop(NameObject(key), None)

    try:
        value = read(annot)
    except ValueError as error:
        msg = f"Cannot remove {key}: the /Parent chain of the field has a cycle."
        raise ValueError(msg) from error
    if value is not None:
        msg = f"Cannot remove {key}: a parent field shared with other fields sets it."
        raise ValueError(msg)


def _update_default_appearance(
    annot: DictionaryObject,
    acroform: DictionaryObject,
    change: Callable[[object], str | bytes],
) -> None:
    """
    Changes the default appearance (`/DA`) of a widget.

    The `/DA` is resolved from the widget, the fields along its `/Parent`
    chain, and then the AcroForm default, so a widget's own `/DA` takes
    precedence. The changed `/DA` replaces the widget's own, and is otherwise
    written to the field the widget belongs to, as `get_widget_field`
    describes, so fields above it, which other fields can share, and the
    AcroForm default are not changed. The change is computed before anything is
    written, and hooks change a PDF writer that is written only when every
    hook succeeds, so an error leaves the PDF unchanged.

    Args:
        annot (DictionaryObject): The widget annotation dictionary.
        acroform (DictionaryObject): The AcroForm dictionary, for its default.
        change (Callable[[object], str | bytes]): Returns the changed `/DA`
            for the resolved `/DA` value, such as `change_font_size`, as bytes
            when it was a byte string.

    Raises:
        ValueError: If no `/DA` is set, the `/Parent` chain has a cycle, or
            the `/DA` can't be changed, such as one without a `Tf` operator.
    """
    entry = resolve_inherited_entry(annot, DA, acroform)
    if entry.value is None:
        msg = "Cannot change /DA: neither the field nor the form sets one."
        raise ValueError(msg)

    result = change(entry.value)
    entry.target[NameObject(DA)] = (
        ByteStringObject(result)
        if isinstance(result, bytes)
        else TextStringObject(result)
    )


def update_text_field_font(
    annot: DictionaryObject, val: str | FontChange, acroform: DictionaryObject
) -> None:
    """
    Updates the font of a text field annotation.

    This function changes the font of the field's default appearance (`/DA`),
    as `_update_default_appearance` describes. A name without a slash that is
    the font this annotation's `/DA` already uses, such as `Courier` in
    `Courier 12 Tf`, leaves the `/DA` unchanged, even when a registered font
    has that name. Otherwise, the font is the resource name of the registered
    font or font of the PDF with that name, which the wrapper looks up, or the
    name itself, which must then be a resource name starting with a slash "/".
    Each annotation is decided by its own `/DA`, as it is when the hook runs,
    so the widgets of a field, or an earlier change of the same font, can
    give different results.

    Args:
        annot (DictionaryObject): The annotation dictionary for the text field.
        val (str | FontChange): The new font, with the resource name the
            wrapper found for it, or a resource name starting with "/".
        acroform (DictionaryObject): The AcroForm dictionary, for its default.

    Raises:
        ValueError: If the font is neither the one this annotation uses, the
            name of a font with a resource name, nor a resource name starting
            with "/", or the `/DA` can't be resolved or has no `Tf` operator
            with a font and a numeric size.
    """
    change = val if isinstance(val, FontChange) else FontChange(val, None)
    if (
        not change.name.startswith("/")
        and read_default_appearance(
            resolve_inherited_entry(annot, DA, acroform).value
        ).font
        == change.name
    ):
        return

    font = change.resource if change.resource is not None else change.name
    if not font.startswith("/"):
        msg = (
            f"Cannot change the font: {font!r} is not a registered font, a font "
            "of the PDF, or a font resource name starting with '/'."
        )
        raise ValueError(msg)
    _update_default_appearance(annot, acroform, lambda da: change_font(da, font))


def update_text_field_font_size(
    annot: DictionaryObject, val: float, acroform: DictionaryObject
) -> None:
    """
    Updates the font size of a text field annotation.

    This function changes the font size of the field's default appearance
    (`/DA`), as `_update_default_appearance` describes.

    Args:
        annot (DictionaryObject): The annotation dictionary for the text field.
        val (float): The new font size to use for the text field.
        acroform (DictionaryObject): The AcroForm dictionary, for its default.

    Raises:
        ValueError: If the `/DA` can't be resolved or has no `Tf` operator
            with a font and a numeric size.
    """
    _update_default_appearance(annot, acroform, lambda da: change_font_size(da, val))


def update_text_field_font_color(
    annot: DictionaryObject, val: tuple, acroform: DictionaryObject
) -> None:
    """
    Updates the font color of a text field annotation.

    This function changes the fill color of the field's default appearance
    (`/DA`) to an RGB color, as `_update_default_appearance` describes.

    Args:
        annot (DictionaryObject): The annotation dictionary for the text field.
        val (tuple): The new font color as an RGB tuple (e.g., (1, 0, 0) for red).
        acroform (DictionaryObject): The AcroForm dictionary, for its default.

    Raises:
        ValueError: If the `/DA` can't be resolved, or has a fill color
            operator without the numeric operands it takes.
    """
    _update_default_appearance(annot, acroform, lambda da: change_font_color(da, val))


def update_text_field_alignment(annot: DictionaryObject, val: int) -> None:
    """
    Updates the text alignment of a text field annotation.

    This function modifies the Q entry of the field, as `_set_field_entry`
    does, to change the text alignment of the text field. None removes the
    entry from the annotation and its own field, since the field's alignment
    is inheritable.

    Args:
        annot (DictionaryObject): The annotation dictionary for the text field.
        val (int | None): The new alignment value (0=Left, 1=Center, 2=Right),
            or None to remove it.

    Raises:
        ValueError: If None is given and a parent field shared with other
            fields sets the alignment, or the `/Parent` chain has a cycle.
    """
    if val is None:
        _remove_field_entry(annot, Q, _read_alignment)
    else:
        _set_field_entry(annot, Q, NumberObject(val))


def update_text_field_multiline(annot: DictionaryObject, val: bool) -> None:
    """
    Updates the multiline property of a text field annotation.

    This function modifies the Ff (flags) entry of the field, as
    `_update_field_flag` does, to enable or disable the multiline property of
    the text field. Disabling a field that is not multiline leaves the
    annotation unchanged.

    Args:
        annot (DictionaryObject): The annotation dictionary for the text field.
        val (bool): True to enable multiline, False to disable.

    Raises:
        ValueError: If the flags are changed and the `/Parent` chain has a
            cycle before any flags are found.
    """
    if val or check_field_flag(annot, MULTILINE):
        _update_field_flag(annot, MULTILINE, bool(val))


def update_text_field_comb(annot: DictionaryObject, val: bool) -> None:
    """
    Updates the comb property of a text field annotation.

    This function modifies the Ff (flags) entry of the field, as
    `_update_field_flag` does, to enable or disable the comb property of the
    text field, which displays fixed character positions for fields with a
    maximum length. Disabling a field that is not a comb field leaves the
    annotation unchanged.

    Args:
        annot (DictionaryObject): The annotation dictionary for the text field.
        val (bool): True to enable comb, False to disable.

    Raises:
        ValueError: If the flags are changed and the `/Parent` chain has a
            cycle before any flags are found.
    """
    if val or check_field_flag(annot, COMB):
        _update_field_flag(annot, COMB, bool(val))


def update_text_field_max_length(annot: DictionaryObject, val: int) -> None:
    """
    Updates the maximum length of a text field annotation.

    This function sets the MaxLen entry of the field, as `_set_field_entry`
    does, which specifies the maximum number of characters that can be
    entered into the text field. None removes the entry from the annotation
    and its own field, since the field's maximum length is inheritable.

    Args:
        annot (DictionaryObject): The annotation dictionary for the text field.
        val (int | None): The maximum number of characters allowed in the text
            field, or None to remove the limit.

    Raises:
        ValueError: If None is given and a parent field shared with other
            fields sets the maximum length, or the `/Parent` chain has a cycle.
    """
    if val is None:
        _remove_field_entry(annot, MaxLen, _read_max_length)
    else:
        _set_field_entry(annot, MaxLen, NumberObject(val))


def _normalize_geometry_value(val: int | float) -> float:
    """
    Normalizes scalar geometry to a float before modifying an annotation.

    Values are validated when they are assigned to the widget, by
    `Widget.validate_geometry_value`.

    Args:
        val (int | float): The coordinate or dimension to normalize.

    Returns:
        float: The normalized geometry value.
    """
    return float(val)


def update_check_radio_size(annot: DictionaryObject, val: int | float) -> None:
    """
    Updates the size of a check box or radio button annotation.

    This function modifies the Rect entry in the annotation dictionary to change
    the size of the check box or radio button. The lower-left corner stays fixed
    and the upper-right corner is moved to make the field square.

    Args:
        annot (DictionaryObject): The annotation dictionary for the check box or
            radio button.
        val (int | float): The new size (width and height) for the check box or radio button.
    """
    val = _normalize_geometry_value(val)
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

    This function modifies the Opt entry of the field to change the available
    choices in the dropdown field. The options are resolved from the widget and
    the fields along its `/Parent` chain, as `get_dropdown_choices` reads them,
    and the new options replace the widget's own, and are otherwise written to
    the field the widget belongs to, as `resolve_inherited_entry` describes,
    so every widget of the field gets them and fields above it, which other
    fields can share, are not changed. String choices
    use the same export and display value. Two-item sequences are written as
    `[export, display]` PDF option arrays from the user-facing
    `(display, export)` order.

    Args:
        annot (DictionaryObject): The annotation dictionary for the dropdown field.
        val (list): A list of strings or tuples representing the new choices for the dropdown.

    Raises:
        ValueError: If the `/Parent` chain has a cycle before any options are
            found.
    """
    resolve_inherited_entry(annot, Opt, None).target[NameObject(Opt)] = ArrayObject(
        [DropdownOption.from_choice(each).to_pdf() for each in val]
    )


def update_field_readonly(annot: DictionaryObject, val: bool) -> None:
    """
    Sets or unsets the ReadOnly flag on a form field annotation,
    making it read-only or editable based on the `val` parameter.

    This function modifies the Ff (flags) entry of the field, as
    `_update_field_flag` does, to set or unset the ReadOnly flag, preventing or
    allowing the user from interacting with the form field.

    Args:
        annot (DictionaryObject): The annotation dictionary.
        val (bool): True to make the field read-only, False to make it editable.

    Raises:
        ValueError: If the `/Parent` chain has a cycle before any flags are
            found.
    """
    _update_field_flag(annot, READ_ONLY, val)


def update_field_x(annot: DictionaryObject, val: int | float) -> None:
    """
    Updates the X-coordinate (horizontal position) of a form field annotation.

    This function modifies the 'Rect' entry of the annotation dictionary to change
    the left X-coordinate of the field and adjusts the right X-coordinate by the
    same delta to maintain the field's width. Integer and float inputs are
    normalized to floats before updating the rectangle.

    Args:
        annot (DictionaryObject): The annotation dictionary for the form field.
        val (int | float): The new X-coordinate for the left edge of the field.
    """
    val = _normalize_geometry_value(val)
    diff = val - annot[Rect][0]
    annot[NameObject(Rect)][0] = FloatObject(val)
    annot[NameObject(Rect)][2] = FloatObject(annot[NameObject(Rect)][2] + diff)


def update_field_y(annot: DictionaryObject, val: int | float) -> None:
    """
    Updates the Y-coordinate (vertical position) of a form field annotation.

    This function modifies the 'Rect' entry of the annotation dictionary to change
    the bottom Y-coordinate of the field and adjusts the top Y-coordinate by the
    same delta to maintain the field's height. Integer and float inputs are
    normalized to floats before updating the rectangle.

    Args:
        annot (DictionaryObject): The annotation dictionary for the form field.
        val (int | float): The new Y-coordinate for the bottom edge of the field.
    """
    val = _normalize_geometry_value(val)
    diff = val - annot[Rect][1]
    annot[NameObject(Rect)][1] = FloatObject(val)
    annot[NameObject(Rect)][3] = FloatObject(annot[NameObject(Rect)][3] + diff)


def update_field_width(annot: DictionaryObject, val: int | float) -> None:
    """
    Updates the width of a form field annotation.

    This function modifies the 'Rect' entry of the annotation dictionary to set
    the new width of the field, adjusting the rightmost coordinate while keeping
    the leftmost coordinate fixed. Integer and float inputs are normalized to
    floats before updating the rectangle.

    Args:
        annot (DictionaryObject): The annotation dictionary for the form field.
        val (int | float): The new width of the field.
    """
    val = _normalize_geometry_value(val)
    annot[NameObject(Rect)][2] = FloatObject(annot[Rect][0] + val)


def update_field_height(annot: DictionaryObject, val: int | float) -> None:
    """
    Updates the height of a form field annotation.

    This function modifies the 'Rect' entry of the annotation dictionary to set
    the new height of the field, adjusting the topmost coordinate while keeping
    the bottommost coordinate fixed. Integer and float inputs are normalized to
    floats before updating the rectangle.

    Args:
        annot (DictionaryObject): The annotation dictionary for the form field.
        val (int | float): The new height of the field.
    """
    val = _normalize_geometry_value(val)
    annot[NameObject(Rect)][3] = FloatObject(annot[Rect][1] + val)


def update_field_tooltip(annot: DictionaryObject, val: str) -> None:
    """
    Updates the tooltip (alternate field name) of a form field annotation.

    This function sets the 'TU' entry, which provides a text string that can be
    used as a tooltip for the field, on the widget when it has a tooltip of its
    own, which `get_field_tooltip` reads first, and otherwise on the field it
    belongs to, as `get_widget_field` describes. None or an empty string
    removes the tooltip from the annotation and its own field. A tooltip isn't inherited, as `get_field_tooltip` describes, so
    fields above the widget's own field are neither read nor changed.

    Args:
        annot (DictionaryObject): The annotation dictionary for the form field.
        val (str | None): The new tooltip string for the field, or None to
            remove it.
    """
    if val:
        target = annot if get_entry(annot, TU) else get_widget_field(annot)
        target[NameObject(TU)] = TextStringObject(val)
    else:
        _remove_field_entry(annot, TU, get_field_tooltip)


def update_field_required(annot: DictionaryObject, val: bool) -> None:
    """
    Updates the 'Required' flag of a form field annotation.

    This function modifies the Ff (flags) entry of the field, as
    `_update_field_flag` does, to set or unset the 'Required' flag, making the
    field mandatory or optional.

    Args:
        annot (DictionaryObject): The annotation dictionary for the form field.
        val (bool): True to set the field as required, False to make it optional.

    Raises:
        ValueError: If the `/Parent` chain has a cycle before any flags are
            found.
    """
    _update_field_flag(annot, REQUIRED, val)


def update_field_hidden(annot: DictionaryObject, val: bool) -> None:
    """
    Updates the 'Hidden' flag of a form field annotation.

    This function modifies the F entry in the annotation dictionary to set
    or unset the 'Hidden' flag, making the field invisible or visible.

    Args:
        annot (DictionaryObject): The annotation dictionary for the form field.
        val (bool): True to hide the field, False to make it visible.
    """
    annot[NameObject(F)] = NumberObject(
        (
            int(annot.get(NameObject(F), 0)) | HIDDEN
            if val
            else int(annot.get(NameObject(F), 0)) & ~HIDDEN
        )
    )


def _update_field_javascript(
    annot: DictionaryObject, trigger_event: str, val: str | TextIO
) -> None:
    """
    Updates a specific JavaScript action for a form field annotation.

    This internal helper function adds or updates a JavaScript action in the
    annotation's additional actions dictionary (AA) for a specific trigger event.
    The JavaScript value can be literal code, a path, or a readable object; it is
    normalized to string content before being written.

    Args:
        annot (DictionaryObject): The annotation dictionary for the form field.
        trigger_event (str): The event that triggers the JavaScript action
            (e.g., E for enter, X for exit, D for down, U for up, Fo for focus, Bl for blur).
        val (str | TextIO): The JavaScript code to execute. Can be a string
            containing the code or a file-like object/path to a file containing the code.
    """
    if AA not in annot:
        annot[NameObject(AA)] = DictionaryObject()

    annot[NameObject(AA)][NameObject(trigger_event)] = DictionaryObject()
    annot[NameObject(AA)][NameObject(trigger_event)][NameObject(Type)] = NameObject(
        Action
    )
    annot[NameObject(AA)][NameObject(trigger_event)][NameObject(S)] = NameObject(
        JavaScript
    )
    annot[NameObject(AA)][NameObject(trigger_event)][NameObject(JS)] = TextStringObject(
        fp_or_f_obj_or_f_content_to_content(val)
    )


def update_field_on_hovered_over_javascript(
    annot: DictionaryObject, val: str | TextIO
) -> None:
    """
    Updates the JavaScript action triggered when the mouse enters the field area.

    This function sets the 'E' (Enter) entry in the annotation's additional actions
    dictionary, specifying JavaScript code to execute when the cursor enters the field.

    Args:
        annot (DictionaryObject): The annotation dictionary for the form field.
        val (str | TextIO): The JavaScript code to execute.
    """
    _update_field_javascript(annot, E, val)


def update_field_on_hovered_off_javascript(
    annot: DictionaryObject, val: str | TextIO
) -> None:
    """
    Updates the JavaScript action triggered when the mouse exits the field area.

    This function sets the 'X' (Exit) entry in the annotation's additional actions
    dictionary, specifying JavaScript code to execute when the cursor leaves the field.

    Args:
        annot (DictionaryObject): The annotation dictionary for the form field.
        val (str | TextIO): The JavaScript code to execute.
    """
    _update_field_javascript(annot, X, val)


def update_field_on_mouse_pressed_javascript(
    annot: DictionaryObject, val: str | TextIO
) -> None:
    """
    Updates the JavaScript action triggered when the mouse button is pressed down inside the field.

    This function sets the 'D' (Down) entry in the annotation's additional actions
    dictionary, specifying JavaScript code to execute when the mouse button is pressed.

    Args:
        annot (DictionaryObject): The annotation dictionary for the form field.
        val (str | TextIO): The JavaScript code to execute.
    """
    _update_field_javascript(annot, D, val)


def update_field_on_mouse_released_javascript(
    annot: DictionaryObject, val: str | TextIO
) -> None:
    """
    Updates the JavaScript action triggered when the mouse button is released inside the field.

    This function sets the 'U' (Up) entry in the annotation's additional actions
    dictionary, specifying JavaScript code to execute when the mouse button is released.

    Args:
        annot (DictionaryObject): The annotation dictionary for the form field.
        val (str | TextIO): The JavaScript code to execute.
    """
    _update_field_javascript(annot, U, val)


def update_field_on_focused_javascript(
    annot: DictionaryObject, val: str | TextIO
) -> None:
    """
    Updates the JavaScript action triggered when the field receives input focus.

    This function sets the 'Fo' (Focus) entry in the annotation's additional actions
    dictionary, specifying JavaScript code to execute when the field gains focus.

    Args:
        annot (DictionaryObject): The annotation dictionary for the form field.
        val (str | TextIO): The JavaScript code to execute.
    """
    _update_field_javascript(annot, Fo, val)


def update_field_on_blurred_javascript(
    annot: DictionaryObject, val: str | TextIO
) -> None:
    """
    Updates the JavaScript action triggered when the field loses input focus.

    This function sets the 'Bl' (Blur) entry in the annotation's additional actions
    dictionary, specifying JavaScript code to execute when the field loses focus.

    Args:
        annot (DictionaryObject): The annotation dictionary for the form field.
        val (str | TextIO): The JavaScript code to execute.
    """
    _update_field_javascript(annot, Bl, val)
