# -*- coding: utf-8 -*-
"""Provides template processing utilities for PDF forms.

This module contains functions for:
- Building and managing PDF form widgets
- Handling widget properties and attributes
- Processing text fields and paragraphs
- Managing widget keys and names
- Supporting comb fields and multiline text
"""

from functools import lru_cache
from io import BytesIO
from sys import maxsize
from typing import Dict, List, Tuple, Union, cast

from pypdf import PdfReader, PdfWriter
from pypdf.generic import DictionaryObject
from reportlab.pdfbase.pdfmetrics import stringWidth

from .constants import (COMB, DEFAULT_BORDER_WIDTH, DEFAULT_FONT_SIZE,
                        MULTILINE, NEW_LINE_SYMBOL, WIDGET_TYPES, Annots,
                        MaxLen, Parent, Rect, T)
from .font import (adjust_paragraph_font_size, adjust_text_field_font_size,
                   auto_detect_font, get_text_field_font_color,
                   get_text_field_font_size, text_field_font_size)
from .middleware.checkbox import Checkbox
from .middleware.dropdown import Dropdown
from .middleware.radio import Radio
from .middleware.text import Text
from .patterns import (BACKGROUND_COLOR_PATTERNS, BORDER_COLOR_PATTERNS,
                       BORDER_DASH_ARRAY_PATTERNS, BORDER_STYLE_PATTERNS,
                       BORDER_WIDTH_PATTERNS, BUTTON_STYLE_PATTERNS,
                       DROPDOWN_CHOICE_PATTERNS, TEXT_FIELD_FLAG_PATTERNS,
                       WIDGET_DESCRIPTION_PATTERNS, WIDGET_KEY_PATTERNS,
                       WIDGET_TYPE_PATTERNS, update_annotation_name)
from .utils import (extract_widget_property, find_pattern_match, handle_color,
                    stream_to_io)


def set_character_x_paddings(
    pdf_stream: bytes, widgets: Dict[str, WIDGET_TYPES]
) -> Dict[str, WIDGET_TYPES]:
    """Calculates and sets character spacing for comb text fields.

    Args:
        pdf_stream: PDF form as bytes
        widgets: Dictionary of widget middleware objects

    Returns:
        Dict[str, WIDGET_TYPES]: Updated widgets with character paddings
    """

    for _widgets in get_widgets_by_page(pdf_stream).values():
        for widget in _widgets:
            key = extract_widget_property(widget, WIDGET_KEY_PATTERNS, None, str)
            _widget = widgets[key]

            if isinstance(_widget, Text) and _widget.comb is True:
                _widget.character_paddings = get_character_x_paddings(widget, _widget)

    return widgets


def build_widgets(
    pdf_stream: bytes,
    use_full_widget_name: bool,
    render_widgets: bool,
) -> Dict[str, WIDGET_TYPES]:
    """Constructs widget middleware objects from a PDF form.

    Args:
        pdf_stream: PDF form as bytes
        use_full_widget_name: Whether to include parent widget names
        render_widgets: Whether widgets should be rendered visibly

    Returns:
        Dict[str, WIDGET_TYPES]: Dictionary mapping field names to widgets
    """

    results = {}

    for widgets in get_widgets_by_page(pdf_stream).values():
        for widget in widgets:
            key = extract_widget_property(widget, WIDGET_KEY_PATTERNS, None, str)
            _widget = construct_widget(widget, key)
            if _widget is not None:
                if use_full_widget_name:
                    _widget.full_name = get_widget_full_key(widget)

                _widget.render_widget = render_widgets
                _widget.desc = extract_widget_property(
                    widget, WIDGET_DESCRIPTION_PATTERNS, None, str
                )
                _widget.border_color = extract_widget_property(
                    widget, BORDER_COLOR_PATTERNS, None, handle_color
                )
                _widget.background_color = extract_widget_property(
                    widget, BACKGROUND_COLOR_PATTERNS, None, handle_color
                )
                _widget.border_width = extract_widget_property(
                    widget, BORDER_WIDTH_PATTERNS, DEFAULT_BORDER_WIDTH, float
                )
                _widget.border_style = extract_widget_property(
                    widget, BORDER_STYLE_PATTERNS, None, str
                )
                _widget.dash_array = extract_widget_property(
                    widget, BORDER_DASH_ARRAY_PATTERNS, None, list
                )

                if isinstance(_widget, Text):
                    _widget.max_length = get_text_field_max_length(widget)
                    if _widget.max_length is not None and is_text_field_comb(widget):
                        _widget.comb = True

                if isinstance(_widget, (Checkbox, Radio)):
                    _widget.button_style = (
                        extract_widget_property(
                            widget, BUTTON_STYLE_PATTERNS, None, str
                        )
                        or _widget.button_style
                    )

                if isinstance(_widget, Dropdown):
                    _widget.choices = get_dropdown_choices(widget)

                if isinstance(_widget, Radio):
                    if key not in results:
                        results[key] = _widget

                    results[key].number_of_options += 1
                    continue

                results[key] = _widget
                if _widget.full_name is not None and use_full_widget_name:
                    results[_widget.full_name] = results[key]
    return results


def dropdown_to_text(dropdown: Dropdown) -> Text:
    """Converts a dropdown widget to a text widget while preserving properties.

    Args:
        dropdown: Dropdown widget to convert

    Returns:
        Text: New text widget with dropdown's selected value and styling
    """

    result = Text(dropdown.name)
    result.border_color = dropdown.border_color
    result.background_color = dropdown.background_color
    result.border_width = dropdown.border_width
    result.render_widget = dropdown.render_widget

    if dropdown.value is not None:
        result.value = (
            dropdown.choices[dropdown.value]
            if dropdown.value < len(dropdown.choices)
            else ""
        )

    return result


def update_text_field_attributes(
    template_stream: bytes,
    widgets: Dict[str, WIDGET_TYPES],
) -> None:
    """Updates text field properties based on PDF template settings.

    Handles:
    - Font detection and sizing
    - Color properties
    - Paragraph wrapping
    - Auto font size adjustment

    Args:
        template_stream: PDF form as bytes
        widgets: Dictionary of widget middleware objects
    """

    for _widgets in get_widgets_by_page(template_stream).values():
        for _widget in _widgets:
            key = extract_widget_property(_widget, WIDGET_KEY_PATTERNS, None, str)

            if isinstance(widgets[key], Text):
                should_adjust_font_size = False
                is_paragraph = is_text_multiline(_widget)
                if widgets[key].font is None:
                    widgets[key].font = auto_detect_font(_widget)
                if widgets[key].font_size is None:
                    template_font_size = get_text_field_font_size(_widget)
                    widgets[key].font_size = template_font_size or (
                        text_field_font_size(_widget)
                        if not is_paragraph
                        else DEFAULT_FONT_SIZE
                    )
                    should_adjust_font_size = (
                        not template_font_size and widgets[key].max_length is None
                    )
                if widgets[key].font_color is None:
                    widgets[key].font_color = get_text_field_font_color(_widget)
                if is_paragraph and widgets[key].text_wrap_length is None:
                    widgets[key].text_lines = get_paragraph_lines(_widget, widgets[key])
                    widgets[key].text_wrap_length = get_paragraph_auto_wrap_length(
                        widgets[key]
                    )
                if widgets[key].value and should_adjust_font_size:
                    if is_paragraph:
                        adjust_paragraph_font_size(_widget, widgets[key])
                    else:
                        adjust_text_field_font_size(_widget, widgets[key])


@lru_cache()
def get_widgets_by_page(pdf: bytes) -> Dict[int, List[dict]]:
    """Extracts all form widgets from a PDF grouped by page number.

    Args:
        pdf: PDF form as bytes

    Returns:
        Dict[int, List[dict]]: Mapping of page numbers to widget dictionaries
    """

    pdf_file = PdfReader(stream_to_io(pdf))

    result = {}

    for i, page in enumerate(pdf_file.pages):
        widgets = page.annotations
        result[i + 1] = []
        if widgets:
            for widget in widgets:
                widget = dict(widget.get_object())
                for each in WIDGET_TYPE_PATTERNS:
                    patterns = each[0]
                    check = True
                    for pattern in patterns:
                        check = check and find_pattern_match(pattern, widget)
                    if check:
                        result[i + 1].append(widget)
                        break

    return result


def get_widget_full_key(widget: dict) -> Union[str, None]:
    """Constructs a widget's full hierarchical key including parent names.

    Args:
        widget: PDF widget dictionary

    Returns:
        Union[str, None]: Full key in format "parent.child" if parent exists,
            otherwise None
    """

    key = extract_widget_property(widget, WIDGET_KEY_PATTERNS, None, str)

    if (
        Parent in widget
        and T in widget[Parent].get_object()
        and widget[Parent].get_object()[T] != key
    ):
        return f"{widget[Parent].get_object()[T]}.{key}"

    return key


def construct_widget(widget: dict, key: str) -> Union[WIDGET_TYPES, None]:
    """Creates appropriate widget middleware based on PDF widget type.

    Args:
        widget: PDF widget dictionary
        key: Field name/key for the widget

    Returns:
        Union[WIDGET_TYPES, None]: Appropriate widget middleware instance
            or None if type not recognized
    """

    result = None
    for each in WIDGET_TYPE_PATTERNS:
        patterns, _type = each
        check = True
        for pattern in patterns:
            check = check and find_pattern_match(pattern, widget)
        if check:
            result = _type(key)
            break
    return result


def get_text_field_max_length(widget: dict) -> Union[int, None]:
    """Extracts max length constraint from a text field widget.

    Args:
        widget: PDF widget dictionary

    Returns:
        Union[int, None]: Max character length if specified, otherwise None
    """

    return int(widget[MaxLen]) or None if MaxLen in widget else None


def check_field_flag_bit(widget: dict, bit: int) -> bool:
    """Tests whether a specific flag bit is set in a widget's field flags.

    Args:
        widget: PDF widget dictionary
        bit: Flag bit to check (e.g. COMB, MULTILINE)

    Returns:
        bool: True if the bit is set, False otherwise
    """

    field_flag = extract_widget_property(widget, TEXT_FIELD_FLAG_PATTERNS, None, int)

    if field_flag is None:
        return False

    return bool(int(field_flag) & bit)


def is_text_field_comb(widget: dict) -> bool:
    """Determines if a text field uses comb formatting (fixed character spacing).

    Args:
        widget: PDF widget dictionary

    Returns:
        bool: True if field uses comb formatting
    """

    return check_field_flag_bit(widget, COMB)


def is_text_multiline(widget: dict) -> bool:
    """Determines if a text field supports multiple lines/paragraphs.

    Args:
        widget: PDF widget dictionary

    Returns:
        bool: True if field supports multiline text
    """

    return check_field_flag_bit(widget, MULTILINE)


def get_dropdown_choices(widget: dict) -> Union[Tuple[str, ...], None]:
    """Extracts available choices from a dropdown widget.

    Args:
        widget: PDF widget dictionary

    Returns:
        Union[Tuple[str, ...], None]: Tuple of choice strings if found,
            otherwise None
    """

    return tuple(
        (each if isinstance(each, str) else str(each[1]))
        for each in extract_widget_property(
            widget, DROPDOWN_CHOICE_PATTERNS, None, None
        )
    )


def get_char_rect_width(widget: dict, widget_middleware: Text) -> float:
    """Calculates per-character width for comb text fields.

    Args:
        widget: PDF widget dictionary
        widget_middleware: Text middleware instance

    Returns:
        float: Width in points allocated per character
    """

    rect_width = abs(float(widget[Rect][0]) - float(widget[Rect][2]))
    return rect_width / widget_middleware.max_length


def get_character_x_paddings(widget: dict, widget_middleware: Text) -> List[float]:
    """Calculates horizontal positioning for each character in comb fields.

    Args:
        widget: PDF widget dictionary
        widget_middleware: Text middleware instance

    Returns:
        List[float]: X-offsets for centering each character in its comb cell
    """

    length = min(len(widget_middleware.value or ""), widget_middleware.max_length)
    char_rect_width = get_char_rect_width(widget, widget_middleware)

    result = []

    current_x = 0
    for char in (widget_middleware.value or "")[:length]:
        current_mid_point = current_x + char_rect_width / 2
        result.append(
            current_mid_point
            - stringWidth(char, widget_middleware.font, widget_middleware.font_size) / 2
        )
        current_x += char_rect_width

    return result


def split_characters_into_lines(
    split_by_new_line_symbol: List[str], middleware: Text, width: float
) -> List[str]:
    """Splits text into lines that fit within a paragraph field's width.

    Args:
        split_by_new_line_symbol: Text already split by newlines
        middleware: Text middleware with font properties
        width: Available width in points

    Returns:
        List[str]: Lines of text fitting within the specified width
    """

    lines = []
    for line in split_by_new_line_symbol:
        characters = line.split(" ")
        current_line = ""
        for each in characters:
            line_extended = f"{current_line} {each}" if current_line else each
            if (
                stringWidth(line_extended, middleware.font, middleware.font_size)
                <= width
            ):
                current_line = line_extended
            else:
                lines.append(current_line)
                current_line = each
        lines.append(
            current_line + NEW_LINE_SYMBOL
            if len(split_by_new_line_symbol) > 1
            else current_line
        )

    return lines


def adjust_each_line(lines: List[str], middleware: Text, width: float) -> List[str]:
    """Optimizes line breaks to minimize empty space in paragraph fields.

    Args:
        lines: Text lines from split_characters_into_lines()
        middleware: Text middleware with font properties
        width: Available width in points

    Returns:
        List[str]: Optimized lines with balanced word wrapping
    """

    result = []
    for each in lines:
        tracker = ""
        for char in each:
            check = tracker + char
            if stringWidth(check, middleware.font, middleware.font_size) > width:
                result.append(tracker)
                tracker = char
            else:
                tracker = check

        each = tracker
        if each:
            if (
                result
                and stringWidth(
                    f"{each} {result[-1]}",
                    middleware.font,
                    middleware.font_size,
                )
                <= width
                and NEW_LINE_SYMBOL not in result[-1]
            ):
                result[-1] = f"{result[-1]}{each} "
            else:
                result.append(f"{each} ")

    for i, each in enumerate(result):
        result[i] = each.replace(NEW_LINE_SYMBOL, "")

    if result:
        result[-1] = result[-1][:-1]

    return result


def get_paragraph_lines(widget: dict, widget_middleware: Text) -> List[str]:
    """Generates properly wrapped lines for a paragraph text field.

    Args:
        widget: PDF widget dictionary
        widget_middleware: Text middleware instance

    Returns:
        List[str]: Wrapped lines fitting the paragraph field dimensions
    """

    value = widget_middleware.value or ""
    if widget_middleware.max_length is not None:
        value = value[: widget_middleware.max_length]

    width = abs(float(widget[Rect][0]) - float(widget[Rect][2]))

    split_by_new_line_symbol = value.split(NEW_LINE_SYMBOL)
    lines = split_characters_into_lines(
        split_by_new_line_symbol, widget_middleware, width
    )

    return adjust_each_line(lines, widget_middleware, width)


def get_paragraph_auto_wrap_length(widget_middleware: Text) -> int:
    """Determines optimal line length for paragraph text wrapping.

    Args:
        widget_middleware: Text middleware instance

    Returns:
        int: Suggested maximum characters per line
    """

    result = maxsize
    for line in widget_middleware.text_lines:
        result = min(result, len(line))

    return result


def update_widget_keys(
    template: bytes,
    widgets: Dict[str, WIDGET_TYPES],
    old_keys: List[str],
    new_keys: List[str],
    indices: List[int],
) -> bytes:
    """Renames widget fields in a PDF template.

    Args:
        template: PDF form as bytes
        widgets: Dictionary of widget middleware
        old_keys: List of current field names
        new_keys: List of new field names
        indices: List of indices for handling radio button groups

    Returns:
        bytes: Modified PDF with updated field names
    """
    # pylint: disable=R0801

    pdf = PdfReader(stream_to_io(template))
    out = PdfWriter()
    out.append(pdf)

    for i, old_key in enumerate(old_keys):
        index = indices[i]
        new_key = new_keys[i]
        tracker = -1
        for page in out.pages:
            for annot in page.get(Annots, []):  # noqa
                annot = cast(DictionaryObject, annot.get_object())
                key = extract_widget_property(
                    annot.get_object(), WIDGET_KEY_PATTERNS, None, str
                )

                widget = widgets.get(key)
                if widget is None:
                    continue

                if old_key != key:
                    continue

                tracker += 1
                if not isinstance(widget, Radio) and tracker != index:
                    continue

                update_annotation_name(annot, new_key)

    with BytesIO() as f:
        out.write(f)
        f.seek(0)
        return f.read()
