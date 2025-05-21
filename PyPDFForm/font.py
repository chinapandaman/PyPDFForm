# -*- coding: utf-8 -*-
"""Provides font handling utilities for PDF forms.

This module contains functions for:
- Registering custom fonts from TTF files
- Extracting font information from PDF text appearances
- Calculating font sizes based on widget dimensions
- Adjusting font sizes to fit text within fields
- Managing font colors and properties
"""

from io import BytesIO
from math import sqrt
from re import findall
from typing import Tuple, Union

from pypdf import PdfReader, PdfWriter
from pypdf.generic import (ArrayObject, DictionaryObject, NameObject,
                           NumberObject, StreamObject)
from reportlab.pdfbase.acroform import AcroForm as RAcroForm
from reportlab.pdfbase.pdfmetrics import (registerFont, standardFonts,
                                          stringWidth)
from reportlab.pdfbase.ttfonts import TTFError, TTFont

from .constants import (DEFAULT_FONT, DR, FONT_COLOR_IDENTIFIER,
                        FONT_NAME_PREFIX, FONT_SIZE_IDENTIFIER,
                        FONT_SIZE_REDUCE_STEP, MARGIN_BETWEEN_LINES, AcroForm,
                        BaseFont, Encoding, Fields, Font, FontDescriptor,
                        FontFile2, FontName, Length1, Rect, Subtype, TrueType,
                        Type, WinAnsiEncoding)
from .middleware.text import Text
from .patterns import TEXT_FIELD_APPEARANCE_PATTERNS
from .utils import extract_widget_property, stream_to_io


def register_font(font_name: str, ttf_stream: bytes) -> bool:
    """Registers a TrueType font for use in PDF generation.

    Args:
        font_name: Name to register the font under
        ttf_stream: TTF font data as bytes

    Returns:
        bool: True if registration succeeded, False if failed
    """

    buff = BytesIO()
    buff.write(ttf_stream)
    buff.seek(0)

    try:
        registerFont(TTFont(name=font_name, filename=buff))
        result = True
    except TTFError:
        result = False

    buff.close()
    return result


def register_font_acroform(pdf: bytes, ttf_stream: bytes) -> tuple:
    """Registers a TrueType font in a PDF's AcroForm and returns modified PDF.

    This function handles the registration of a TTF font into a PDF's AcroForm structure,
    creating all necessary font-related objects in the PDF and ensuring proper font
    registration for form fields.

    Args:
        pdf: Input PDF data as bytes to modify
        ttf_stream: TTF font data as bytes to register in the PDF

    Returns:
        tuple: A tuple containing:
            - bytes: Modified PDF data with font registration
            - str: The registered font name (with format '/FontName')

    Note:
        This function performs several PDF object manipulations:
        - Creates font file stream object
        - Builds font descriptor dictionary
        - Registers font in PDF's AcroForm structure
        - Handles font naming and encoding
    """

    base_font_name = (
        f"/{TTFont(name='new_font', filename=stream_to_io(ttf_stream)).face.name.ustr}"
    )
    reader = PdfReader(stream_to_io(pdf))
    writer = PdfWriter()
    writer.append(reader)

    font_file_stream = StreamObject()
    font_file_stream.set_data(ttf_stream)
    font_file_stream.update(
        {
            NameObject(Length1): NumberObject(len(ttf_stream)),
        }
    )
    font_file_ref = writer._add_object(font_file_stream)  # type: ignore # noqa: SLF001 # # pylint: disable=W0212

    font_descriptor = DictionaryObject()
    font_descriptor.update(
        {
            NameObject(Type): NameObject(FontDescriptor),
            NameObject(FontName): NameObject(base_font_name),
            NameObject(FontFile2): font_file_ref,
        }
    )
    font_descriptor_ref = writer._add_object(font_descriptor)  # type: ignore # noqa: SLF001 # # pylint: disable=W0212

    font_dict = DictionaryObject()
    font_dict.update(
        {
            NameObject(Type): NameObject(Font),
            NameObject(Subtype): NameObject(TrueType),
            NameObject(BaseFont): NameObject(base_font_name),
            NameObject(FontDescriptor): font_descriptor_ref,
            NameObject(Encoding): NameObject(WinAnsiEncoding),
        }
    )
    font_dict_ref = writer._add_object(font_dict)  # type: ignore # noqa: SLF001 # # pylint: disable=W0212

    if AcroForm not in writer._root_object:  # type: ignore # noqa: SLF001 # # pylint: disable=W0212
        writer._root_object[NameObject(AcroForm)] = DictionaryObject({NameObject(Fields): ArrayObject([])})  # type: ignore # noqa: SLF001 # # pylint: disable=W0212
    acroform = writer._root_object[AcroForm]  # type: ignore # noqa: SLF001 # # pylint: disable=W0212

    if DR not in acroform:
        acroform[NameObject(DR)] = DictionaryObject()
    dr = acroform[DR]

    if Font not in dr:
        dr[NameObject(Font)] = DictionaryObject()
    fonts = dr[Font]

    new_font_name = get_new_font_name(fonts)
    fonts[NameObject(new_font_name)] = font_dict_ref

    with BytesIO() as f:
        writer.write(f)
        f.seek(0)
        return f.read(), new_font_name


def get_new_font_name(fonts: dict) -> str:
    """Generates a new unique font name for font registration.

    Scans existing font names and generates a new unique name by finding the next
    available numeric suffix. Used when registering new fonts to avoid name conflicts.

    Args:
        fonts: Dictionary of existing font names to check for conflicts.
            Keys should be strings, values are font objects.

    Returns:
        str: New unique font name in format '/F#' where # is the next available number.
            Example: '/F1', '/F2' etc.

    Note:
        - Handles numeric suffixes to ensure uniqueness
        - Skips existing numbers in font names
        - Returns names with prefix '/F' by default
    """

    existing = set()
    for key in fonts:
        if isinstance(key, str) and key.startswith(FONT_NAME_PREFIX):
            existing.add(int(key[2:]))

    n = 1
    while n in existing:
        n += 1
    return f"{FONT_NAME_PREFIX}{n}"


def get_all_available_fonts(pdf: bytes) -> dict:
    """Extracts all available fonts from a PDF's AcroForm resources.

    Scans the PDF's AcroForm DR (Resource Dictionary) Fonts section to collect
    all registered fonts and their corresponding resource keys.

    Args:
        pdf: Input PDF data as bytes to scan for fonts

    Returns:
        dict: Dictionary mapping base font names (str) to their resource keys (str).
            Returns empty dictionary if:
            - PDF has no AcroForm
            - AcroForm has no DR (Resource Dictionary)
            - DR has no Fonts section

    Example:
        {
            '/Helvetica': '/F1',
            '/Times-Roman': '/F2'
        }
    """

    reader = PdfReader(stream_to_io(pdf))
    try:
        fonts = reader.root_object[AcroForm][DR][Font]
    except KeyError:
        return {}

    result = {}
    for key, value in fonts.items():
        result[value[BaseFont]] = key

    return result


def extract_font_from_text_appearance(text_appearance: str) -> Union[str, None]:
    """Extracts font name from PDF text appearance string.

    Parses the font information embedded in PDF text field appearance strings.

    Args:
        text_appearance: PDF text appearance string (/DA field)

    Returns:
        Union[str, None]: Font name if found, None if not found
    """

    text_appearances = text_appearance.split(" ")

    for each in text_appearances:
        if each.startswith("/"):
            text_segments = findall("[A-Z][^A-Z]*", each.replace("/", ""))

            if len(text_segments) == 1:
                for k, v in RAcroForm.formFontNames.items():
                    if v == text_segments[0]:
                        return k

            for font in standardFonts:
                font_segments = findall("[A-Z][^A-Z]*", font.replace("-", ""))
                if len(font_segments) != len(text_segments):
                    continue

                found = True
                for i, val in enumerate(font_segments):
                    if not val.startswith(text_segments[i]):
                        found = False

                if found:
                    return font

    return None


def auto_detect_font(widget: dict) -> str:
    """Attempts to detect the font used in a PDF text field widget.

    Falls back to DEFAULT_FONT if detection fails.

    Args:
        widget: PDF form widget dictionary

    Returns:
        str: Detected font name or DEFAULT_FONT
    """

    text_appearance = extract_widget_property(
        widget, TEXT_FIELD_APPEARANCE_PATTERNS, None, None
    )

    if not text_appearance:
        return DEFAULT_FONT

    return extract_font_from_text_appearance(text_appearance) or DEFAULT_FONT


def text_field_font_size(widget: dict) -> Union[float, int]:
    """Calculates an appropriate font size based on text field dimensions.

    Args:
        widget: PDF form widget dictionary containing Rect coordinates

    Returns:
        Union[float, int]: Suggested font size in points
    """

    height = abs(float(widget[Rect][1]) - float(widget[Rect][3]))

    return height * 2 / 3


def checkbox_radio_font_size(widget: dict) -> Union[float, int]:
    """Calculates appropriate symbol size for checkbox/radio widgets.

    Args:
        widget: PDF form widget dictionary containing Rect coordinates

    Returns:
        Union[float, int]: Suggested symbol size in points
    """

    area = abs(float(widget[Rect][0]) - float(widget[Rect][2])) * abs(
        float(widget[Rect][1]) - float(widget[Rect][3])
    )

    return sqrt(area) * 72 / 96


def get_text_field_font_size(widget: dict) -> Union[float, int]:
    """Extracts font size from PDF text field appearance properties.

    Args:
        widget: PDF form widget dictionary

    Returns:
        Union[float, int]: Font size in points if found, otherwise 0
    """

    result = 0
    text_appearance = extract_widget_property(
        widget, TEXT_FIELD_APPEARANCE_PATTERNS, None, None
    )
    if text_appearance:
        properties = text_appearance.split(" ")
        for i, val in enumerate(properties):
            if val.startswith(FONT_SIZE_IDENTIFIER):
                return float(properties[i - 1])

    return result


def get_text_field_font_color(
    widget: dict,
) -> Union[Tuple[float, float, float], None]:
    """Extracts font color from PDF text field appearance properties.

    Args:
        widget: PDF form widget dictionary

    Returns:
        Union[Tuple[float, float, float], None]: RGB color tuple (0-1 range)
            or black by default if not specified
    """

    result = (0, 0, 0)
    text_appearance = extract_widget_property(
        widget, TEXT_FIELD_APPEARANCE_PATTERNS, None, None
    )
    if text_appearance:
        if FONT_COLOR_IDENTIFIER not in text_appearance:
            return result

        text_appearance = text_appearance.split(" ")
        for i, val in enumerate(text_appearance):
            if val.startswith(FONT_COLOR_IDENTIFIER.replace(" ", "")):
                result = (
                    float(text_appearance[i - 3]),
                    float(text_appearance[i - 2]),
                    float(text_appearance[i - 1]),
                )
                break

    return result


def adjust_paragraph_font_size(widget: dict, widget_middleware: Text) -> None:
    """Dynamically reduces font size until text fits in paragraph field.

    Args:
        widget: PDF form widget dictionary
        widget_middleware: Text middleware instance containing text properties
    """

    # pylint: disable=C0415, R0401
    from .template import get_paragraph_lines

    height = abs(float(widget[Rect][1]) - float(widget[Rect][3]))

    while (
        widget_middleware.font_size > FONT_SIZE_REDUCE_STEP
        and len(widget_middleware.text_lines)
        * (widget_middleware.font_size + MARGIN_BETWEEN_LINES)
        > height
    ):
        widget_middleware.font_size -= FONT_SIZE_REDUCE_STEP
        widget_middleware.text_lines = get_paragraph_lines(widget, widget_middleware)


def adjust_text_field_font_size(widget: dict, widget_middleware: Text) -> None:
    """Dynamically reduces font size until text fits in text field.

    Args:
        widget: PDF form widget dictionary
        widget_middleware: Text middleware instance containing text properties
    """

    width = abs(float(widget[Rect][0]) - float(widget[Rect][2]))

    while (
        widget_middleware.font_size > FONT_SIZE_REDUCE_STEP
        and stringWidth(
            widget_middleware.value, widget_middleware.font, widget_middleware.font_size
        )
        > width
    ):
        widget_middleware.font_size -= FONT_SIZE_REDUCE_STEP
