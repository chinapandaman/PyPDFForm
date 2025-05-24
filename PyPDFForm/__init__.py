# -*- coding: utf-8 -*-

__version__ = "2.5.0"

from .middleware.text import Text
from .wrapper import PdfWrapper

__all__ = ["PdfWrapper", "Text"]
