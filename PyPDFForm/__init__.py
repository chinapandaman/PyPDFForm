# -*- coding: utf-8 -*-

from .middleware.wrapper import PyPDFForm as Wrapper
from .middleware.wrapper import WrapperV2

PyPDFForm = Wrapper
PyPDFForm2 = WrapperV2

__version__ = "0.3.8"
