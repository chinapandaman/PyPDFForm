# -*- coding: utf-8 -*-
"""
Module for cloning page annotations without content from excluded pages.

It provides `ClonePlan`, which decides which objects reachable from the
annotations of selected source pages are cloned into a writer. References are
remapped to the destination pages, shared fields keep only their cloned
widgets, and references to excluded content are removed or rejected.
"""

from collections.abc import Callable
from typing import Any, Dict, Iterable, List, Optional, cast

from pypdf import PdfReader, PdfWriter
from pypdf.generic import ArrayObject, DictionaryObject, IndirectObject, NameObject

from .constants import (
    A,
    AcroForm,
    Annots,
    D,
    Dest,
    GoTo,
    Kids,
    Link,
    P,
    Parent,
    Root,
    S,
    Subtype,
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
    * `/Kids` arrays drop annotations that are not cloned and fields whose
      widgets are all not cloned, so a field shared with other pages keeps only
      the cloned part of its hierarchy.
    * GoTo actions whose explicit destination is an excluded page are removed,
      together with any actions chained after them.
    * Any other reference to an excluded page, the page tree, the AcroForm
      dictionary, an annotation that is not cloned, or a field whose widgets are
      all not cloned raises `ValueError` instead of copying excluded content.
    """

    _REMOVE = object()

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

    def _check(self, value: Any, path: str, page_number: int, prune: bool) -> Any:
        """
        Decides what happens to one entry of an object being guarded.

        Args:
            value (Any): The raw entry value.
            path (str): The entry's location, for error messages.
            page_number (int): The 1-based source page being guarded.
            prune (bool): Whether the entry is an item of a `/Kids` array.

        Returns:
            Any: `_REMOVE` to remove the entry, a replacement reference, or None
                to keep it.

        Raises:
            ValueError: If the entry refers to excluded content.
        """
        if isinstance(value, IndirectObject) and value.pdf is self._reader:
            if value.idnum in self._references:
                return self._references[value.idnum]
            if value.idnum in self._forbidden or self._is_excluded_field(value):
                if prune:
                    return self._REMOVE
                msg = (
                    f"Cannot copy page {page_number}: {path} refers to content "
                    "that is not being copied, such as another page or a field "
                    "or annotation on one."
                )
                raise ValueError(msg)

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
        stack: List[tuple[Any, str, bool]] = [(root, path, False)]
        while stack:
            obj, path, prune = stack.pop()
            if id(obj) in self._visited:
                continue
            self._visited[id(obj)] = obj

            is_dict = isinstance(obj, DictionaryObject)
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
                result = self._check(value, entry_path, page_number, prune)
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
                    stack.append((target, entry_path, is_dict and key == Kids))
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
