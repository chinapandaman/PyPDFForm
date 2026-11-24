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

from enum import Enum

VERSION_IDENTIFIER_PREFIX = "%PDF-".encode("utf-8")


class PdfVersion(str, Enum):
    """PDF versions supported by PyPDFForm."""

    pdf_1_0 = "1.0"
    pdf_1_1 = "1.1"
    pdf_1_2 = "1.2"
    pdf_1_3 = "1.3"
    pdf_1_4 = "1.4"
    pdf_1_5 = "1.5"
    pdf_1_6 = "1.6"
    pdf_1_7 = "1.7"
    pdf_2_0 = "2.0"


PDF_VERSIONS = tuple(version.value for version in PdfVersion)
VERSION_IDENTIFIERS = [
    VERSION_IDENTIFIER_PREFIX + version.encode() for version in PDF_VERSIONS
]

DEPRECATION_NOTICE = "{} will be deprecated soon."
DEPRECATION_REPLACE_NOTICE = "Use {} instead."
UNEXPECTED_KWARG_NOTICE = "{}() got an unexpected keyword argument '{}'."
REMOVED_KWARG_NOTICE = "It was removed in PyPDFForm {}. {}"
SUPPORTED_KWARGS_NOTICE = "Supported keyword arguments: {}."
# method name -> removed keyword -> (version removed, migration guidance)
REMOVED_KWARGS = {
    "__init__": {
        "preserve_metadata": (
            "6.0.0",
            "Remove it; input PDF metadata is preserved automatically.",
        ),
    },
    "fill": {
        "flatten": (
            "6.0.0",
            "Use readonly=True to make fields read-only; there is no form-flattening replacement.",
        ),
    },
}

Title = "/Title"
Root = "/Root"
Annots = "/Annots"
Annot = "/Annot"
P = "/P"
B = "/B"
Link = "/Link"
Dest = "/Dest"
Contents = "/Contents"
Widget = "/Widget"
XObject = "/XObject"
Form = "/Form"
BBox = "/BBox"
Matrix = "/Matrix"
T = "/T"
TU = "/TU"
Rect = "/Rect"
FT = "/FT"
Parent = "/Parent"
Kids = "/Kids"
Ff = "/Ff"
F = "/F"
Tx = "/Tx"
V = "/V"
AP = "/AP"
I = "/I"  # noqa: E741
N = "/N"
R = "/R"
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
MK = "/MK"
BC = "/BC"
BS = "/BS"
W = "/W"
H = "/H"
TP = "/TP"
IF = "/IF"

# javascript
A = "/A"
AA = "/AA"
Action = "/Action"
S = "/S"
GoTo = "/GoTo"
ResetForm = "/ResetForm"
SubmitForm = "/SubmitForm"
Hide = "/Hide"
Next = "/Next"
Flags = "/Flags"
JavaScript = "/JavaScript"
JS = "/JS"
OpenAction = "/OpenAction"
# navigation node forward and backward actions
NA = "/NA"
PA = "/PA"
E = "/E"
X = "/X"
D = "/D"
U = "/U"
Fo = "/Fo"
Bl = "/Bl"

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
Fields = "/Fields"
CO = "/CO"
XFA = "/XFA"

# action type -> the entry that names the fields or annotations it acts on
NAMED_TARGETS = {ResetForm: Fields, SubmitForm: Fields, Hide: T}
# ResetForm and SubmitForm flag bit: act on every field except the named ones
INCLUDE_EXCLUDE = 1 << 0

# Field flag bits
READ_ONLY = 1 << 0
REQUIRED = 1 << 1
MULTILINE = 1 << 12
RADIO = 1 << 15
PUSHBUTTON = 1 << 16
COMB = 1 << 24

# annotation flag bits
HIDDEN = 1 << 1

# entries read when choosing a PDF version
Info = "/Info"
Version = "/Version"
ToUnicode = "/ToUnicode"
SMask = "/SMask"
URI = "/URI"
CA = "/CA"
ca = "/ca"

# Minimum PDF versions of the features that PyPDFForm can add, from the
# "(PDF 1.x)" marks of the PDF Reference
FEATURE_VERSIONS_BY_KEY = {
    # an annotation's title; fields, Hide actions, and threads are 1.1 or later
    T: "1.1",
    FontFile2: "1.1",
    OpenAction: "1.1",
    AcroForm: "1.2",
    ToUnicode: "1.2",
    TU: "1.3",
    SMask: "1.4",
}
FEATURE_VERSIONS_BY_SUBTYPE = {
    Widget: "1.2",
    "/Stamp": "1.3",
    "/Highlight": "1.3",
    "/Underline": "1.3",
    "/StrikeOut": "1.3",
    "/Squiggly": "1.4",
}
FEATURE_VERSIONS_BY_ACTION = {URI: "1.1", JavaScript: "1.3"}
FEATURE_VERSIONS_BY_FILTER = {FlateDecode: "1.2"}
FEATURE_VERSIONS_BY_FIELD_TYPE = {Sig: "1.3"}
TITLE_VERSION = "1.1"  # the title in the document information dictionary
ALPHA_VERSION = "1.4"  # a numeric /CA or /ca, for constant opacity
COMB_VERSION = "1.5"  # also RadiosInUnison, the same bit for radio buttons
# widget property hooks that write a JavaScript action, whatever the script
JAVASCRIPT_HOOKS = frozenset(
    {
        "update_field_on_hovered_over_javascript",
        "update_field_on_hovered_off_javascript",
        "update_field_on_mouse_pressed_javascript",
        "update_field_on_mouse_released_javascript",
        "update_field_on_focused_javascript",
        "update_field_on_blurred_javascript",
    }
)
# widget property hooks that can add or remove a feature above: comb (1.5),
# tooltips (/TU), and JavaScript actions; PdfWrapper.version applies them to
# a copy of the PDF while they are queued
FEATURE_HOOKS = (
    frozenset({"update_text_field_comb", "update_field_tooltip"}) | JAVASCRIPT_HOOKS
)
# the font hook, whose user-facing font names PdfWrapper maps to resource names
FONT_HOOK = "update_text_field_font"
# widget property hooks that change the default appearance (/DA), which a
# field can inherit from its ancestors or the AcroForm; they get the AcroForm
DEFAULT_APPEARANCE_HOOKS = frozenset(
    {
        FONT_HOOK,
        "update_text_field_font_size",
        "update_text_field_font_color",
    }
)
# no feature above needs a newer version, so newer documents are never raised
NEWEST_FEATURE_VERSION = max(
    [
        *FEATURE_VERSIONS_BY_KEY.values(),
        *FEATURE_VERSIONS_BY_SUBTYPE.values(),
        *FEATURE_VERSIONS_BY_ACTION.values(),
        *FEATURE_VERSIONS_BY_FILTER.values(),
        *FEATURE_VERSIONS_BY_FIELD_TYPE.values(),
        TITLE_VERSION,
        ALPHA_VERSION,
        COMB_VERSION,
    ],
    key=lambda version: tuple(int(part) for part in version.split(".")),
)

# reportlab acroform func
fieldFlags = "fieldFlags"
required = "required"

DEFAULT_FONT = "Helvetica"
DEFAULT_FONT_SIZE = 12
DEFAULT_FONT_COLOR = (0, 0, 0)

IMAGE_IMPORT_JAVASCRIPT = "event.target.buttonImportIcon();"

COORDINATE_GRID_FONT_SIZE_MARGIN_RATIO = DEFAULT_FONT_SIZE / 100
UNIQUE_SUFFIX_LENGTH = 20

# blank page
BLANK_PAGE_DEFAULT_WIDTH = 612
BLANK_PAGE_DEFAULT_HEIGHT = 792
