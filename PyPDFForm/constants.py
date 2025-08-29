# -*- coding: utf-8 -*-
"""
Module containing constants used throughout the PyPDFForm library.

This module defines a collection of constants that are used across various
modules within the PyPDFForm library. These constants include:

- String identifiers for PDF syntax elements (e.g., /Annots, /Rect, /FT).
- Numerical values representing field flags (e.g., READ_ONLY, MULTILINE).
- Default values for fonts, font sizes, and font colors.
- Identifiers for image fields and coordinate grid calculations.
- Version identifiers for PDF versions.

Using constants improves code readability and maintainability by providing
meaningful names for frequently used values and reducing the risk of typos.
"""

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
VERSION_IDENTIFIER_PREFIX = "%PDF-".encode("utf-8")

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
I = "/I"  # noqa: E741
N = "/N"
Sig = "/Sig"
DA = "/DA"
DR = "/DR"
DV = "/DV"
Btn = "/Btn"
MaxLen = "/MaxLen"
Q = "/Q"
Ch = "/Ch"
Opt = "/Opt"
AS = "/AS"
Yes = "/Yes"
Off = "/Off"

# Font dict
Length = "/Length"
Length1 = "/Length1"
Type = "/Type"
FontDescriptor = "/FontDescriptor"
FontName = "/FontName"
FontFile2 = "/FontFile2"
Font = "/Font"
Subtype = "/Subtype"
TrueType = "/TrueType"
BaseFont = "/BaseFont"
Filter = "/Filter"
FlateDecode = "/FlateDecode"
Encoding = "/Encoding"
WinAnsiEncoding = "/WinAnsiEncoding"
Widths = "/Widths"
FirstChar = "/FirstChar"
LastChar = "/LastChar"
MissingWidth = "/MissingWidth"
FontHead = "head"
FontCmap = "cmap"
FontHmtx = "hmtx"
FontNotdef = ".notdef"

FIRST_CHAR_CODE = 0
LAST_CHAR_CODE = 255
ENCODING_TABLE_SIZE = 256
EM_TO_PDF_FACTOR = 1000
DEFAULT_ASSUMED_GLYPH_WIDTH = 300

Resources = "/Resources"
FONT_NAME_PREFIX = "/F"

# For Adobe Acrobat
AcroForm = "/AcroForm"
Root = "/Root"
Fields = "/Fields"
XFA = "/XFA"

# Field flag bits
READ_ONLY = 1 << 0
REQUIRED = 1 << 1
MULTILINE = 1 << 12
COMB = 1 << 24

# reportlab acroform func
fieldFlags = "fieldFlags"
required = "required"

FONT_SIZE_IDENTIFIER = "Tf"
FONT_COLOR_IDENTIFIER = " rg"
DEFAULT_FONT = "Helvetica"
DEFAULT_FONT_SIZE = 12
DEFAULT_FONT_COLOR = (0, 0, 0)

IMAGE_FIELD_IDENTIFIER = "event.target.buttonImportIcon();"

COORDINATE_GRID_FONT_SIZE_MARGIN_RATIO = DEFAULT_FONT_SIZE / 100
UNIQUE_SUFFIX_LENGTH = 20

SLASH = "/"
