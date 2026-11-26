# -*- coding: utf-8 -*-
"""
Module for maintaining the AcroForm field tree.

It removes form fields by key from page annotations, the field tree, the
calculation order, and the form actions that name them, lists the keys that
removal can match, and detaches fields and widgets from the tree. It also
shares widget annotations and parent fields stored inline, as earlier versions
of PyPDFForm could save them, with their copies in the field tree, so that a
page and the field tree refer to one object.
"""

from collections.abc import Callable
from functools import lru_cache
from io import BytesIO
from typing import Dict, List, NamedTuple, Optional, cast

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
    INCLUDE_EXCLUDE,
    NA,
    NAMED_TARGETS,
    PA,
    A,
    AcroForm,
    Annots,
    Dest,
    Fields,
    Flags,
    Hide,
    Kids,
    Next,
    OpenAction,
    P,
    Parent,
    Rect,
    S,
    Subtype,
    T,
    Type,
    U,
    Widget,
)
from .patterns import get_widget_key
from .utils import (
    get_array,
    get_dictionary,
    get_entry,
    get_version,
    has_name,
    set_version,
)


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
    when it becomes empty. Form actions that name detached fields stop naming
    them, as described in `_remove_action_targets`; JavaScript is not changed.
    A field or widget to remove whose `/Parent` chain has a cycle raises a
    `ValueError` before anything is detached, since which fields are below it,
    and would go with it, isn't defined. Other fields in a cycle don't stop
    the removal. When anything was detached, the written PDF is then cloned
    again, so it contains only objects reachable from its trailer: objects
    that only removed fields, widgets, or replaced entries used are dropped,
    while objects other content uses are kept.
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

    Raises:
        ValueError: If the `/Parent` chain of a field or widget to remove has a
            cycle.
    """
    if not keys:
        return pdf

    key_set = set(keys)
    writer = PdfWriter(BytesIO(pdf))
    acroform = get_dictionary(writer.root_object, AcroForm) or DictionaryObject()
    names = _get_field_names(writer)
    actions = _find_actions(writer.root_object)

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

    # every match first, so that a cycle raises before anything is detached
    for each in matched.values():
        _check_parent_chain(each)

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

    _remove_action_targets(actions, detached, names - _get_field_names(writer))

    if detached:
        # detached objects are still in the writer, and cloning the written
        # PDF copies only the objects reachable from its trailer
        with BytesIO() as f:
            writer.write(f)
            writer = PdfWriter(BytesIO(f.getvalue()))

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

    A terminal field has no `/Kids`, or only kids without a name, which are
    its widget annotations; a null `/T` is absent, as `has_name` describes.
    Other fields are walked into, and each object is visited once.

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
                isinstance(kid.get_object(), DictionaryObject)
                and has_name(kid.get_object())
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


def _check_parent_chain(obj: DictionaryObject) -> None:
    """
    Checks that the `/Parent` chain of a field or widget to remove has no cycle.

    Args:
        obj (DictionaryObject): A field or widget annotation.

    Raises:
        ValueError: If the chain reaches an object a second time.
    """
    seen = set()
    node: Optional[DictionaryObject] = obj
    while node is not None:
        if id(node) in seen:
            msg = "Cannot remove the field: the /Parent chain of the field has a cycle."
            raise ValueError(msg)
        seen.add(id(node))
        node = get_dictionary(node, Parent)


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


def _get_field_names(writer: PdfWriter) -> set:
    """
    Gets the fully qualified names of the fields in a PDF.

    These are the names of the fields in the AcroForm field tree, walked from
    the `/Fields` array through `/Kids`, and of the widget annotations on
    pages, including widgets whose field is missing from the tree. A name
    joins the partial names (`/T`) of a field and its ancestors with dots,
    which is how form actions name fields. A `/T` that is not a text string,
    such as a null, is treated as absent. Each object is visited once.

    Args:
        writer (PdfWriter): The PDF writer that owns the pages and field tree.

    Returns:
        set: The fully qualified names of the fields.
    """
    acroform = get_dictionary(writer.root_object, AcroForm) or DictionaryObject()
    result = set()
    stack = [(field, "") for field in get_array(acroform, Fields)]
    seen = set()
    while stack:
        reference, prefix = stack.pop()
        node = reference.get_object()
        if not isinstance(node, DictionaryObject) or id(node) in seen:
            continue
        seen.add(id(node))
        name = get_entry(node, T)
        if isinstance(name, str):
            prefix = f"{prefix}.{name}" if prefix else str(name)
            result.add(prefix)
        stack.extend((kid, prefix) for kid in get_array(node, Kids))

    for page in writer.pages:
        for annot in get_array(page, Annots):
            widget = annot.get_object()
            if _is_widget_annotation(widget) and (name := _get_full_name(widget)):
                result.add(name)

    return result


def _get_full_name(obj: DictionaryObject) -> str:
    """
    Gets the fully qualified name of a field or widget from its ancestors.

    Args:
        obj (DictionaryObject): A field or widget annotation.

    Returns:
        str: The partial names (`/T`) along its `/Parent` chain, outermost
            first, joined with dots. The chain ends at a cycle.
    """
    parts = []
    seen = set()
    node: Optional[DictionaryObject] = obj
    while node is not None and id(node) not in seen:
        seen.add(id(node))
        name = get_entry(node, T)
        if isinstance(name, str):
            parts.append(str(name))
        node = get_dictionary(node, Parent)

    return ".".join(reversed(parts))


def _get_action_type(action: DictionaryObject) -> Optional[NameObject]:
    """
    Gets the type of an action.

    Args:
        action (DictionaryObject): A dictionary in an action entry.

    Returns:
        Optional[NameObject]: Its resolved `/S` entry, or None when that is
            missing or not a name, as in some structure attributes.
    """
    kind = get_entry(action, S)
    return kind if isinstance(kind, NameObject) else None


class _FormActions(NamedTuple):
    """
    The actions reachable from a catalog, found before any field is removed.

    Attributes:
        entries (list): The `(dictionary, key)` pairs of the `/A`,
            `/OpenAction`, navigation node `/NA` and `/PA`, and `/AA` trigger
            entries whose value is a dictionary.
        following (dict): Each action with the actions in its `/Next`,
            listed before removal, keyed by its `id`.
        targets (list): An `(action, key, targets)` triple for each ResetForm,
            SubmitForm, and Hide action: the entry that names its targets and
            a list of them. The list is taken before removal, which changes
            arrays such as `/Kids` in place, so an action whose array is
            shared with them still lists every target it had.
        additional (dict): Each `/AA` dictionary with the dictionaries that
            hold it, keyed by its `id`.
    """

    entries: list
    following: dict
    targets: list
    additional: dict


def _find_actions(root: DictionaryObject) -> _FormActions:
    """
    Finds the actions in the objects reachable from a catalog.

    Every dictionary and array reachable from the catalog is visited once. The
    dictionaries in an `/A`, `/OpenAction`, `/NA`, `/PA`, or `/AA` trigger
    entry are actions; `/NA` and `/PA` are the forward and backward actions of
    a navigation node. So are the dictionaries with both an `/S` entry, which
    every action has, and a `/Next` entry, and the dictionaries in that
    `/Next`. Outline items and navigation nodes, whose `/Next` is the next
    item or node, have no `/S`.
    Stream contents are not read.

    Args:
        root (DictionaryObject): The document catalog.

    Returns:
        _FormActions: The entries that hold actions, the actions that follow
            each action, and the targets of the ResetForm, SubmitForm, and
            Hide actions among them.
    """
    entries = []
    chains = []
    additional: Dict[int, tuple[DictionaryObject, list]] = {}
    stack: list = [root]
    seen = set()
    while stack:
        obj = stack.pop().get_object()
        if not isinstance(obj, (ArrayObject, DictionaryObject)) or id(obj) in seen:
            continue
        seen.add(id(obj))
        if isinstance(obj, ArrayObject):
            stack.extend(obj)
            continue

        for key in obj:
            value = obj.raw_get(key)
            target = value.get_object()
            if key == Next and S in obj:
                chains.append(obj)
            elif key in (A, OpenAction, NA, PA) and isinstance(
                target, DictionaryObject
            ):
                entries.append((obj, key))
            elif key == AA and isinstance(target, DictionaryObject):
                if id(target) not in additional:
                    additional[id(target)] = (target, [])
                    entries.extend(
                        (target, trigger)
                        for trigger in target
                        if isinstance(target[trigger], DictionaryObject)
                    )
                additional[id(target)][1].append(obj)
            stack.append(value)

    return _FormActions(entries, *_list_actions(entries, chains), additional)


def _list_actions(entries: list, chains: list) -> tuple[dict, list]:
    """
    Lists the actions that follow each action, and the targets of form actions.

    Args:
        entries (list): The `(dictionary, key)` pairs of the entries that hold
            actions.
        chains (list): The actions with a `/Next` entry.

    Returns:
        tuple[dict, list]: The `following` and `targets` of `_FormActions`,
            for the actions in `entries`, the ones in `chains`, and the ones
            that follow them.
    """
    actions = {id(container[key]): container[key] for container, key in entries}
    for chain in chains:
        actions[id(chain)] = chain
        for each in _get_next(chain):
            action = each.get_object()
            if isinstance(action, DictionaryObject):
                actions[id(action)] = action

    following = {}
    targets = []
    for action in actions.values():
        following[id(action)] = (action, _get_next(action))
        key = NAMED_TARGETS.get(_get_action_type(action))
        if key is not None and key in action:
            value = action[key]
            targets.append(
                (
                    action,
                    key,
                    list(value)
                    if isinstance(value, ArrayObject)
                    else [action.raw_get(key)],
                )
            )

    return following, targets


def _remove_action_targets(
    actions: _FormActions, detached: Dict[int, DictionaryObject], names: set
) -> None:
    """
    Removes removed fields from the form actions that name them.

    ResetForm and SubmitForm actions name fields in `/Fields`, and Hide
    actions name fields and annotations in `/T`, by reference or by fully
    qualified name. Every action found by `_find_actions` is searched. A
    reference to a detached object, or to a descendant of one, is removed,
    and so is a name in `names`. The action gets a new array of its remaining
    targets, so an array shared with other objects, such as a field's
    `/Kids`, is not changed by it.

    An empty `/Fields` makes ResetForm and SubmitForm act on every field, and
    a Hide action without targets has nothing to act on, so an action that
    would be left without targets stops acting instead: it becomes a no-op in
    place, as described in `_make_no_op`. A ResetForm or SubmitForm action
    that acts on every field except the ones it names (`INCLUDE_EXCLUDE`) is
    kept with an empty `/Fields`, which still means every field. No action is
    taken out of a `/Next`, since some viewers, such as PDFium, stop running a
    trigger's actions when they reach one a second time, so every chain keeps
    its shape. An entry that holds actions is deleted when it reaches an
    action that stopped acting and none of the actions it reaches still act,
    counting no-ops left by earlier removals, since running it would do
    nothing, unless it is an `/A` that another entry would act in place of, as
    described in `_delete_entries`. An `/AA` dictionary left without triggers
    is deleted too.

    Args:
        actions (_FormActions): The actions, found before removal.
        detached (Dict[int, DictionaryObject]): Detached fields and widgets
            keyed by `id`.
        names (set): The fully qualified names of the removed fields that no
            remaining field has.
    """
    stopped = {
        id(action)
        for action, key, targets in actions.targets
        if _remove_targets(action, key, targets, detached, names)
    }
    if not stopped:
        return

    for key in stopped:
        _make_no_op(actions.following[key][0])

    live = _get_reaching(
        actions.following,
        {
            key
            for key, (action, _) in actions.following.items()
            if not _is_no_op(action)
        },
    )
    _delete_entries(actions, _get_reaching(actions.following, stopped) - live, live)


def _delete_entries(actions: _FormActions, inert: set, live: set) -> None:
    """
    Deletes the entries whose action is in a set.

    An `/A` entry that would let another entry act instead is kept, as
    described in `_overrides_other_entry`. When an `/AA` `/U` trigger is
    deleted, the `/A` of the same dictionary is deleted too if none of the
    actions it reaches act, so that a no-op kept for that trigger by an
    earlier removal doesn't outlive it. An `/AA` dictionary left without
    triggers is deleted too.

    Args:
        actions (_FormActions): The actions, found before removal.
        inert (set): The `id` of each action whose entries are deleted.
        live (set): The `id` of each action that acts, or from which one
            that acts can be reached through `/Next`.
    """
    deleted = set(inert)
    for triggers, owners in actions.additional.values():
        released = get_entry(triggers, U)
        if released is None or id(released) not in deleted:
            continue
        for owner in owners:
            action = get_entry(owner, A)
            if isinstance(action, DictionaryObject) and id(action) not in live:
                deleted.add(id(action))

    emptied = set()
    for container, key in actions.entries:
        if id(container[key]) in deleted and not _overrides_other_entry(
            container, key, deleted
        ):
            del container[key]
            if not container:
                emptied.add(id(container))

    for actions_dict, owners in actions.additional.values():
        if id(actions_dict) in emptied:
            for owner in owners:
                del owner[AA]


def _overrides_other_entry(container: DictionaryObject, key: str, inert: set) -> bool:
    """
    Checks whether deleting an `/A` entry would let another entry act instead.

    An annotation's `/A` takes precedence over the `/U` trigger of its `/AA`
    (ISO 32000-1, Table 194), so deleting it would let that trigger act on
    mouse release. A link annotation or outline item is not permitted to have
    both `/A` and `/Dest`, so a viewer may read either one when both are
    present.

    Args:
        container (DictionaryObject): The dictionary with the entry.
        key (str): The entry's key.
        inert (set): The `id` of each action whose entries are deleted.

    Returns:
        bool: True if `key` is `/A` and the dictionary has a `/Dest`, or an
            `/AA` whose `/U` action is not deleted too.
    """
    if key != A:
        return False

    if get_entry(container, Dest) is not None:
        return True

    triggers = get_dictionary(container, AA)
    released = get_entry(triggers, U) if triggers is not None else None
    return isinstance(released, DictionaryObject) and id(released) not in inert


def _remove_targets(
    action: DictionaryObject,
    key: str,
    targets: list,
    detached: Dict[int, DictionaryObject],
    names: set,
) -> bool:
    """
    Removes removed fields from the targets of one form action.

    Args:
        action (DictionaryObject): A ResetForm, SubmitForm, or Hide action.
        key (str): The entry that names its targets.
        targets (list): Its targets, listed before removal.
        detached (Dict[int, DictionaryObject]): Detached fields and widgets
            keyed by `id`.
        names (set): The fully qualified names of the removed fields.

    Returns:
        bool: True if the action would be left without targets and must
            stop acting instead, as described in `_remove_action_targets`.
    """
    remaining = [
        each
        for each in targets
        if not _is_removed_target(each.get_object(), detached, names)
    ]
    if len(remaining) == len(targets):
        return False

    flags = get_entry(action, Flags)
    if not remaining and (
        _get_action_type(action) == Hide
        or not (isinstance(flags, int) and flags & INCLUDE_EXCLUDE)
    ):
        return True

    action[NameObject(key)] = ArrayObject(remaining)
    return False


def _is_removed_target(
    target: object, detached: Dict[int, DictionaryObject], names: set
) -> bool:
    """
    Checks whether a form action's target is a removed field.

    Args:
        target (object): A resolved target, such as a field or a name.
        detached (Dict[int, DictionaryObject]): Detached fields and widgets
            keyed by `id`.
        names (set): The fully qualified names of the removed fields.

    Returns:
        bool: True if `target` names a removed field, or is a detached object
            or a descendant of one.
    """
    if isinstance(target, str):
        return str(target) in names

    return _is_detached(target, detached)


def _get_next(action: DictionaryObject) -> list:
    """
    Gets the actions that follow an action.

    Args:
        action (DictionaryObject): An action dictionary.

    Returns:
        list: The entries of its `/Next` array, its single `/Next` action, or
            an empty list without `/Next`.
    """
    if Next not in action:
        return []

    following = action[Next]
    return (
        list(following)
        if isinstance(following, ArrayObject)
        else [action.raw_get(Next)]
    )


def _get_reaching(following: dict, keys: set) -> set:
    """
    Finds the actions from which an action in a set can be reached.

    The `/Next` links are followed backwards from the actions in the set, so
    each action is visited once, including in shared branches and cycles.

    Args:
        following (dict): Each action with the actions in its `/Next`, keyed
            by its `id`, as `_FormActions` lists them.
        keys (set): The `id` of each action to reach.

    Returns:
        set: The `id` of each action in `keys`, and of each action from which
            one of them can be reached through `/Next`.
    """
    preceding: Dict[int, list] = {}
    for key, (_, next_actions) in following.items():
        for each in next_actions:
            preceding.setdefault(id(each.get_object()), []).append(key)

    result = set(keys)
    stack = list(keys)
    while stack:
        for key in preceding.get(stack.pop(), []):
            if key not in result:
                result.add(key)
                stack.append(key)

    return result


def _make_no_op(action: DictionaryObject) -> None:
    """
    Makes an action do nothing, keeping its `/Type` and `/Next`.

    The action becomes a Hide action with an empty `/T`, which hides no
    annotation. Hide and `/Next` are both PDF 1.2, so this suits any PDF with
    an action chain. Its other entries, which belonged to its old type, are
    removed.

    Args:
        action (DictionaryObject): The action, changed in place.
    """
    for key in list(action):
        if key not in (Type, Next):
            del action[key]
    action[NameObject(S)] = NameObject(Hide)
    action[NameObject(T)] = ArrayObject()


def _is_no_op(action: DictionaryObject) -> bool:
    """
    Checks whether an action is a no-op that `_make_no_op` could have made.

    Args:
        action (DictionaryObject): A dictionary in an action entry.

    Returns:
        bool: True if it is a Hide action whose `/T` is an empty array.
    """
    targets = get_entry(action, T)
    return (
        _get_action_type(action) == Hide
        and isinstance(targets, ArrayObject)
        and not targets
    )


def detach_field(writer: PdfWriter, field: DictionaryObject) -> List[DictionaryObject]:
    """
    Detaches a field or widget and its emptied ancestors from the AcroForm tree.

    The object is removed from its parent's `/Kids`. A parent left without
    kids is detached the same way, stopping at the first parent with remaining
    kids, at the top of the tree, or at a `/Parent` cycle. Every detached
    object is then removed from the AcroForm's root `/Fields` array, so a
    field listed there although it has a parent, or whose ancestors form a
    cycle, doesn't stay in the form. Resolved objects are compared by
    identity so unrelated fields with the same name keep their references.
    Page annotations are not changed.

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
            break
        field = parent
        result.append(field)
        parent = get_dictionary(field, Parent)

    acroform = get_dictionary(writer.root_object, AcroForm) or DictionaryObject()
    fields = get_array(acroform, Fields)
    fields[:] = [
        reference
        for reference in fields
        if not any(reference.get_object() is each for each in result)
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
