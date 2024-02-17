# -*- coding: utf-8 -*-
"""Contains constants for middleware layer."""

from typing import Union

from .middleware.checkbox import Checkbox
from .middleware.dropdown import Dropdown
from .middleware.radio import Radio
from .middleware.signature import Signature
from .middleware.text import Text

VERSION_IDENTIFIERS = [
    b"%PDF-1.0",
    b"%PDF-1.1",
    b"%PDF-1.2",
    b"%PDF-1.3",
    b"%PDF-1.4",
    b"%PDF-1.5",
    b"%PDF-1.6",
    b"%PDF-1.7",
    b"%PDF-2.0",
]
VERSION_IDENTIFIER_PREFIX = b"%PDF-"

WIDGET_TYPES = Union[Text, Checkbox, Radio, Dropdown, Signature]

DEPRECATION_NOTICE = "{} will be deprecated soon. Use {} instead."

ANNOTATION_FIELD_KEY = "/T"
ANNOTATION_RECTANGLE_KEY = "/Rect"
