# -*- coding: utf-8 -*-
"""
This module provides a collection of utility functions used throughout the PyPDFForm library.

It includes functions for:
- Reading array and dictionary entries, treating null entries as absent.
- Removing all widgets (form fields) from a PDF.
- Splitting PDFs into single-page streams without content from other pages.
- Merging PDF byte streams while preserving page annotations.
- Cloning page annotations with `ClonePlan`, so page references point at the destination pages.
- Finding and traversing patterns within PDF widgets.
- Extracting widget properties based on defined patterns.
- Generating unique suffixes for internal use.
- Reading and choosing PDF header versions.
"""

from collections.abc import Callable, Sequence
from functools import lru_cache
from io import BytesIO
from secrets import choice
from string import ascii_letters, digits, punctuation
from typing import Any, Dict, List, Optional, cast

from pypdf import PageObject, PdfReader, PdfWriter
from pypdf.errors import PyPdfError
from pypdf.generic import (
    ArrayObject,
    DictionaryObject,
    FloatObject,
    IndirectObject,
    NameObject,
    NullObject,
    NumberObject,
)

from .clone import ClonePlan
from .constants import (
    ALPHA_VERSION,
    CA,
    COMB,
    COMB_VERSION,
    FEATURE_VERSIONS_BY_ACTION,
    FEATURE_VERSIONS_BY_FIELD_TYPE,
    FEATURE_VERSIONS_BY_FILTER,
    FEATURE_VERSIONS_BY_KEY,
    FEATURE_VERSIONS_BY_SUBTYPE,
    FT,
    NEWEST_FEATURE_VERSION,
    PDF_VERSIONS,
    TITLE_VERSION,
    UNIQUE_SUFFIX_LENGTH,
    VERSION_IDENTIFIER_PREFIX,
    VERSION_IDENTIFIERS,
    Annots,
    B,
    Ff,
    Filter,
    Info,
    Parent,
    S,
    Subtype,
    T,
    Title,
    Version,
    ca,
)


def get_array(obj: DictionaryObject, key: str) -> ArrayObject:
    """
    Gets an array entry of a dictionary, resolving indirect references.

    A missing entry reads as an empty array, and so does a null, which ISO
    32000-1 treats as an absent entry, or any other value that is not an array.
    Such an empty array is not stored in `obj`, so changing it has no effect.

    Args:
        obj (DictionaryObject): The dictionary to read.
        key (str): The entry's key.

    Returns:
        ArrayObject: The resolved array, or a new empty array.
    """
    value = obj.get(key)
    value = value.get_object() if value is not None else None
    return value if isinstance(value, ArrayObject) else ArrayObject()


def get_dictionary(obj: DictionaryObject, key: str) -> Optional[DictionaryObject]:
    """
    Gets a dictionary entry of a dictionary, resolving indirect references.

    Args:
        obj (DictionaryObject): The dictionary to read.
        key (str): The entry's key.

    Returns:
        Optional[DictionaryObject]: The resolved dictionary, or None when the
            entry is missing, null, or not a dictionary.
    """
    value = obj.get(key)
    value = value.get_object() if value is not None else None
    return value if isinstance(value, DictionaryObject) else None


def get_entry(obj: DictionaryObject, key: str) -> object:
    """
    Gets an entry of a dictionary, resolving an indirect reference.

    Args:
        obj (DictionaryObject): The dictionary to read.
        key (str): The entry's key.

    Returns:
        object: The resolved value, or None when the entry is missing or null,
            which ISO 32000-1 treats as absent.
    """
    value = obj.get(key)
    value = value.get_object() if value is not None else None
    return None if isinstance(value, NullObject) else value


def has_name(obj: DictionaryObject) -> bool:
    """
    Checks whether a field or widget dictionary has a name (`/T`).

    A null name is absent, as ISO 32000-1 specifies for null entries, so a
    widget whose `/T` is null belongs to its parent field like a widget
    without one.

    Args:
        obj (DictionaryObject): The field or widget dictionary.

    Returns:
        bool: True if the dictionary has a `/T` that isn't null.
    """
    return get_entry(obj, T) is not None


def remove_all_widgets(pdf: bytes) -> bytes:
    """
    Removes all widgets (form fields) from a PDF.

    This function takes a PDF as a bytes stream, removes all of its interactive
    form field annotations from each page, and returns the modified PDF as a
    bytes stream. This is useful for creating a non-interactive version of a PDF
    form or for temporarily stripping widgets before copying them back.

    Args:
        pdf (bytes): The PDF as a bytes stream.

    Returns:
        bytes: The PDF with all widgets removed, as a bytes stream.
    """
    result_stream = BytesIO()
    writer = PdfWriter(BytesIO(pdf))
    for page in writer.pages:
        if page.annotations:
            page.annotations.clear()

    writer.write(result_stream)
    result_stream.seek(0)
    return result_stream.read()


def map_page_references(
    source_pages: Sequence[PageObject],
    writer_pages: Sequence[PageObject],
) -> Dict[int, IndirectObject]:
    """
    Maps source pages to the writer pages that take their place.

    Pages are paired in order. Source pages without a matching writer page are
    left unmapped.

    Args:
        source_pages (Sequence[PageObject]): The pages of a source PDF.
        writer_pages (Sequence[PageObject]): The writer pages, in the same order
            as their source pages.

    Returns:
        Dict[int, IndirectObject]: Writer page references keyed by the object
            numbers of their source pages.
    """
    return {
        cast(IndirectObject, source.indirect_reference).idnum: cast(
            IndirectObject, target.indirect_reference
        )
        for source, target in zip(source_pages, writer_pages, strict=False)
    }


def clone_page_annotations(
    reader: PdfReader,
    writer: PdfWriter,
    page_references: Dict[int, IndirectObject],
    select: Optional[Callable[[DictionaryObject], bool]] = None,
) -> List[List[Any]]:
    """
    Clones the annotations of selected source pages into a writer.

    Only content of the selected pages is cloned. References to a selected page,
    including each annotation's `/P`, are pointed at its writer page. Fields
    shared with excluded pages keep only their cloned widgets. Links whose
    explicit destination is an excluded page are not cloned, and GoTo actions
    with such a destination are removed. Other references to excluded content
    raise `ValueError`. The reader's objects are edited in memory, so the reader
    must not be used for anything else afterwards.

    Args:
        reader (PdfReader): The source reader, used only for this call.
        writer (PdfWriter): The writer to clone the annotations into.
        page_references (Dict[int, IndirectObject]): Writer page references
            keyed by the object numbers of their source pages. Annotations of
            other pages are not cloned.
        select (Optional[Callable[[DictionaryObject], bool]]): Decides which
            annotations of selected pages are cloned. Defaults to all.

    Returns:
        List[List[Any]]: The cloned annotations, one list per source page.

    Raises:
        ValueError: If a cloned annotation refers to excluded content, or a
            field to prune has a `/Parent` cycle before an entry it inherits.
    """
    return ClonePlan(reader, writer, page_references, select).clone_annotations()


def get_page_streams(pdf: bytes) -> List[bytes]:
    """
    Splits a PDF into single-page PDF streams that keep their annotations.

    Each page is copied from its own reader without its `/Parent` or article
    beads (`/B`), and its annotations are cloned by a `ClonePlan` for that
    page. The page itself is checked by the same rules, so an excluded page reached
    from it, for example through a page action, is not copied either. The
    stream does not contain the source catalog, so document-level structures
    such as the AcroForm dictionary are not copied.

    Args:
        pdf (bytes): The PDF as a bytes stream.

    Returns:
        List[bytes]: A list of single-page PDF byte streams, one for each page.

    Raises:
        ValueError: If a page or one of its annotations refers to content of
            another page in a way that cannot be removed, or a field shared
            with another page has a `/Parent` cycle before an entry it
            inherits.
    """
    result = []
    page_count = len(PdfReader(BytesIO(pdf)).pages)
    for index in range(page_count):
        reader = PdfReader(BytesIO(pdf))
        writer = PdfWriter()
        page = reader.pages[index]
        reference = cast(IndirectObject, page.indirect_reference)
        plan = ClonePlan(reader, writer, {reference.idnum: reference})
        plan.guard(page, "", index + 1, (Parent, Annots, B))
        for key in (Annots, B):
            if key in page:
                del page[key]

        output_page = writer.add_page(page)
        annotations = plan.clone_annotations()[index]
        if annotations:
            output_page[NameObject(Annots)] = ArrayObject(annotations)

        with BytesIO() as f:
            writer.write(f)
            result.append(f.getvalue())

    return result


def generic_merge(items: list, merger: Callable[[Any, Any], Any]) -> Any:
    """
    Merges a list of items using a pairwise merging strategy.

    This function takes a list of items and a merger function. It merges the items
    in pairs until only a single merged item remains. This is efficient for
    combining multiple items. Callers must provide at least two items because the
    final step always merges the remaining two entries.

    Args:
        items (list): The list of items to merge.
        merger (Callable[[Any, Any], Any]): A function that takes two items and returns their merged result.

    Returns:
        Any: The final merged item.
    """
    curr_list = items[:]
    while len(curr_list) > 2:
        groups = [curr_list[i : i + 2] for i in range(0, len(curr_list), 2)]
        curr_list = []
        for each in groups:
            if len(each) == 2:
                curr_list.append(merger(each[0], each[1]))
            else:
                curr_list += each

    return merger(curr_list[0], curr_list[1])


def merge_pdfs(pdf_list: list[bytes]) -> bytes:
    """
    Merges a list of PDF byte streams into a single PDF byte stream.

    This function uses a pairwise merging strategy (similar to a merge sort's merge phase)
    to combine multiple PDF files efficiently. Instead of iteratively merging the result
    with the next PDF (O(n^2) complexity where n is the number of pages), this approach
    merges all available PDFs in pairs in a single pass. This process repeats until
    only a single merged PDF remains, offering better performance for large lists of
    PDFs.

    The list must contain at least two PDF byte streams.

    Args:
        pdf_list (list[bytes]): A list of PDF files as byte streams to be merged.

    Returns:
        bytes: The merged PDF file as a single byte stream.
    """
    return generic_merge(pdf_list, merge_two_pdfs)


def merge_two_pdfs(pdf: bytes, other: bytes) -> bytes:
    """
    Merges two PDF files into a single PDF file.

    This function takes two PDF files as byte streams, merges them, and returns the result as a single PDF byte stream.
    It handles the merging of pages from both PDFs and also attempts to preserve form field widgets from both input PDFs
    in the final merged PDF. The annotations are cloned with `clone_page_annotations`, so their page
    references point at the merged pages, and added to the output pages.

    Args:
        pdf (bytes): The first PDF file as a byte stream.
        other (bytes): The second PDF file as a byte stream.

    Returns:
        bytes: The merged PDF file as a byte stream.
    """
    output = PdfWriter()
    pdf_file = PdfReader(BytesIO(pdf))
    other_file = PdfReader(BytesIO(other))
    result = BytesIO()

    for page in pdf_file.pages:
        output.add_page(page)
    for page in other_file.pages:
        output.add_page(page)

    output.write(result)
    result.seek(0)

    merged_no_widgets = PdfReader(BytesIO(remove_all_widgets(result.read())))
    output = PdfWriter()
    output.append(merged_no_widgets)

    widgets_to_copy = {}
    for offset, source in ((0, pdf_file), (len(pdf_file.pages), other_file)):
        page_references = map_page_references(source.pages, output.pages[offset:])
        for i, annotations in enumerate(
            clone_page_annotations(source, output, page_references)
        ):
            widgets_to_copy[i + offset] = annotations

    for i, page in enumerate(output.pages):
        page[NameObject(Annots)] = (
            (page[NameObject(Annots)] + ArrayObject(widgets_to_copy[i]))
            if Annots in page
            else ArrayObject(widgets_to_copy[i])
        )

    result = BytesIO()
    output.write(result)
    result.seek(0)
    return result.read()


def _is_value_match(pattern_value: Any, widget_value: Any) -> bool:
    """
    Checks if a widget value matches a pattern value.

    Nested dictionaries delegate to `find_pattern_match`. Other values match
    when they are equal.

    Args:
        pattern_value (Any): The value from the pattern.
        widget_value (Any): The value from the widget.

    Returns:
        bool: True if it matches, False otherwise.
    """
    if isinstance(pattern_value, dict) and isinstance(
        widget_value, (dict, DictionaryObject)
    ):
        return find_pattern_match(pattern_value, widget_value)

    return pattern_value == widget_value


def find_pattern_match(pattern: dict, widget: dict | DictionaryObject) -> bool:
    """
    Recursively finds a pattern match within a PDF widget (annotation dictionary).

    This function searches for a specific pattern within a PDF widget's
    properties. It checks the widget's immediate keys and recursively descends
    only when the pattern value and widget value are both dictionary-like.
    A match is found as soon as any requested key/value pair matches.

    Args:
        pattern (dict): The pattern to search for, represented as a dictionary.
        widget (dict | DictionaryObject): The widget to search within, which
            can be a dictionary or a DictionaryObject.

    Returns:
        bool: True if a match is found, False otherwise.
    """
    for key, value in widget.items():
        if key in pattern and _is_value_match(pattern[key], value.get_object()):
            return True

    return False


def generate_unique_suffix() -> str:
    """
    Generates a unique suffix string for internal use, such as to avoid naming conflicts.

    This function creates a random string of characters with a predefined length
    (UNIQUE_SUFFIX_LENGTH) using a combination of ASCII letters, digits, and
    punctuation characters (excluding hyphens).

    Returns:
        str: A unique suffix string.
    """
    return "".join(
        [
            choice(ascii_letters + digits + punctuation.replace("-", ""))
            for _ in range(UNIQUE_SUFFIX_LENGTH)
        ]
    )


def get_version(pdf: bytes) -> str | None:
    """
    Extracts the PDF header version from a byte stream.

    The stream is checked against the supported PDF header identifiers defined
    in constants. The function inspects the original bytes directly so callers
    can capture a document's version before handing it to tools that may rewrite
    the header during output processing.

    Args:
        pdf (bytes): The PDF stream to inspect.

    Returns:
        str | None: The PDF version string, or None when the stream does not
            start with a known PDF version identifier.
    """

    version_identifier_length = len(VERSION_IDENTIFIERS[0])
    version_identifier = pdf[:version_identifier_length]
    if version_identifier not in VERSION_IDENTIFIERS:
        return None

    return version_identifier[len(VERSION_IDENTIFIER_PREFIX) :].decode()


def set_version(pdf: bytes, old: str | None, new: str | None) -> bytes:
    """
    Replaces the first PDF header version marker in a byte stream.

    This helper only changes the literal header marker, such as `%PDF-1.7`; it
    does not validate or rewrite the document for version-specific feature
    compatibility. It is used after egress rewrites so output keeps the wrapper's
    cached version instead of inheriting a writer-selected version.

    Args:
        pdf (bytes): The PDF stream to update.
        old (str | None): The currently present PDF version string. When
            None, the header token after `%PDF-` is replaced if one exists.
        new (str | None): The PDF version string to write into the header. When
            None, the PDF stream is returned unchanged.

    Returns:
        bytes: The PDF stream with the first matching version marker replaced.
    """

    if new is None or old == new:
        return pdf

    new_header = VERSION_IDENTIFIER_PREFIX + new.encode()

    if old is None:
        if not pdf.startswith(VERSION_IDENTIFIER_PREFIX):
            return pdf

        header_end = len(pdf)
        for separator in (b"\r", b"\n"):
            separator_index = pdf.find(separator, len(VERSION_IDENTIFIER_PREFIX))
            if separator_index != -1:
                header_end = min(header_end, separator_index)

        return new_header + pdf[header_end:]

    old_header = VERSION_IDENTIFIER_PREFIX + old.encode()
    if pdf.startswith(old_header):
        return new_header + pdf[len(old_header) :]

    return pdf.replace(old_header, new_header, 1)


def _version_number(version: str | None) -> tuple[int, ...] | None:
    """
    Converts a PDF version string to numbers that compare in version order.

    Args:
        version (str | None): The PDF version string, such as "1.7".

    Returns:
        tuple[int, ...] | None: The version's numbers, such as (1, 7), or None
            when the version is None or not made of numbers.
    """

    if version is None:
        return None

    try:
        return tuple(int(part) for part in version.split("."))
    except ValueError:
        return None


def get_newest_version(versions: Sequence[str | None]) -> str | None:
    """
    Gets the newest of several PDF versions.

    Args:
        versions (Sequence[str | None]): The PDF version strings. None and
            versions that are not made of numbers are ignored.

    Returns:
        str | None: The newest version, or None when none can be compared.
    """

    return max(
        (version for version in versions if _version_number(version) is not None),
        key=lambda version: _version_number(version) or (),
        default=None,
    )


# entries whose name value is looked up in a feature table
_FEATURE_VERSIONS_BY_NAME = {
    Subtype: FEATURE_VERSIONS_BY_SUBTYPE,
    S: FEATURE_VERSIONS_BY_ACTION,
    FT: FEATURE_VERSIONS_BY_FIELD_TYPE,
    Filter: FEATURE_VERSIONS_BY_FILTER,
}
# every key that `_get_feature_version` can find a feature in
_FEATURE_KEYS = frozenset(
    [*FEATURE_VERSIONS_BY_KEY, *_FEATURE_VERSIONS_BY_NAME, Ff, CA, ca]
)


def _get_feature_version(key: str, value: Any) -> str | None:
    """
    Gets the minimum PDF version of a dictionary entry that PyPDFForm can add.

    The entry is checked against the feature tables in constants: entries
    such as `/AcroForm` by key, annotations by `/Subtype`, actions by `/S`,
    signature fields by `/FT`, compressed streams by `/Filter`, comb text
    fields and radio buttons in unison by their `/Ff` bit, and constant
    opacity by a numeric `/CA` or `/ca`, which tells it from the caption of a
    widget's `/MK`.

    Args:
        key (str): The entry's key.
        value (Any): The entry's value, with indirect references resolved.

    Returns:
        str | None: The minimum PDF version of the feature, or None when the
            entry is not in the feature tables.
    """

    if key in FEATURE_VERSIONS_BY_KEY:
        return FEATURE_VERSIONS_BY_KEY[key]

    if key == Ff and isinstance(value, NumberObject) and value & COMB:
        return COMB_VERSION

    if key in (CA, ca) and isinstance(value, (NumberObject, FloatObject)):
        return ALPHA_VERSION

    table = _FEATURE_VERSIONS_BY_NAME.get(key, {})
    names = [
        each.get_object()
        for each in (value if isinstance(value, ArrayObject) else [value])
    ]  # a /Filter can be an array of filters
    return get_newest_version(
        [
            table[name]
            for name in names
            if isinstance(name, NameObject) and name in table
        ]
    )


@lru_cache(maxsize=8)
def get_required_version(pdf: bytes) -> str | None:
    """
    Gets the lowest PDF version that supports the features PyPDFForm can add.

    Every object reachable from the trailer is checked against the feature
    tables in constants, such as interactive forms (1.2), JavaScript actions
    (1.3), and comb text fields (1.5), and so is the title in the document
    information dictionary (1.1). Features that PyPDFForm doesn't add are not
    checked. The result is cached using lru_cache for performance.

    Args:
        pdf (bytes): The PDF stream to inspect.

    Returns:
        str | None: The highest minimum version among the features found, or
            None when the stream has none of them or cannot be read.
    """

    if not pdf:
        return None

    result = None
    try:
        reader = PdfReader(BytesIO(pdf))
        info = get_dictionary(reader.trailer, Info)
        if info is not None and Title in info:
            result = TITLE_VERSION

        seen = set()
        stack: list = [reader.trailer]
        while stack:
            obj = stack.pop()
            if isinstance(obj, IndirectObject):
                if (obj.idnum, obj.generation) in seen:
                    continue
                seen.add((obj.idnum, obj.generation))
                obj = obj.get_object()

            if isinstance(obj, ArrayObject):
                stack.extend(obj)
            elif isinstance(obj, DictionaryObject):
                for key, value in obj.items():
                    stack.append(value)
                    if key not in _FEATURE_KEYS:
                        continue
                    result = get_newest_version(
                        [result, _get_feature_version(key, value.get_object())]
                    )
    except PyPdfError:
        return None

    return result


def get_output_version(
    version: str | None, baseline: str | None, required: str | None
) -> str | None:
    """
    Chooses the PDF header version to write for a document.

    The document's version, read from its template or set by
    `PdfWrapper.change_version`, is kept unless the document needs a newer
    one for a feature that was added since: that is, unless the version it
    requires is newer than both its version and the baseline, the version its
    own content required then. A document whose header already understates
    its own content keeps that header.

    Args:
        version (str | None): The document's version.
        baseline (str | None): The version that the document's content
            required when its version was read or set.
        required (str | None): The version that the document's current
            content requires, from `get_required_version`.

    Returns:
        str | None: `required` when it is newer than both `version` and
            `baseline`, otherwise `version`.
    """

    covered = get_newest_version([version, baseline])
    if get_newest_version([covered, required]) == covered:
        return version

    return required


@lru_cache(maxsize=8)
def get_catalog_version(pdf: bytes) -> str | None:
    """
    Gets the PDF version that the document catalog's `/Version` entry declares.

    A catalog `/Version` overrides the header's version when it is newer. It
    is lost when only some pages are copied into a new document, so their
    version has to come from the header and this entry together. The result
    is cached using lru_cache for performance.

    Args:
        pdf (bytes): The PDF stream to inspect.

    Returns:
        str | None: The declared version, or None when the catalog has no
            `/Version` with a supported version, or the stream cannot be read.
    """

    if not pdf:
        return None

    try:
        value = PdfReader(BytesIO(pdf)).root_object.get(Version)
        value = value.get_object() if value is not None else None
    except PyPdfError:
        return None

    if isinstance(value, NameObject) and value[1:] in PDF_VERSIONS:
        return value[1:]

    return None


def can_need_newer_version(version: str | None) -> bool:
    """
    Checks whether a feature that PyPDFForm can add may need a newer version.

    No feature in the feature tables needs a version newer than
    `NEWEST_FEATURE_VERSION`, so a document at that version or newer is never
    raised, and scanning it with `get_required_version` can be skipped.

    Args:
        version (str | None): The document's version.

    Returns:
        bool: False when `version` is at least `NEWEST_FEATURE_VERSION`,
            otherwise True, including when the version is unknown.
    """

    number = _version_number(version)
    return number is None or number < (_version_number(NEWEST_FEATURE_VERSION) or ())
