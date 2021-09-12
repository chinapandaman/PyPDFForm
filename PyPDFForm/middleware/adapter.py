# -*- coding: utf-8 -*-
"""Contains user input adapters."""

import os
from typing import Any, BinaryIO, Union


class FileAdapter:
    """Contains methods for adapting user inputs for files."""

    @staticmethod
    def readable(obj: Any) -> bool:
        """Checks if an object is readable."""

        return callable(getattr(obj, "read", None))

    def fp_or_f_obj_or_stream_to_stream(
        self, fp_or_f_obj_or_stream: Union[bytes, str, BinaryIO]
    ) -> Union[bytes, None]:
        """Converts a file path or a file object to a stream."""

        if isinstance(fp_or_f_obj_or_stream, bytes):
            return fp_or_f_obj_or_stream

        if self.readable(fp_or_f_obj_or_stream):
            return fp_or_f_obj_or_stream.read()

        if isinstance(fp_or_f_obj_or_stream, str):
            if not os.path.isfile(fp_or_f_obj_or_stream):
                return None

            with open(fp_or_f_obj_or_stream, "rb+") as _file:
                return _file.read()

        return None
