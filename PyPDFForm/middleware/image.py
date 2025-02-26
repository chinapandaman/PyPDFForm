# -*- coding: utf-8 -*-
"""Contains image field middleware."""

from .signature import Signature


class Image(Signature):
    """A class to represent an image field widget."""

    preserve_aspect_ratio = False
