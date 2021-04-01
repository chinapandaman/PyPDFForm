# -*- coding: utf-8 -*-
"""Contains user input adapters."""

from typing import Union, BinaryIO


class FileAdapter:
    """Contains methods for adapting user inputs for files."""

    @staticmethod
    def fp_or_f_obj_or_stream_to_stream(fp_or_f_obj_or_stream: Union[str, BinaryIO]) -> bytes:
        if isinstance(fp_or_f_obj_or_stream, bytes):
            return fp_or_f_obj_or_stream

        if callable(getattr(fp_or_f_obj_or_stream, "read", None)):
            return fp_or_f_obj_or_stream.read()

        with open(fp_or_f_obj_or_stream, "rb+") as f:
            return f.read()
