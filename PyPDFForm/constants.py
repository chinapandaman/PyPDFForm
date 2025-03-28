# -*- coding: utf-8 -*-
"""Contains library constants."""

from typing import Union

from .middleware.checkbox import Checkbox
from .middleware.dropdown import Dropdown
from .middleware.image import Image
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

WIDGET_TYPES = Union[Text, Checkbox, Radio, Dropdown, Signature, Image]

DEPRECATION_NOTICE = "{} will be deprecated soon. Use {} instead."

Annots = "/Annots"
A = "/A"
JS = "/JS"
T = "/T"
TU = "/TU"
Rect = "/Rect"
FT = "/FT"
Parent = "/Parent"
Ff = "/Ff"
Tx = "/Tx"
V = "/V"
AP = "/AP"
N = "/N"
Sig = "/Sig"
DA = "/DA"
DV = "/DV"
Btn = "/Btn"
MaxLen = "/MaxLen"
Q = "/Q"
Ch = "/Ch"
Opt = "/Opt"
MK = "/MK"
CA = "/CA"
BC = "/BC"
BG = "/BG"
BS = "/BS"
W = "/W"
S = "/S"
D = "/D"
U = "/U"
AS = "/AS"
Yes = "/Yes"
Off = "/Off"

# For Adobe Acrobat
AcroForm = "/AcroForm"
Root = "/Root"
NeedAppearances = "/NeedAppearances"

# Field flag bits
READ_ONLY = 1 << 0
MULTILINE = 1 << 12
COMB = 1 << 24

FONT_SIZE_IDENTIFIER = "Tf"
FONT_COLOR_IDENTIFIER = " rg"
DEFAULT_BORDER_WIDTH = 1
DEFAULT_FONT = "Helvetica"
DEFAULT_FONT_SIZE = 12
DEFAULT_FONT_COLOR = (0, 0, 0)
PREVIEW_FONT_COLOR = (1, 0, 0)

NEW_LINE_SYMBOL = "\n"

IMAGE_FIELD_IDENTIFIER = "event.target.buttonImportIcon();"

DEFAULT_CHECKBOX_STYLE = "\u2713"
DEFAULT_RADIO_STYLE = "\u25cf"
BUTTON_STYLES = {
    "4": "\u2713",  # check
    "5": "\u00d7",  # cross
    "l": "\u25cf",  # circle
}

COORDINATE_GRID_FONT_SIZE_MARGIN_RATIO = DEFAULT_FONT_SIZE / 100
UNIQUE_SUFFIX_LENGTH = 20

# Used for adjusting paragraph font size
FONT_SIZE_REDUCE_STEP = 0.5
MARGIN_BETWEEN_LINES = 2
