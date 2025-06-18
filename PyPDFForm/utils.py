# -*- coding: utf-8 -*-
"""
This module provides a collection of utility functions used throughout the PyPDFForm library.

It includes functions for:
- Converting byte streams to BinaryIO objects.
- Removing all widgets (form fields) from a PDF.
- Extracting the content stream of each page in a PDF.
- Merging two PDFs into one.
- Finding and traversing patterns within PDF widgets.
- Extracting widget properties based on defined patterns.
- Generating unique suffixes for internal use.
- Enabling Adobe-specific settings in the PDF to ensure proper rendering of form fields.
"""

from collections.abc import Callable
from functools import lru_cache
from io import BytesIO
from secrets import choice
from string import ascii_letters, digits, punctuation
from typing import Any, BinaryIO, List, Union

from pypdf import PdfReader, PdfWriter
from pypdf.generic import (ArrayObject, BooleanObject, DictionaryObject,
                           NameObject)

from .constants import (UNIQUE_SUFFIX_LENGTH, AcroForm, Annots,
                        NeedAppearances, Root)


@lru_cache
def stream_to_io(stream: bytes) -> BinaryIO:
    """
    Converts a bytes stream to a BinaryIO object, which can be used by PyPDFForm.

    This function takes a bytes stream as input and returns a BinaryIO object
    that represents the same data. This is useful because PyPDFForm often
    works with BinaryIO objects, so this function allows you to easily convert
    a bytes stream to the correct format. The result is cached using lru_cache
    for performance.

    Args:
        stream (bytes): The bytes stream to convert.

    Returns:
        BinaryIO: A BinaryIO object representing the stream.
    """
    result = BytesIO()
    result.write(stream)
    result.seek(0)

    return result


@lru_cache
def enable_adobe_mode(pdf: bytes) -> bytes:
    """Enables Adobe-specific settings in the PDF to ensure proper rendering of form fields.

    This function modifies the PDF's AcroForm dictionary to include the `NeedAppearances` flag,
    which forces Adobe Reader to generate appearance streams for form fields. This ensures that
    the form fields are rendered correctly in Adobe Reader, especially when the form is filled
    programmatically.

    Args:
        pdf (bytes): The PDF content as bytes.

    Returns:
        bytes: The modified PDF content with Adobe mode enabled.
    """
    reader = PdfReader(stream_to_io(pdf))
    writer = PdfWriter()

    # https://stackoverflow.com/questions/47288578/pdf-form-filled-with-pypdf2-does-not-show-in-print
    if AcroForm in reader.trailer[Root]:
        if NeedAppearances in reader.trailer[Root][AcroForm]:
            return pdf
    else:
        reader.trailer[Root].update({NameObject(AcroForm): DictionaryObject()})
    reader.trailer[Root][AcroForm].update(
        {NameObject(NeedAppearances): BooleanObject(True)}
    )
    writer.append(reader)

    with BytesIO() as f:
        writer.write(f)
        f.seek(0)
        return f.read()


@lru_cache
def remove_all_widgets(pdf: bytes) -> bytes:
    """
    Removes all widgets (form fields) from a PDF, effectively flattening the form.

    This function takes a PDF as a bytes stream, removes all of its interactive
    form fields (widgets), and returns the modified PDF as a bytes stream. This
    is useful for creating a non-interactive version of a PDF form.

    Args:
        pdf (bytes): The PDF as a bytes stream.

    Returns:
        bytes: The PDF with all widgets removed, as a bytes stream.
    """
    pdf_file = PdfReader(stream_to_io(pdf))
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

    This function takes a PDF as a bytes stream and returns a list of bytes streams,
    where each element in the list represents the content stream of a page in the PDF.

    Args:
        pdf (bytes): The PDF as a bytes stream.

    Returns:
        List[bytes]: A list of bytes streams, one for each page.
    """
    pdf_file = PdfReader(stream_to_io(pdf))
    result = []

    for page in pdf_file.pages:
        writer = PdfWriter()
        writer.add_page(page)
        with BytesIO() as f:
            writer.write(f)
            f.seek(0)
            result.append(f.read())

    return result


def merge_two_pdfs(pdf: bytes, other: bytes) -> bytes:
    """
    Merges two PDFs into one, creating a single PDF containing all pages from both input PDFs.

    This function takes two PDFs as bytes streams and merges them into a single PDF.
    The pages from the second PDF are appended to the end of the first PDF.

    Args:
        pdf (bytes): The first PDF as a bytes stream.
        other (bytes): The second PDF as a bytes stream.

    Returns:
        bytes: The merged PDF as a bytes stream.
    """
    output = PdfWriter()
    pdf_file = PdfReader(stream_to_io(pdf))
    other_file = PdfReader(stream_to_io(other))
    result = BytesIO()

    for page in pdf_file.pages:
        output.add_page(page)
    for page in other_file.pages:
        output.add_page(page)

    output.write(result)
    result.seek(0)

    merged_no_widgets = PdfReader(stream_to_io(remove_all_widgets(result.read())))
    output = PdfWriter()
    output.append(merged_no_widgets)

    # TODO: refactor duplicate logic with copy_watermark_widgets
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


def find_pattern_match(pattern: dict, widget: Union[dict, DictionaryObject]) -> bool:
    """
    Recursively finds a pattern match within a PDF widget (annotation dictionary).

    This function searches for a specific pattern within a PDF widget's properties.
    It recursively traverses the widget's dictionary, comparing keys and values
    to the provided pattern.

    Args:
        pattern (dict): The pattern to search for, represented as a dictionary.
        widget (Union[dict, DictionaryObject]): The widget to search within, which
            can be a dictionary or a DictionaryObject.

    Returns:
        bool: True if a match is found, False otherwise.
    """
    for key, value in widget.items():
        result = False
        if key in pattern:
            value = value.get_object()
            if isinstance(pattern[key], dict) and isinstance(
                value, (dict, DictionaryObject)
            ):
                result = find_pattern_match(pattern[key], value)
            else:
                if isinstance(pattern[key], tuple):
                    result = value in pattern[key]
                else:
                    result = pattern[key] == value
        if result:
            return result
    return False


def traverse_pattern(
    pattern: dict, widget: Union[dict, DictionaryObject]
) -> Union[str, list, None]:
    """
    Recursively traverses a pattern within a PDF widget (annotation dictionary) and returns the value.

    This function searches for a specific pattern within a PDF widget's properties.
    It recursively traverses the widget's dictionary, comparing keys and values
    to the provided pattern and returns the value if the pattern is True.

    Args:
        pattern (dict): The pattern to traverse, represented as a dictionary.
        widget (Union[dict, DictionaryObject]): The widget to traverse within, which
            can be a dictionary or a DictionaryObject.

    Returns:
        Union[str, list, None]: The value found, or None if not found.
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
    widget: Union[dict, DictionaryObject],
    patterns: list,
    default_value: Any,
    func_before_return: Union[Callable, None],
) -> Any:
    """
    Extracts a specific property from a PDF widget based on a list of patterns.

    This function iterates through a list of patterns, attempting to find a match
    within the provided widget. If a match is found, the corresponding value is
    extracted and returned. If no match is found, a default value is returned.

    Args:
        widget (Union[dict, DictionaryObject]): The widget to extract the property from.
        patterns (list): A list of patterns to search for. Each pattern should be a
            dictionary representing the structure of the property to extract.
        default_value (Any): The default value to return if no pattern is found.
        func_before_return (Union[Callable, None]): An optional function to call before
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
