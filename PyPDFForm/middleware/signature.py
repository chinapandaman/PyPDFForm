# -*- coding: utf-8 -*-
"""Provides middleware for PDF signature field widgets.

This module contains the Signature class which handles:
- Signature image processing
- Aspect ratio preservation
- File path resolution
- PDF form field integration
"""

from os.path import expanduser
from typing import BinaryIO, Union

from ..adapter import fp_or_f_obj_or_stream_to_stream
from .base import Widget


class Signature(Widget):
    """Middleware for PDF signature field widgets.

    Handles all aspects of signature field processing including:
    - Signature image handling
    - Aspect ratio control
    - File path resolution
    - PDF form field integration

    Inherits from Widget base class and extends it with signature-specific features.
    """

    preserve_aspect_ratio = True
    """Whether to preserve the original image's aspect ratio when scaling."""

    def __init__(
        self,
        name: str,
        value: Union[bytes, str, BinaryIO] = None,
    ) -> None:
        """Initializes a new signature field widget.

        Args:
            name: Field name/key for the signature
            value: Signature image as bytes, file path, or file object (default: None)
        """

        super().__init__(name, value)

    @property
    def schema_definition(self) -> dict:
        """Generates a JSON schema definition for the signature field.

        Returns:
            dict: Schema properties including:
                - type: string (file path)
                - description (if available from base class)
        """

        return {"type": "string"}

    @property
    def sample_value(self) -> str:
        """Generates a sample value for the signature field.

        Returns a default sample image path from the user's Downloads folder.

        Returns:
            str: Path to sample image file
        """

        return expanduser("~/Downloads/sample_image.jpg")

    @property
    def stream(self) -> Union[bytes, None]:
        """Converts the signature image to a byte stream.

        Handles conversion of:
        - Raw image bytes
        - File paths
        - File-like objects

        Returns:
            Union[bytes, None]: Image data as bytes, or None if no value set
        """

        return (
            fp_or_f_obj_or_stream_to_stream(self.value)
            if self.value is not None
            else None
        )
