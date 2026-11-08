# -*- coding: utf-8 -*-
"""
Module for cloning page annotations without content from excluded pages.

It provides `ClonePlan`, which decides which objects reachable from the
annotations of selected source pages are cloned into a writer. References are
remapped to the destination pages, shared fields keep only their cloned
widgets, and references to excluded content are removed or rejected.
"""

from collections.abc import Callable
from typing import Any, Dict, Iterable, List, NoReturn, Optional, cast

from pypdf import PdfReader, PdfWriter
from pypdf.generic import (
    ArrayObject,
    DictionaryObject,
    IndirectObject,
    NameObject,
    StreamObject,
)

from .constants import (
    AP,
    AS,
    DV,
    FT,
    A,
    AcroForm,
    Annots,
    Btn,
    D,
    Dest,
    Fields,
    GoTo,
    Hide,
    Kids,
    Link,
    N,
    Off,
    Opt,
    P,
    Parent,
    R,
    ResetForm,
    Root,
    S,
    SubmitForm,
    Subtype,
    T,
    V,
    Widget,
)


class ClonePlan:
    """
    Keeps the objects cloned with the annotations of selected pages within those pages.

    The plan is built from one source reader and edits that reader's objects in
    memory before they are cloned, so the reader must not be used for anything
    else afterwards. Every annotation listed by a selected page is cloned unless
    `select` rejects it or it is a link whose explicit destination is not a
    selected page. Before cloning:

    * References to selected pages become their mapped references, and
      references to the document catalog become the writer's catalog. An
      annotation's own `/P` is first pointed at the page that lists it.
    * Fields get new `/Kids` arrays without annotations that are not cloned
      and fields whose widgets are all not cloned, so a field shared with other
      pages keeps only the cloned part of its hierarchy. A button field's
      `/Opt` and positional on-states are updated to match its remaining kids.
    * GoTo actions whose explicit destination is an excluded page are removed,
      together with any actions chained after them.
    * Any other reference to an excluded page, the page tree, the AcroForm
      dictionary, an annotation that is not cloned, or a field whose widgets are
      all not cloned raises `ValueError` instead of copying excluded content.
      This includes fields that ResetForm, SubmitForm, and Hide actions name by
      fully qualified name.
    """

    _REMOVE = object()
    _NAMED_TARGETS = {ResetForm: Fields, SubmitForm: Fields, Hide: T}

    def __init__(
        self,
        reader: PdfReader,
        writer: PdfWriter,
        page_references: Dict[int, IndirectObject],
        select: Optional[Callable[[DictionaryObject], bool]] = None,
    ) -> None:
        """
        Plans which annotations of a source reader are cloned into a writer.

        Args:
            reader (PdfReader): The source reader, used only for this plan.
            writer (PdfWriter): The writer the annotations are cloned into.
            page_references (Dict[int, IndirectObject]): The references that
                replace each selected page, keyed by the object numbers of the
                source pages. Other pages are excluded.
            select (Optional[Callable[[DictionaryObject], bool]]): Decides which
                annotations of selected pages are cloned. Defaults to all.
        """
        super().__init__()
        self._reader = reader
        self._writer = writer
        self._pages = set(page_references)
        self._references = dict(page_references)
        self._visited: Dict[int, Any] = {}

        forbidden = set()
        root = reader.trailer.raw_get(Root)
        self._references[root.idnum] = cast(
            IndirectObject, writer.root_object.indirect_reference
        )
        acroform = root.get_object().get(AcroForm)
        if isinstance(acroform, IndirectObject):
            forbidden.add(acroform.idnum)

        self._excluded_pages = {
            cast(IndirectObject, page.indirect_reference).idnum for page in reader.pages
        } - self._pages
        forbidden |= self._excluded_pages

        self.annotations: List[List[tuple[int, Any]]] = []
        kept = set()
        dropped = set()
        owned = set()
        self._kept_fields: set[int] = set()
        for page in reader.pages:
            reference = cast(IndirectObject, page.indirect_reference)
            forbidden |= self._get_ancestors(page)
            selected = []
            annots = page.get(Annots, ArrayObject()).get_object()
            for index, annot in enumerate(annots):
                if reference.idnum not in self._pages:
                    if isinstance(annot, IndirectObject):
                        dropped.add(annot.idnum)
                    continue
                obj = annot.get_object()
                keep = self._is_selected(obj, select)
                if isinstance(annot, IndirectObject):
                    (kept if keep else dropped).add(annot.idnum)
                if not keep:
                    continue
                selected.append((index, annot))
                if P in obj and id(obj) not in owned:
                    obj[NameObject(P)] = reference
                owned.add(id(obj))
                if obj.get(Subtype) == Widget:
                    self._kept_fields |= self._get_ancestors(obj)
            self.annotations.append(selected)

        self._dropped = dropped - kept
        self._excluded_fields: Dict[int, bool] = {}
        self._field_names: Optional[Dict[str, IndirectObject]] = None
        self._original_kids: Dict[int, ArrayObject] = {}
        self._forbidden = (forbidden | self._dropped) - set(self._references)

    @staticmethod
    def _get_destination_page(destination: Any) -> int | None:
        """
        Gets the object number of the page an explicit destination refers to.

        Args:
            destination (Any): A destination value, or a reference to one.

        Returns:
            int | None: The object number of the destination's first element when
                it is an indirect reference, or None for named destinations and
                other values.
        """
        if isinstance(destination, IndirectObject):
            destination = destination.get_object()
        if (
            isinstance(destination, ArrayObject)
            and destination
            and isinstance(destination[0], IndirectObject)
        ):
            return destination[0].idnum
        return None

    @staticmethod
    def _get_link_destination(annot: DictionaryObject) -> Any:
        """
        Gets the destination of a link annotation.

        Args:
            annot (DictionaryObject): The annotation dictionary.

        Returns:
            Any: The link's `/Dest`, or the `/D` of its GoTo action, or None for
                other annotations and actions.
        """
        if annot.get(Subtype) != Link:
            return None
        if Dest in annot:
            return annot.raw_get(Dest)

        action = annot.get(A, DictionaryObject()).get_object()
        if isinstance(action, DictionaryObject) and action.get(S) == GoTo:
            return action.get(D)
        return None

    def _is_selected(
        self,
        annot: DictionaryObject,
        select: Optional[Callable[[DictionaryObject], bool]],
    ) -> bool:
        """
        Checks whether an annotation of a selected page is cloned.

        Args:
            annot (DictionaryObject): The annotation dictionary.
            select (Optional[Callable[[DictionaryObject], bool]]): The
                annotation filter, if any.

        Returns:
            bool: False if `select` rejects the annotation or it is a link whose
                explicit destination is not a selected page, otherwise True.
        """
        target = self._get_destination_page(self._get_link_destination(annot))
        return (select is None or select(annot)) and (
            target is None or target in self._pages
        )

    @staticmethod
    def _get_ancestors(obj: DictionaryObject) -> set[int]:
        """
        Collects the object numbers along the `/Parent` chain of an object.

        Args:
            obj (DictionaryObject): A page, page tree node, or field.

        Returns:
            set[int]: The object numbers of its ancestors.
        """
        result = set()
        parent = obj.get(Parent)
        while isinstance(parent, IndirectObject) and parent.idnum not in result:
            result.add(parent.idnum)
            node = parent.get_object()
            parent = node.get(Parent) if isinstance(node, DictionaryObject) else None
        return result

    def _is_excluded_field(self, reference: IndirectObject) -> bool:
        """
        Checks whether a reference is a field whose widgets are all not cloned.

        A field is excluded when its `/Kids` subtree contains an annotation that
        is not cloned and the field is not an ancestor of a cloned widget.
        Fields without widgets on any page are not excluded. Results are cached.

        Args:
            reference (IndirectObject): A reference to a source object.

        Returns:
            bool: True if the referenced object is an excluded field.
        """
        if reference.idnum in self._kept_fields:
            return False
        if reference.idnum not in self._excluded_fields:
            result = False
            stack = [reference]
            seen = {reference.idnum}
            while stack and not result:
                node = stack.pop()
                result = node.idnum in self._dropped
                obj = node.get_object()
                if isinstance(obj, DictionaryObject) and Kids in obj:
                    kids = [
                        kid
                        for kid in obj[Kids]
                        if isinstance(kid, IndirectObject) and kid.idnum not in seen
                    ]
                    seen.update(kid.idnum for kid in kids)
                    stack.extend(kids)
            self._excluded_fields[reference.idnum] = result
        return self._excluded_fields[reference.idnum]

    def _is_excluded(self, value: Any) -> bool:
        """
        Checks whether a value refers to content that is not cloned.

        Args:
            value (Any): A raw value from a source object, or None.

        Returns:
            bool: True if the value is a source reference to an excluded page,
                the page tree, the AcroForm dictionary, an annotation that is
                not cloned, or a field whose widgets are all not cloned.
        """
        return (
            isinstance(value, IndirectObject)
            and value.pdf is self._reader
            and value.idnum not in self._references
            and (value.idnum in self._forbidden or self._is_excluded_field(value))
        )

    @staticmethod
    def _reject(path: str, page_number: int) -> NoReturn:
        """
        Raises the error for a reference to content that is not cloned.

        Args:
            path (str): The location of the reference.
            page_number (int): The 1-based source page being guarded.

        Raises:
            ValueError: Always.
        """
        msg = (
            f"Cannot copy page {page_number}: {path} refers to content that is "
            "not being copied, such as another page or a field or annotation on "
            "one."
        )
        raise ValueError(msg)

    def _find_field(self, name: str) -> IndirectObject | None:
        """
        Finds a source field by its fully qualified name.

        The field hierarchy under the AcroForm `/Fields` array is indexed on
        first use, including kids that were already pruned.

        Args:
            name (str): The fully qualified field name.

        Returns:
            IndirectObject | None: A reference to the field with that name, or
                None if there is none.
        """
        if self._field_names is None:
            self._field_names = {}
            acroform = (
                self._reader.trailer[Root]
                .get(AcroForm, DictionaryObject())
                .get_object()
            )
            stack = [
                (field, "")
                for field in acroform.get(Fields, ArrayObject()).get_object()
                if isinstance(field, IndirectObject)
            ]
            seen = {field.idnum for field, _ in stack}
            while stack:
                reference, prefix = stack.pop()
                node = cast(DictionaryObject, reference.get_object())
                if T in node:
                    prefix = f"{prefix}.{node[T]}" if prefix else str(node[T])
                    self._field_names.setdefault(prefix, reference)
                kids = [
                    kid
                    for kid in self._original_kids.get(
                        id(node),
                        cast(ArrayObject, node.get(Kids, ArrayObject()).get_object()),
                    )
                    if isinstance(kid, IndirectObject) and kid.idnum not in seen
                ]
                seen.update(kid.idnum for kid in kids)
                stack.extend((kid, prefix) for kid in kids)
        return self._field_names.get(name)

    def _check_named_targets(
        self, action: DictionaryObject, path: str, page_number: int
    ) -> None:
        """
        Rejects an action that names a field that is not cloned.

        ResetForm and SubmitForm actions can name fields in `/Fields`, and Hide
        actions in `/T`, by fully qualified name instead of by reference. Names
        are resolved against the source field hierarchy, including names
        stored as indirect strings, and follow the same rule as references.
        Names of unknown fields are kept.

        Args:
            action (DictionaryObject): A source dictionary, possibly an action.
            path (str): The dictionary's location, for error messages.
            page_number (int): The 1-based source page being guarded.

        Raises:
            ValueError: If the action names a field that is not cloned.
        """
        key = self._NAMED_TARGETS.get(action.get(S))
        if key is None or key not in action:
            return

        targets = action[key]
        entries = (
            [(f"{path}{key}[{index}]", target) for index, target in enumerate(targets)]
            if isinstance(targets, ArrayObject)
            else [(f"{path}{key}", targets)]
        )
        for entry_path, target in entries:
            name = target.get_object()
            if isinstance(name, str) and self._is_excluded(self._find_field(name)):
                self._reject(entry_path, page_number)

    def _prune_kids(self, field: DictionaryObject) -> None:
        """
        Removes kids that are not cloned from a field's `/Kids`.

        The field gets a new `/Kids` array, so the original array stays intact
        for anything else that refers to it, such as an action's `/Fields`,
        and is still checked there. For a button field whose kids are widgets and whose `/Opt`, inherited
        or not, has one entry per kid, the field gets its own `/Opt` with the
        entries of the remaining kids, and their positional states are
        renumbered with `_renumber_states`.

        Args:
            field (DictionaryObject): A source dictionary with `/Kids`.
        """
        kids = field[Kids]
        keep = [index for index, kid in enumerate(kids) if not self._is_excluded(kid)]
        if len(keep) == len(kids):
            return

        options = field.get_inherited(Opt, ArrayObject())
        if (
            field.get_inherited(FT) == Btn
            and len(options) == len(kids)
            and all(kid.get_object().get(Subtype) == Widget for kid in kids)
        ):
            self._renumber_states(
                field, [kids[index].get_object() for index in keep], keep
            )
            field[NameObject(Opt)] = ArrayObject(options[index] for index in keep)
        self._original_kids[id(field)] = kids
        field[NameObject(Kids)] = ArrayObject(kids[index] for index in keep)

    @staticmethod
    def _renumber_states(
        field: DictionaryObject, kids: List[DictionaryObject], keep: List[int]
    ) -> None:
        """
        Renumbers positional states after a button field's `/Kids` are pruned.

        With `/Opt`, a kid's on-state may be its position in `/Kids`, such as
        `/0` or `/1`. Those names are renumbered to the new positions in each
        remaining kid's `/AS` and normal, rollover, and down appearance
        dictionaries. Each remaining kid gets its own `/AP` dictionary with
        renamed copies of those state dictionaries, so dictionaries shared with
        other fields are not changed. Appearance streams stay shared, and kids
        or appearance types of this field that shared a state dictionary share
        its copy (see `_rename_appearances`). The copies hold the same values as
        the originals, which the guard walks. The field's `/V` and `/DV`, inherited or
        not, are renumbered on the field itself. One naming the position of a
        removed kid is deleted from the field, or set to `/Off` when an
        ancestor would otherwise still supply a value. Other state names are
        kept.

        Args:
            field (DictionaryObject): The button field.
            kids (List[DictionaryObject]): The remaining kids, in order.
            keep (List[int]): The original positions of the remaining kids.
        """
        states = {
            NameObject(f"/{old}"): NameObject(f"/{new}") for new, old in enumerate(keep)
        }
        for key in (V, DV):
            value = field.get_inherited(key)
            if not (isinstance(value, NameObject) and value[1:].isdigit()):
                continue
            if value in states:
                field[NameObject(key)] = states[value]
                continue
            if key in field:
                del field[key]
            if field.get_inherited(key) is not None:
                field[NameObject(key)] = NameObject(Off)

        copies: Dict[int, tuple[DictionaryObject, DictionaryObject]] = {}
        for kid in kids:
            if AS in kid and kid[AS] in states:
                kid[NameObject(AS)] = states[kid[AS]]
            if AP in kid:
                kid[NameObject(AP)] = ClonePlan._rename_appearances(
                    cast(DictionaryObject, kid[AP]), states, copies
                )

    @staticmethod
    def _rename_appearances(
        appearances: DictionaryObject,
        states: Dict[NameObject, NameObject],
        copies: Dict[int, tuple[DictionaryObject, DictionaryObject]],
    ) -> DictionaryObject:
        """
        Copies a kid's appearance dictionary with renamed state dictionaries.

        The normal, rollover, and down entries that are state dictionaries are
        replaced with copies whose keys are renamed by `states`. A state
        dictionary already copied for another kid or entry of the same field
        reuses that copy. Appearance streams, including entries that are a
        single stream, are kept as they are.

        Args:
            appearances (DictionaryObject): The kid's `/AP` dictionary.
            states (Dict[NameObject, NameObject]): The renamed states.
            copies (Dict[int, tuple[DictionaryObject, DictionaryObject]]): The
                state dictionaries copied so far for the field, with their
                originals kept alive, keyed by the originals' `id`.

        Returns:
            DictionaryObject: The new `/AP` dictionary.
        """
        result = DictionaryObject(
            {key: appearances.raw_get(key) for key in appearances}
        )
        for key in (N, R, D):
            if key not in result:
                continue
            state = result[key]
            if not isinstance(state, DictionaryObject) or isinstance(
                state, StreamObject
            ):
                continue
            if id(state) not in copies:
                entries = [(name, state.raw_get(name)) for name in state]
                copies[id(state)] = (
                    state,
                    DictionaryObject(
                        {name: value for name, value in entries if name not in states}
                        | {
                            states[name]: value
                            for name, value in entries
                            if name in states
                        }
                    ),
                )
            result[NameObject(key)] = copies[id(state)][1]
        return result

    def _check(self, value: Any, path: str, page_number: int) -> Any:
        """
        Decides what happens to one entry of an object being guarded.

        Args:
            value (Any): The raw entry value.
            path (str): The entry's location, for error messages.
            page_number (int): The 1-based source page being guarded.

        Returns:
            Any: `_REMOVE` to remove the entry, a replacement reference, or None
                to keep it.

        Raises:
            ValueError: If the entry refers to excluded content.
        """
        if (
            isinstance(value, IndirectObject)
            and value.pdf is self._reader
            and value.idnum in self._references
        ):
            return self._references[value.idnum]
        if self._is_excluded(value):
            self._reject(path, page_number)

        action = value.get_object()
        if (
            isinstance(action, DictionaryObject)
            and action.get(S) == GoTo
            and self._get_destination_page(action.get(D)) in self._excluded_pages
        ):
            return self._REMOVE
        return None

    def guard(
        self,
        root: DictionaryObject,
        path: str,
        page_number: int,
        skip: Iterable[str] = (),
    ) -> None:
        """
        Applies the plan to every source object reachable from a root object.

        Args:
            root (DictionaryObject): The page or annotation to start from.
            path (str): The root's location, for error messages.
            page_number (int): The 1-based source page of the root.
            skip (Iterable[str]): Keys of the root that are not followed.

        Raises:
            ValueError: If a reachable object refers to excluded content.
        """
        stack: List[tuple[Any, str]] = [(root, path)]
        while stack:
            obj, path = stack.pop()
            if id(obj) in self._visited:
                continue
            self._visited[id(obj)] = obj

            is_dict = isinstance(obj, DictionaryObject)
            if is_dict:
                if Kids in obj:
                    self._prune_kids(obj)
                self._check_named_targets(obj, path, page_number)
            entries = (
                [(key, obj.raw_get(key)) for key in list(obj)]
                if is_dict
                else list(enumerate(obj))
            )
            kept = []
            for key, value in entries:
                if is_dict and obj is root and key in skip:
                    continue
                entry_path = f"{path}{key}" if is_dict else f"{path}[{key}]"
                result = self._check(value, entry_path, page_number)
                if result is self._REMOVE:
                    if is_dict:
                        del obj[key]
                    continue
                if result is not None:
                    value = result
                    if is_dict:
                        obj[key] = value
                elif isinstance(
                    target := value.get_object(), (DictionaryObject, ArrayObject)
                ):
                    stack.append((target, entry_path))
                kept.append(value)

            if not is_dict:
                obj[:] = kept

    def clone_annotations(self) -> List[List[Any]]:
        """
        Guards and clones the selected annotations of each source page.

        Returns:
            List[List[Any]]: The cloned annotations, one list per source page.

        Raises:
            ValueError: If a selected annotation refers to excluded content.
        """
        for page_number, selected in enumerate(self.annotations, 1):
            for index, annot in selected:
                self.guard(annot.get_object(), f"{Annots}[{index}]", page_number)

        return [
            [annot.clone(self._writer) for _, annot in selected]
            for selected in self.annotations
        ]
