# -*- coding: utf-8 -*-
"""
Module representing an image widget.

This module defines the Image class, which is a subclass of the
Signature class. It represents an image form field in a PDF document,
allowing users to add images to the form.
"""

from .signature import Signature


class Image(Signature):
    """
    Represents an image widget.

    The Image class provides a concrete implementation for
    image form fields. It inherits from the Signature class and
    sets the preserve_aspect_ratio attribute to False by default.
    """

    preserve_aspect_ratio: bool = False
