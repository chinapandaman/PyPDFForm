# -*- coding: utf-8 -*-
"""Provides adapters for handling different types of file inputs.

This module contains utility functions for working with various file input types:
- Raw bytes
- File paths
- File-like objects

The adapters normalize these different input types into consistent byte streams
that can be processed by the PDF manipulation functions.
"""

from os.path import isfile
from typing import Any, BinaryIO, Union


def readable(obj: Any) -> bool:
    """Determines if an object is file-like and readable.

    Checks if the object has a callable read() method, indicating it can be
    treated as a file-like object for reading operations.

    Args:
        obj: The object to check for read capability

    Returns:
        bool: True if the object has a callable read() method, False otherwise

    Example:
        >>> readable(open('file.txt'))  # Returns True
        >>> readable(b'bytes')  # Returns False
    """

    return callable(getattr(obj, "read", None))


def fp_or_f_obj_or_stream_to_stream(
    fp_or_f_obj_or_stream: Union[bytes, str, BinaryIO],
) -> bytes:
    """Converts various file input types to a byte stream.

    Handles conversion of:
    - Raw bytes (passed through unchanged)
    - File paths (reads file contents)
    - File-like objects (reads using read() method)

    Args:
        fp_or_f_obj_or_stream: Input to convert, which can be:
            - bytes: Raw PDF data
            - str: Path to PDF file
            - BinaryIO: File-like object containing PDF data

    Returns:
        bytes: The PDF data as a byte stream

    Example:
        >>> # From file path
        >>> data = fp_or_f_obj_or_stream_to_stream("form.pdf")
        >>> # From file object  
        >>> with open("form.pdf", "rb") as f:
        ...     data = fp_or_f_obj_or_stream_to_stream(f)
        >>> # From bytes
        >>> data = fp_or_f_obj_or_stream_to_stream(b"%PDF-1.4...")
    """

    result = b""
    if isinstance(fp_or_f_obj_or_stream, bytes):
        result = fp_or_f_obj_or_stream

    elif readable(fp_or_f_obj_or_stream):
        result = fp_or_f_obj_or_stream.read()

    elif isinstance(fp_or_f_obj_or_stream, str):
        if not isfile(fp_or_f_obj_or_stream):
            pass
        else:
            with open(fp_or_f_obj_or_stream, "rb+") as _file:
                result = _file.read()
    return result
