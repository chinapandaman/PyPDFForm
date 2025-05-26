# -*- coding: utf-8 -*-
"""Module for adapting different types of input to a consistent byte stream."""


from os.path import isfile
from typing import Any, BinaryIO, Union


def readable(obj: Any) -> bool:
    """Check if an object has a readable "read" attribute.

    Args:
        obj (Any): The object to check.

    Returns:
        bool: True if the object has a callable "read" attribute, False otherwise.
    """
    return callable(getattr(obj, "read", None))


def fp_or_f_obj_or_stream_to_stream(
    fp_or_f_obj_or_stream: Union[bytes, str, BinaryIO],
) -> bytes:
    """Adapt a file path, file object, or stream to a byte stream.

    Args:
        fp_or_f_obj_or_stream (Union[bytes, str, BinaryIO]): The input to adapt.
            It can be a byte stream, a file path (string), or a file object.

    Returns:
        bytes: The byte stream representation of the input.
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
