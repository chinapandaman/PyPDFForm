# -*- coding: utf-8 -*-
"""Contains user input adapters."""

from os.path import isfile
from typing import Any, BinaryIO, Union


def readable(obj: Any) -> bool:
    """Checks if an object is readable."""

    return callable(getattr(obj, "read", None))


def fp_or_f_obj_or_stream_to_stream(
    fp_or_f_obj_or_stream: Union[bytes, str, BinaryIO]
) -> Union[bytes, None]:
    """Converts a file path or a file object to a stream."""

    result = None
    if isinstance(fp_or_f_obj_or_stream, bytes):
        result = fp_or_f_obj_or_stream

    elif readable(fp_or_f_obj_or_stream):
        result = fp_or_f_obj_or_stream.read()

    elif isinstance(fp_or_f_obj_or_stream, str):
        if not isfile(fp_or_f_obj_or_stream):
            result = None

        else:
            with open(fp_or_f_obj_or_stream, "rb+") as _file:
                result = _file.read()
    return result
