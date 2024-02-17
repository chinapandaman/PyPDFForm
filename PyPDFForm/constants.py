# -*- coding: utf-8 -*-
"""Contains library constants."""

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
SUBTYPE_KEY = "/Subtype"
WIDGET_SUBTYPE_KEY = "/Widget"
WIDGET_TYPE_KEY = "/FT"
PARENT_KEY = "/Parent"
FIELD_FLAG_KEY = "/Ff"
TEXT_FIELD_IDENTIFIER = "/Tx"
SIGNATURE_FIELD_IDENTIFIER = "/Sig"
TEXT_FIELD_APPEARANCE_IDENTIFIER = "/DA"
SELECTABLE_IDENTIFIER = "/Btn"
TEXT_FIELD_MAX_LENGTH_KEY = "/MaxLen"
TEXT_FIELD_ALIGNMENT_IDENTIFIER = "/Q"
CHOICE_FIELD_IDENTIFIER = "/Ch"
CHOICES_IDENTIFIER = "/Opt"
BUTTON_IDENTIFIER = "/MK"
BUTTON_STYLE_IDENTIFIER = "/CA"

# Field flag bits
MULTILINE = 1 << 12
COMB = 1 << 24

FONT_SIZE_IDENTIFIER = "Tf"
FONT_COLOR_IDENTIFIER = " rg"
DEFAULT_FONT = "Helvetica"
DEFAULT_FONT_SIZE = 12
DEFAULT_FONT_COLOR = (0, 0, 0)
PREVIEW_FONT_COLOR = (1, 0, 0)

NEW_LINE_SYMBOL = "\n"

DEFAULT_CHECKBOX_STYLE = "\u2713"
DEFAULT_RADIO_STYLE = "\u25CF"
BUTTON_STYLES = {
    "4": "\u2713",
    "5": "\u00D7",
    "l": "\u25CF",
}

COORDINATE_GRID_FONT_SIZE_MARGIN_RATIO = DEFAULT_FONT_SIZE / 100
