# -*- coding: utf-8 -*-
"""
Module for maintaining the AcroForm field tree.

It removes form fields by key from page annotations, the field tree, and the
calculation order, lists the keys that removal can match, and detaches fields
and widgets from the tree. It also shares widget annotations and parent fields
stored inline, as earlier versions of PyPDFForm could save them, with their
copies in the field tree, so that a page and the field tree refer to one
object.
"""

from collections.abc import Callable
from functools import lru_cache
from io import BytesIO
from typing import Dict, List, Optional, cast

from pypdf import PdfReader, PdfWriter
from pypdf.generic import (
    ArrayObject,
    DictionaryObject,
    IndirectObject,
    NameObject,
    NullObject,
)

from .constants import (
    AA,
    CO,
    AcroForm,
    Annots,
    Fields,
    Kids,
    P,
    Parent,
    Rect,
    Subtype,
    T,
    Widget,
)
from .patterns import get_widget_key
from .utils import get_array, get_dictionary, get_version, set_version


def remove_widgets_by_keys(
    pdf: bytes, keys: List[str], use_full_widget_name: bool = False
) -> bytes:
    """
    Removes the form fields with the given keys from a PDF.

    A key matches a widget annotation on a page, or a terminal field anywhere
    in the AcroForm field tree, including fields without a widget on any page,
    using the same key rules as `build_widgets`. Matching widgets, and widgets
    of matching fields, are removed from page `/Annots` arrays, and the other
    annotations keep their references. Matching fields and widgets are then
    detached from the field tree with `detach_field`, and every detached field
    is removed from the AcroForm `/CO` calculation order, which is deleted
    when it becomes empty. Detached objects are no longer form fields, but
    other objects that refer to them, such as form actions, are not changed.
    Null entries, such as a null `/CO`, are treated as absent. `get_field_keys`
    lists the keys this function can match. If no keys are provided, the
    original PDF stream is returned unchanged.

    Args:
        pdf (bytes): The PDF stream to remove fields from.
        keys (List[str]): A list of field keys to remove.
        use_full_widget_name (bool): Whether to match fields by their full
            names, including parent names.

    Returns:
        bytes: The updated PDF stream with the matching fields removed.
    """
    if not keys:
        return pdf

    key_set = set(keys)
    writer = PdfWriter(BytesIO(pdf))
    acroform = get_dictionary(writer.root_object, AcroForm) or DictionaryObject()

    matched = {
        id(field): field
        for field in _get_terminal_fields(acroform)
        if get_widget_key(field, use_full_widget_name) in key_set
    }

    for page in writer.pages:
        annots = get_array(page, Annots)
        page_annots = ArrayObject([])
        for reference in annots:
            annot = reference.get_object()
            if _is_widget_annotation(annot) and (
                get_widget_key(annot, use_full_widget_name) in key_set
                or _has_ancestor_in(annot, matched)
            ):
                matched.setdefault(id(annot), annot)
            else:
                page_annots.append(reference)

        if len(page_annots) != len(annots):
            page[NameObject(Annots)] = page_annots

    detached = {}
    for field in matched.values():
        if not _has_ancestor_in(field, matched):
            detached.update((id(each), each) for each in detach_field(writer, field))

    calculation_order = get_array(acroform, CO)
    if calculation_order:
        calculation_order[:] = [
            reference
            for reference in calculation_order
            if not _is_detached(reference.get_object(), detached)
        ]
        if not calculation_order:
            del acroform[CO]

    with BytesIO() as f:
        writer.write(f)
        f.seek(0)
        return f.read()


def get_field_keys(pdf: bytes, use_full_widget_name: bool) -> set:
    """
    Gets the keys that `remove_widgets_by_keys` can match in a PDF.

    These are the keys of the terminal fields in the AcroForm field tree and of
    the widget annotations on pages, using the same key rules as
    `build_widgets`. Unlike `build_widgets`, fields without a widget on any
    page and widgets of types PyPDFForm does not support are included.

    Args:
        pdf (bytes): The PDF stream to read.
        use_full_widget_name (bool): Whether to use full names, including
            parent names, as keys.

    Returns:
        set: The keys of the terminal fields and page widgets.
    """
    reader = PdfReader(BytesIO(pdf))
    acroform = get_dictionary(reader.root_object, AcroForm) or DictionaryObject()
    page_widgets = [
        annot
        for page in reader.pages
        for annot in (each.get_object() for each in get_array(page, Annots))
        if _is_widget_annotation(annot)
    ]

    return {
        get_widget_key(each, use_full_widget_name)
        for each in _get_terminal_fields(acroform) + page_widgets
    }


def _is_widget_annotation(obj: object) -> bool:
    """
    Checks whether an object is a widget annotation dictionary.

    Args:
        obj (object): A resolved object, such as a page annotation.

    Returns:
        bool: True if `obj` is a dictionary whose `/Subtype` is `/Widget`.
    """
    return isinstance(obj, DictionaryObject) and obj.get(Subtype) == Widget


def _get_terminal_fields(acroform: DictionaryObject) -> List[DictionaryObject]:
    """
    Collects the terminal fields of an AcroForm field tree.

    A terminal field has no `/Kids`, or only kids without a `/T`, which are its
    widget annotations. Other fields are walked into, and each object is
    visited once.

    Args:
        acroform (DictionaryObject): The AcroForm dictionary.

    Returns:
        List[DictionaryObject]: The terminal fields, in tree order.
    """
    result = []
    stack = list(reversed(get_array(acroform, Fields)))
    seen = set()
    while stack:
        field = stack.pop().get_object()
        if isinstance(field, DictionaryObject) and id(field) not in seen:
            seen.add(id(field))
            kids = get_array(field, Kids)
            if any(
                isinstance(kid.get_object(), DictionaryObject) and T in kid.get_object()
                for kid in kids
            ):
                stack.extend(reversed(kids))
            else:
                result.append(field)

    return result


def _has_ancestor_in(
    obj: DictionaryObject, objects: Dict[int, DictionaryObject]
) -> bool:
    """
    Checks whether any object along the `/Parent` chain of an object is listed.

    Args:
        obj (DictionaryObject): A field or widget annotation.
        objects (Dict[int, DictionaryObject]): Objects keyed by their `id`.

    Returns:
        bool: True if an ancestor of `obj` is in `objects`.
    """
    seen = {id(obj)}
    node = get_dictionary(obj, Parent)
    while node is not None and id(node) not in seen:
        if id(node) in objects:
            return True
        seen.add(id(node))
        node = get_dictionary(node, Parent)

    return False


def _is_detached(obj: object, detached: Dict[int, DictionaryObject]) -> bool:
    """
    Checks whether an object or one of its ancestors was detached.

    Args:
        obj (object): A resolved object, such as a `/CO` entry.
        detached (Dict[int, DictionaryObject]): Detached objects keyed by `id`.

    Returns:
        bool: True if `obj` is a detached field or widget, or a descendant of one.
    """
    return id(obj) in detached or (
        isinstance(obj, DictionaryObject) and _has_ancestor_in(obj, detached)
    )


def detach_field(writer: PdfWriter, field: DictionaryObject) -> List[DictionaryObject]:
    """
    Detaches a field or widget and its emptied ancestors from the AcroForm tree.

    The object is removed from its parent's `/Kids`, or from the AcroForm's
    root `/Fields` array when it has no parent. A parent left without kids is
    detached the same way, stopping at the first parent with remaining kids.
    Resolved objects are compared by identity so unrelated fields with the
    same name keep their references. Page annotations are not changed.

    Args:
        writer (PdfWriter): The PDF writer that owns the field tree.
        field (DictionaryObject): The field or widget annotation to detach.

    Returns:
        List[DictionaryObject]: The detached objects: `field` followed by each
            emptied ancestor.
    """
    result = [field]
    parent = get_dictionary(field, Parent)
    while parent is not None:
        kids = get_array(parent, Kids)
        kids[:] = [kid for kid in kids if kid.get_object() is not field]
        if kids or any(parent is each for each in result):
            return result
        field = parent
        result.append(field)
        parent = get_dictionary(field, Parent)

    acroform = get_dictionary(writer.root_object, AcroForm) or DictionaryObject()
    fields = get_array(acroform, Fields)
    fields[:] = [
        reference for reference in fields if reference.get_object() is not field
    ]

    return result


@lru_cache(maxsize=8)
def share_inline_fields(pdf: bytes) -> bytes:
    """
    Shares inline widget annotations and parent fields with the field tree.

    Widget annotations and fields should be indirect objects, so that a page
    and the field tree share one object. PDFs saved by earlier versions of
    PyPDFForm can list a widget inline in a page's `/Annots`, or a field inline
    in its child's `/Parent`, with a separate copy in the field tree. Such PDFs
    are rewritten with `share_inline_objects`, keeping their header version.
    Other PDFs, including empty streams, are returned unchanged. The result is
    cached using lru_cache for performance.

    Args:
        pdf (bytes): The PDF stream to read.

    Returns:
        bytes: The PDF stream whose page widgets and their parents are indirect
            objects shared with the field tree.
    """
    if not pdf or not _has_inline_fields(PdfReader(BytesIO(pdf))):
        return pdf

    writer = PdfWriter(BytesIO(pdf))
    share_inline_objects(writer)
    with BytesIO() as f:
        writer.write(f)
        result = f.getvalue()

    return set_version(result, get_version(result), get_version(pdf))


def _has_inline_fields(reader: PdfReader) -> bool:
    """
    Checks whether a page lists an inline widget or one with an inline parent.

    Args:
        reader (PdfReader): The PDF reader.

    Returns:
        bool: True if a widget annotation in a page's `/Annots`, or a field on
            its `/Parent` chain, is stored inline.
    """
    for page in reader.pages:
        for annot in get_array(page, Annots):
            widget = annot.get_object()
            if _is_widget_annotation(widget) and (
                not isinstance(annot, IndirectObject) or _has_inline_parent(widget)
            ):
                return True

    return False


def _has_inline_parent(obj: DictionaryObject) -> bool:
    """
    Checks whether a field on the `/Parent` chain of an object is stored inline.

    Args:
        obj (DictionaryObject): A widget annotation or field.

    Returns:
        bool: True if a `/Parent` along the chain is not an indirect reference.
    """
    seen = set()
    while get_dictionary(obj, Parent) is not None and id(obj) not in seen:
        seen.add(id(obj))
        if not isinstance(obj.raw_get(Parent), IndirectObject):
            return True
        obj = cast(DictionaryObject, get_dictionary(obj, Parent))

    return False


def share_inline_objects(writer: PdfWriter) -> None:
    """
    Makes inline page widgets and their inline parents shared indirect objects.

    Each widget stored inline in a page's `/Annots` is replaced with a
    reference. Its copy in the field tree is reused when the widget's parent
    `/Kids`, or the AcroForm `/Fields` array for a widget without a parent,
    has an indirect entry that is on no page and has the widget's `/T` and
    `/Rect`. An entry whose `/P` is the page listing the widget is preferred,
    even when the widget's own `/P` names another page; an entry without `/P`
    is considered only when none has such a `/P`, and a reused entry keeps its
    `/P` when the widget's `/P` is not that page. Each field stored inline in
    the `/Parent` of a page widget or of such a field is replaced the same way,
    reusing an entry of its own container that has its `/T` and lists the
    child in `/Kids`.
    A reused entry is updated with `_merge_inline`, so references to it, such
    as `/CO` entries or actions, now refer to the object on the page. An
    entry is reused only when it is the one exact copy among the matching
    entries, or the only matching entry. Otherwise the inline object becomes
    a new indirect object, added to its container.

    Args:
        writer (PdfWriter): The PDF writer to update in place.
    """
    acroform = get_dictionary(writer.root_object, AcroForm)
    root_fields = get_array(acroform, Fields) if acroform is not None else ArrayObject()
    on_pages = {
        id(annot.get_object())
        for page in writer.pages
        for annot in get_array(page, Annots)
    }
    claimed = set()

    for page in writer.pages:
        annots = get_array(page, Annots)
        for index, annot in enumerate(annots):
            widget = annot.get_object()
            if not _is_widget_annotation(widget):
                continue
            if not isinstance(annot, IndirectObject):
                annot = _share_inline_widget(
                    writer,
                    widget,
                    cast(IndirectObject, page.indirect_reference),
                    root_fields,
                    (on_pages, claimed),
                )
                annots[index] = annot
            _share_inline_parents(writer, annot, root_fields)


def _share_inline_widget(
    writer: PdfWriter,
    widget: DictionaryObject,
    page: IndirectObject,
    root_fields: ArrayObject,
    excluded: tuple[set, set],
) -> IndirectObject:
    """
    Returns the reference that replaces an inline page widget.

    Args:
        writer (PdfWriter): The PDF writer that owns the page and field tree.
        widget (DictionaryObject): The inline widget annotation.
        page (IndirectObject): The page whose `/Annots` lists the widget.
        root_fields (ArrayObject): The AcroForm `/Fields` array.
        excluded (tuple[set, set]): The `id` of every annotation listed by a
            page, and the object numbers of entries already used for a page
            widget, which this function adds to.

    Returns:
        IndirectObject: The reused copy, or a new indirect object.
    """
    on_pages, claimed = excluded
    parent = get_dictionary(widget, Parent)
    container = get_array(parent, Kids) if parent is not None else root_fields

    def is_candidate(copy: object) -> bool:
        return (
            _is_widget_annotation(copy)
            and id(copy) not in on_pages
            and cast(DictionaryObject, copy).get(T) == widget.get(T)
            and _get_rect(cast(DictionaryObject, copy)) == _get_rect(widget)
        )

    reference = _find_copy(
        container,
        widget,
        [
            lambda copy: is_candidate(copy) and copy.get(P) == page,
            lambda copy: is_candidate(copy) and get_dictionary(copy, P) is None,
        ],
        claimed,
    )
    if reference is None:
        reference = writer._add_object(widget)  # type: ignore[attr-defined] # noqa: SLF001 # pylint: disable=W0212
        container.append(reference)
    else:
        _merge_inline(
            cast(DictionaryObject, reference.get_object()),
            widget,
            () if widget.get(P) == page else (P,),
        )

    claimed.add(reference.idnum)
    return reference


def _share_inline_parents(
    writer: PdfWriter, child: IndirectObject, root_fields: ArrayObject
) -> None:
    """
    Replaces inline fields along the `/Parent` chain of an indirect object.

    Args:
        writer (PdfWriter): The PDF writer that owns the field tree.
        child (IndirectObject): A page widget, referenced indirectly.
        root_fields (ArrayObject): The AcroForm `/Fields` array.
    """
    obj = cast(DictionaryObject, child.get_object())
    seen = set()
    while (parent := get_dictionary(obj, Parent)) is not None and id(obj) not in seen:
        seen.add(id(obj))
        reference = obj.raw_get(Parent)
        if not isinstance(reference, IndirectObject):
            reference = _share_inline_parent(writer, parent, child, root_fields)
            obj[NameObject(Parent)] = reference
        child = reference
        obj = cast(DictionaryObject, reference.get_object())


def _share_inline_parent(
    writer: PdfWriter,
    parent: DictionaryObject,
    child: IndirectObject,
    root_fields: ArrayObject,
) -> IndirectObject:
    """
    Returns the reference that replaces an inline parent field.

    Args:
        writer (PdfWriter): The PDF writer that owns the field tree.
        parent (DictionaryObject): The inline parent field.
        child (IndirectObject): The child whose `/Parent` it is.
        root_fields (ArrayObject): The AcroForm `/Fields` array.

    Returns:
        IndirectObject: The reused copy, or a new indirect object.
    """
    grandparent = get_dictionary(parent, Parent)
    container = get_array(grandparent, Kids) if grandparent is not None else root_fields
    reference = _find_copy(
        container,
        parent,
        [
            lambda copy: (
                isinstance(copy, DictionaryObject)
                and copy.get(T) == parent.get(T)
                and child in get_array(copy, Kids)
            )
        ],
        set(),
    )
    if reference is None:
        reference = writer._add_object(parent)  # type: ignore[attr-defined] # noqa: SLF001 # pylint: disable=W0212
        container.append(reference)
    else:
        _merge_inline(cast(DictionaryObject, reference.get_object()), parent, (Kids,))

    return reference


def _merge_inline(
    copy: DictionaryObject, obj: DictionaryObject, skip: tuple = ()
) -> None:
    """
    Updates a reused copy with the entries of the inline object it replaces.

    The inline object's values win, and the copy keeps the entries the inline
    object lacks, such as actions added to the field. When both have an
    additional-actions (`/AA`) dictionary, the copy gets a new one with the
    triggers of both, taking the inline object's action for a trigger both
    have. Null entries are treated as absent, as ISO 32000-1 specifies, so
    they don't replace the copy's entries or triggers.

    Args:
        copy (DictionaryObject): The reused entry, updated in place.
        obj (DictionaryObject): The inline object.
        skip (tuple): Keys of `obj` not copied, such as a parent's `/Kids`.
    """
    actions = get_dictionary(copy, AA)
    inline_actions = get_dictionary(obj, AA)
    copy.update(
        {key: value for key, value in _get_entries(obj).items() if key not in skip}
    )
    if actions is not None and inline_actions is not None:
        copy[NameObject(AA)] = DictionaryObject(
            _get_entries(actions) | _get_entries(inline_actions)
        )


def _get_entries(obj: DictionaryObject) -> dict:
    """
    Gets the entries of a dictionary that are not null.

    Args:
        obj (DictionaryObject): The dictionary.

    Returns:
        dict: Its keys and raw values, without entries whose value is null.
    """
    return {
        key: obj.raw_get(key)
        for key in obj
        if not isinstance(obj.raw_get(key).get_object(), NullObject)
    }


def _find_copy(
    container: ArrayObject,
    obj: DictionaryObject,
    tiers: List[Callable[[DictionaryObject], bool]],
    claimed: set,
) -> Optional[IndirectObject]:
    """
    Finds the entry of a container that is the copy of an inline object.

    Args:
        container (ArrayObject): The `/Kids` or `/Fields` array to search.
        obj (DictionaryObject): The inline object.
        tiers (List[Callable[[DictionaryObject], bool]]): Decide which
            resolved entries match the inline object, in order of
            preference. A later one is used only when no entry matches the
            ones before it.
        claimed (set): Object numbers of entries that cannot be used.

    Returns:
        Optional[IndirectObject]: Among the entries of the first tier that
            matches any, the only one equal to `obj`, or the only one when
            none is equal to it, or None when the match is not unique.
    """
    for matches in tiers:
        found = [
            entry
            for entry in container
            if isinstance(entry, IndirectObject)
            and entry.idnum not in claimed
            and matches(cast(DictionaryObject, entry.get_object()))
        ]
        if found:
            exact = [entry for entry in found if entry.get_object() == obj]
            candidates = exact or found
            return candidates[0] if len(candidates) == 1 else None

    return None


def _get_rect(annot: DictionaryObject) -> list:
    """
    Gets the `/Rect` of an annotation as numbers.

    Args:
        annot (DictionaryObject): The annotation.

    Returns:
        list: The rectangle's coordinates, or an empty list without one.
    """
    return [float(each.get_object()) for each in get_array(annot, Rect)]
