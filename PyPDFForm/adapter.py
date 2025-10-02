# -*- coding: utf-8 -*-
"""
Module for adapting different types of input to a consistent byte stream.

This module provides utility functions to adapt various types of input,
such as file paths, file-like objects, and byte streams, into a consistent
byte stream format. This is particularly useful when dealing with PDF form
filling operations, where the input PDF template can be provided in different
forms. The module ensures that the input is properly converted into a byte
stream before further processing.
"""

from os.path import isfile
from typing import Any, BinaryIO, Union


def readable(obj: Any) -> bool:
    """
    Check if an object has a readable "read" attribute.

    This function determines whether the provided object has a "read" attribute that is callable.
    It is used to identify file-like objects or streams that can be read from.

    Args:
        obj (Any): The object to check for a readable "read" attribute.

    Returns:
        bool: True if the object has a callable "read" attribute, indicating it is readable.
              Returns False otherwise.
    """
    return callable(getattr(obj, "read", None))


def fp_or_f_obj_or_stream_to_stream(
    fp_or_f_obj_or_stream: Union[bytes, str, BinaryIO],
) -> bytes:
    """
    Adapt a file path, file object, or stream to a byte stream.

    This function takes a file path, a file object, or a byte stream and adapts it to a consistent byte stream.
    It handles different input types, including:
        - byte streams (bytes)
        - file paths (str)
        - file-like objects with a read() method (BinaryIO)

    Args:
        fp_or_f_obj_or_stream (Union[bytes, str, BinaryIO]): The input to adapt.
            It can be a byte stream, a file path (string), or a file object.

    Returns:
        bytes: The byte stream representation of the input.
               Returns an empty byte string if the file path does not exist.
    """
    # not cached to handle writing to the same disk file
    result = b""
    if isinstance(fp_or_f_obj_or_stream, bytes):
        result = fp_or_f_obj_or_stream

    elif readable(fp_or_f_obj_or_stream):
        result = fp_or_f_obj_or_stream.read()

    elif isinstance(fp_or_f_obj_or_stream, str):
        if not isfile(fp_or_f_obj_or_stream):
            pass
        else:
            with open(fp_or_f_obj_or_stream, "rb") as _file:
                result = _file.read()
    return result
