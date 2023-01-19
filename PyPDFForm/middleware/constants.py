# -*- coding: utf-8 -*-
"""Contains constants for middleware layer."""

from typing import Union
from .text import Text
from .checkbox import Checkbox
from .radio import Radio
from .dropdown import Dropdown

GLOBAL_FONT = "Helvetica"
GLOBAL_FONT_SIZE = 12
GLOBAL_FONT_COLOR = (0, 0, 0)
GLOBAL_TEXT_X_OFFSET = 0
GLOBAL_TEXT_Y_OFFSET = 0
GLOBAL_TEXT_WRAP_LENGTH = 100

ELEMENT_TYPES = Union[Text, Checkbox, Radio, Dropdown]
