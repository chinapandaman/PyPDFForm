# -*- coding: utf-8 -*-
"""
Module containing utility functions for PyPDFForm.
"""

from collections.abc import Callable
from functools import lru_cache
from io import BytesIO
from secrets import choice
from string import ascii_letters, digits, punctuation
from typing import Any, BinaryIO, List, Union

from pypdf import PdfReader, PdfWriter
from pypdf.generic import DictionaryObject

from .constants import UNIQUE_SUFFIX_LENGTH


@lru_cache
def stream_to_io(stream: bytes) -> BinaryIO:
    """
    Converts a bytes stream to a BinaryIO object.

    Args:
        stream (bytes): The bytes stream to convert.

    Returns:
        BinaryIO: A BinaryIO object representing the stream.
    """
    result = BytesIO()
    result.write(stream)
    result.seek(0)

    return result


def remove_all_widgets(pdf: bytes) -> bytes:
    """
    Removes all widgets (form fields) from a PDF.

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
    Extracts the content stream of each page in a PDF.

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
    Merges two PDFs into one.

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
    return result.read()


def find_pattern_match(pattern: dict, widget: Union[dict, DictionaryObject]) -> bool:
    """
    Finds a pattern match in a widget.

    Args:
        pattern (dict): The pattern to search for.
        widget (Union[dict, DictionaryObject]): The widget to search in.

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
    Traverses a pattern in a widget.

    Args:
        pattern (dict): The pattern to traverse.
        widget (Union[dict, DictionaryObject]): The widget to traverse in.

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
    Extracts a widget property based on a list of patterns.

    Args:
        widget (Union[dict, DictionaryObject]): The widget to extract the property from.
        patterns (list): A list of patterns to search for.
        default_value (Any): The default value to return if no pattern is found.
        func_before_return (Union[Callable, None]): A function to call before returning the value.

    Returns:
        Any: The extracted property value.
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
    Generates a unique suffix.

    Returns:
        str: A unique suffix string.
    """
    return "".join(
        [
            choice(ascii_letters + digits + punctuation.replace("-", ""))
            for _ in range(UNIQUE_SUFFIX_LENGTH)
        ]
    )
