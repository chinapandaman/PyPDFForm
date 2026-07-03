# -*- coding: utf-8 -*-
"""
This module provides a collection of utility functions used throughout the PyPDFForm library.

It includes functions for:
- Removing all widgets (form fields) from a PDF.
- Splitting PDFs into single-page streams.
- Merging PDF byte streams while preserving page annotations.
- Finding and traversing patterns within PDF widgets.
- Extracting widget properties based on defined patterns.
- Generating unique suffixes for internal use.
"""

from collections.abc import Callable
from functools import lru_cache
from io import BytesIO
from secrets import choice
from string import ascii_letters, digits, punctuation
from typing import Any, List

from pypdf import PdfReader, PdfWriter
from pypdf.generic import ArrayObject, DictionaryObject, NameObject

from .constants import (
    SLASH,
    UNIQUE_SUFFIX_LENGTH,
    VERSION_IDENTIFIER_PREFIX,
    VERSION_IDENTIFIERS,
    Annots,
)


@lru_cache(maxsize=128)
def remove_all_widgets(pdf: bytes) -> bytes:
    """
    Removes all widgets (form fields) from a PDF, effectively flattening the form.

    This function takes a PDF as a bytes stream, removes all of its interactive
    form field annotations from each page, and returns the modified PDF as a
    bytes stream. This is useful for creating a non-interactive version of a PDF
    form or for temporarily stripping widgets before copying them back.

    Args:
        pdf (bytes): The PDF as a bytes stream.

    Returns:
        bytes: The PDF with all widgets removed, as a bytes stream.
    """
    pdf_file = PdfReader(BytesIO(pdf))
    result_stream = BytesIO()
    writer = PdfWriter()
    for page in pdf_file.pages:
        if page.annotations:
            page.annotations.clear()
        writer.add_page(page)

    writer.write(result_stream)
    result_stream.seek(0)
    return result_stream.read()


def get_page_streams(pdf: bytes) -> List[bytes]:
    """
    Extracts the content stream of each page in a PDF as a list of byte streams.

    This function takes a PDF as a bytes stream and returns a list of single-page
    PDF byte streams. Each element contains a complete one-page PDF produced by a
    writer, not just the page's raw `/Contents` stream.

    Args:
        pdf (bytes): The PDF as a bytes stream.

    Returns:
        List[bytes]: A list of bytes streams, one for each page.
    """
    pdf_file = PdfReader(BytesIO(pdf))
    result = []

    for page in pdf_file.pages:
        writer = PdfWriter()
        writer.add_page(page)
        with BytesIO() as f:
            writer.write(f)
            f.seek(0)
            result.append(f.read())

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
    in the final merged PDF. The form fields are cloned and added to the output pages.

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
    for i, page in enumerate(pdf_file.pages):
        widgets_to_copy[i] = []
        for annot in page.get(Annots, []):
            widgets_to_copy[i].append(annot.clone(output))

    for i, page in enumerate(other_file.pages):
        widgets_to_copy[i + len(pdf_file.pages)] = []
        for annot in page.get(Annots, []):
            widgets_to_copy[i + len(pdf_file.pages)].append(annot.clone(output))

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

    Nested dictionaries delegate to `find_pattern_match`. Tuple pattern values
    support matching any listed value, and a tuple containing ``"/"`` also
    matches PDF names with arbitrary slash-prefixed values.

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

    if isinstance(pattern_value, tuple):
        if widget_value in pattern_value:
            return True
        return SLASH in pattern_value and widget_value.startswith(SLASH)

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


def traverse_pattern(
    pattern: dict, widget: dict | DictionaryObject
) -> str | list | None:
    """
    Recursively traverses a pattern within a PDF widget (annotation dictionary) and returns the value.

    This function searches for a specific pattern within a PDF widget's
    properties. It recursively follows nested pattern dictionaries and returns
    the first truthy widget value whose pattern entry is the sentinel ``True``.
    Falsey values are ignored and treated as not found.

    Args:
        pattern (dict): The pattern to traverse, represented as a dictionary.
        widget (dict | DictionaryObject): The widget to traverse within, which
            can be a dictionary or a DictionaryObject.

    Returns:
        str | list | None: The value found, or None if not found.
    """
    for key, value in widget.items():
        result = None
        if key in pattern:
            value = value.get_object()
            if isinstance(pattern[key], dict) and isinstance(
                value, (dict, DictionaryObject)
            ):
                result = traverse_pattern(pattern[key], value)
            else:
                if pattern[key] is True and value:
                    return value
        if result:
            return result
    return None


def extract_widget_property(
    widget: dict | DictionaryObject,
    patterns: list,
    default_value: Any,
    func_before_return: Callable | None,
) -> Any:
    """
    Extracts a specific property from a PDF widget based on a list of patterns.

    This function iterates through a list of patterns, attempting to find a
    truthy value within the provided widget. If a value is found, an optional
    conversion function is applied before returning it. If every pattern
    returns ``None`` or another falsey value, the default value is returned.

    Args:
        widget (dict | DictionaryObject): The widget to extract the property from.
        patterns (list): A list of patterns to search for. Each pattern should be a
            dictionary representing the structure of the property to extract.
        default_value (Any): The default value to return if no pattern is found.
        func_before_return (Callable | None): An optional function to call before
            returning the extracted value. This can be used to perform additional
            processing or formatting on the value.

    Returns:
        Any: The extracted property value, or the default value if no pattern is found.
    """
    result = default_value

    for pattern in patterns:
        value = traverse_pattern(pattern, widget)
        if value:
            result = func_before_return(value) if func_before_return else value
            break

    return result


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
