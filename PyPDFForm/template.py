# -*- coding: utf-8 -*-

from functools import lru_cache
from io import BytesIO
from typing import Dict, List, Tuple, Union, cast

from pypdf import PdfReader, PdfWriter
from pypdf.generic import DictionaryObject

from .constants import WIDGET_TYPES, Annots, MaxLen, Parent, T
from .middleware.dropdown import Dropdown
from .middleware.radio import Radio
from .middleware.text import Text
from .patterns import (DROPDOWN_CHOICE_PATTERNS, WIDGET_DESCRIPTION_PATTERNS,
                       WIDGET_KEY_PATTERNS, WIDGET_TYPE_PATTERNS,
                       update_annotation_name)
from .utils import extract_widget_property, find_pattern_match, stream_to_io


def build_widgets(
    pdf_stream: bytes,
    use_full_widget_name: bool,
) -> Dict[str, WIDGET_TYPES]:
    results = {}

    for widgets in get_widgets_by_page(pdf_stream).values():
        for widget in widgets:
            key = get_widget_key(widget, use_full_widget_name)
            _widget = construct_widget(widget, key)
            if _widget is not None:
                _widget.desc = extract_widget_property(
                    widget, WIDGET_DESCRIPTION_PATTERNS, None, str
                )

                if isinstance(_widget, Text):
                    # mostly for schema for now
                    _widget.max_length = get_text_field_max_length(widget)

                if isinstance(_widget, Dropdown):
                    # actually used for filling value
                    _widget.choices = get_dropdown_choices(widget)

                if isinstance(_widget, Radio):
                    if key not in results:
                        results[key] = _widget

                    # for schema
                    results[key].number_of_options += 1
                    continue

                results[key] = _widget

    return results


@lru_cache()
def get_widgets_by_page(pdf: bytes) -> Dict[int, List[dict]]:
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


def get_widget_key(widget: dict, use_full_widget_name: bool) -> str:
    key = extract_widget_property(widget, WIDGET_KEY_PATTERNS, None, str)
    if not use_full_widget_name:
        return key

    if (
        Parent in widget
        and T in widget[Parent].get_object()
        and widget[Parent].get_object()[T] != key  # sejda case
    ):
        key = (
            f"{get_widget_key(widget[Parent].get_object(), use_full_widget_name)}.{key}"
        )

    return key


def construct_widget(widget: dict, key: str) -> Union[WIDGET_TYPES, None]:
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
    return int(widget[MaxLen]) or None if MaxLen in widget else None


def get_dropdown_choices(widget: dict) -> Union[Tuple[str, ...], None]:
    return tuple(
        (each if isinstance(each, str) else str(each[1]))
        for each in extract_widget_property(
            widget, DROPDOWN_CHOICE_PATTERNS, None, None
        )
    )


def update_widget_keys(
    template: bytes,
    widgets: Dict[str, WIDGET_TYPES],
    old_keys: List[str],
    new_keys: List[str],
    indices: List[int],
) -> bytes:
    # pylint: disable=R0801

    pdf = PdfReader(stream_to_io(template))
    out = PdfWriter()
    out.append(pdf)

    for i, old_key in enumerate(old_keys):
        index = indices[i]
        new_key = new_keys[i]
        tracker = -1
        for page in out.pages:
            for annot in page.get(Annots, []):
                annot = cast(DictionaryObject, annot.get_object())
                key = get_widget_key(annot.get_object(), False)

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
