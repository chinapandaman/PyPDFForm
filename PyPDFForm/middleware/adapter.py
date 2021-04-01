# -*- coding: utf-8 -*-
"""Contains user input adapters."""

from typing import Union, BinaryIO


class FileAdapter:
    """Contains methods for adapting user inputs for files."""

    @staticmethod
    def fp_or_f_obj_to_stream(fp_or_f_obj: Union[str, BinaryIO]) -> bytes:
        if callable(getattr(fp_or_f_obj, "read", None)):
            return fp_or_f_obj.read()

        with open(fp_or_f_obj, "rb+") as f:
            return f.read()
