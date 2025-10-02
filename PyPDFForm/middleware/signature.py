# -*- coding: utf-8 -*-
"""
Module representing a signature widget.

This module defines the Signature class, which is a subclass of the
Widget class. It represents a signature form field in a PDF document,
allowing users to add their signature as an image.
"""

from os.path import expanduser
from typing import Union

from ..adapter import fp_or_f_obj_or_stream_to_stream
from .base import Widget


class Signature(Widget):
    """
    Represents a signature widget.

    The Signature class provides a concrete implementation for
    signature form fields. It inherits from the Widget class and
    implements the schema_definition, sample_value, and stream
    properties.
    """

    preserve_aspect_ratio: bool = True

    @property
    def schema_definition(self) -> dict:
        """
        Returns the schema definition for the signature.

        The schema definition is a dictionary that describes the
        data type and other constraints for the signature value,
        which is expected to be a string representing the path to
        the signature image.

        Returns:
            dict: A dictionary representing the schema definition.
        """
        return {"type": "string", **super().schema_definition}

    @property
    def sample_value(self) -> str:
        """
        Returns a sample value for the signature.

        The sample value is used to generate example data for the
        signature field. It returns the path to a sample image file.

        Returns:
            str: A sample value for the signature.
        """
        return expanduser("~/Downloads/sample_image.jpg")

    @property
    def stream(self) -> Union[bytes, None]:
        """
        Returns the stream of the signature image.

        This method reads the signature image from the file path
        specified in the value attribute and returns the image data
        as a stream of bytes.

        Returns:
            Union[bytes, None]: The stream of the signature image.
        """
        return (
            fp_or_f_obj_or_stream_to_stream(self.value)
            if self.value is not None
            else None
        )
