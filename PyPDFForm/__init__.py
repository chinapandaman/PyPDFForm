# -*- coding: utf-8 -*-
"""Contains v1 and v2 wrappers."""

from .middleware.wrapper import PyPDFForm as Wrapper
from .middleware.wrapper_v2 import WrapperV2

PyPDFForm = Wrapper
PyPDFForm2 = WrapperV2

__version__ = "1.2.1"
