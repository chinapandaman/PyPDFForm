# -*- coding: utf-8 -*-
"""Contains user input adapters."""

import os
from typing import Union, BinaryIO


class FileAdapter:
    """Contains methods for adapting user inputs for files."""

    @staticmethod
    def fp_or_f_obj_or_stream_to_stream(fp_or_f_obj_or_stream: Union[bytes, str, BinaryIO]) -> Union[bytes, None]:
        if isinstance(fp_or_f_obj_or_stream, bytes):
            return fp_or_f_obj_or_stream

        if callable(getattr(fp_or_f_obj_or_stream, "read", None)):
            return fp_or_f_obj_or_stream.read()

        if isinstance(fp_or_f_obj_or_stream, str):
            if not os.path.isfile(fp_or_f_obj_or_stream):
                return None

            with open(fp_or_f_obj_or_stream, "rb+") as f:
                return f.read()

        return None
