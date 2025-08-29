# -*- coding: utf-8 -*-
"""
This module provides functionalities for handling custom fonts within PDF documents.

It includes functions for registering fonts with ReportLab and within the PDF's AcroForm,
allowing these fonts to be used when filling form fields. The module also provides utilities
for extracting font information from TTF streams and managing font names within a PDF.
"""
# TODO: In `get_additional_font_params`, iterating through `reader.pages[0][Resources][Font].values()` can be inefficient for PDFs with many fonts. Consider building a font lookup dictionary once per PDF or caching results if this function is called frequently with the same PDF.
# TODO: In `register_font_acroform`, `PdfReader(stream_to_io(pdf))` and `writer.append(reader)` involve re-parsing and appending the PDF. For large PDFs, passing `PdfReader` and `PdfWriter` objects directly could reduce overhead.
# TODO: In `register_font_acroform`, `compress(ttf_stream)` can be CPU-intensive. If the same font stream is registered multiple times within a single PDF processing session, consider caching the compressed stream to avoid redundant compression.
# TODO: In `get_new_font_name`, while `existing` is a set, if `n` needs to increment many times due to a dense range of existing font names, the `while` loop could be slow. However, this is likely a minor bottleneck in typical scenarios.
# TODO: In `get_all_available_fonts`, the `replace("/", "")` operation on `BaseFont` could be avoided if font names are consistently handled with or without the leading slash to prevent string manipulation overhead in a loop.

from functools import lru_cache
from io import BytesIO
from typing import Any
from zlib import compress

from pypdf import PdfReader, PdfWriter
from pypdf.generic import (ArrayObject, DictionaryObject, NameObject,
                           NumberObject, StreamObject, FloatObject)
from reportlab.pdfbase.pdfmetrics import registerFont
from reportlab.pdfbase.ttfonts import TTFError, TTFont
from fontTools.ttLib import TTFont as FT_TTFont
from .constants import (DEFAULT_ASSUMED_GLYPH_WIDTH, DR, FONT_NAME_PREFIX, AcroForm, BaseFont, Encoding,
                        Fields, Filter, FlateDecode, Font, FontDescriptor,
                        FontFile2, FontName, Length, Length1, MissingWidth, Resources,
                        Subtype, TrueType, Type, WinAnsiEncoding, Widths,
                        FirstChat, LastChar, FontHmtx, FontHead, FontCmap, FontNotdef,
                        EM_TO_PDF_FACTOR, FIRST_CHAR_CODE, LAST_CHAR_CODE, ENCODING_TABLE_SIZE)

from .utils import stream_to_io

@lru_cache
def register_font(font_name: str, ttf_stream: bytes) -> bool:
    """
    Registers a TrueType font with the ReportLab library.

    This allows the font to be used for generating PDF documents with ReportLab.

    Args:
        font_name (str): The name to register the font under. This name will be used
            to reference the font when creating PDF documents with ReportLab.
        ttf_stream (bytes): The font file data in TTF format. This should be the raw
            bytes of the TTF file.

    Returns:
        bool: True if the font was registered successfully, False otherwise.
            Returns False if a TTFError occurs during registration, which usually
            indicates an invalid TTF stream.
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


def get_additional_font_params(pdf: bytes, base_font_name: str) -> tuple:
    """
    Retrieves additional font parameters from a PDF document for a given base font name.

    This function searches the PDF's resources for a font dictionary matching the provided
    base font name. If a match is found, it extracts the font descriptor parameters and
    the font dictionary parameters. These parameters can be used to further describe
    and define the font within the PDF.

    Args:
        pdf (bytes): The PDF file data as bytes.
        base_font_name (str): The base font name to search for within the PDF's font resources.

    Returns:
        tuple: A tuple containing two dictionaries:
            - font_descriptor_params (dict): A dictionary of font descriptor parameters.
            - font_dict_params (dict): A dictionary of font dictionary parameters.
            Returns empty dictionaries if the font is not found.
    """
    font_descriptor_params = {}
    font_dict_params = {}
    reader = PdfReader(stream_to_io(pdf))
    first_page = reader.get_page(0)

    for font in first_page[Resources][Font].values():
        if base_font_name.replace("/", "") in font[BaseFont]:
            font_descriptor_params = dict(font[FontDescriptor])
            font_dict_params = dict(font)
            break

    return font_descriptor_params, font_dict_params

def compute_font_glyph_widths(ttf_file: BytesIO, missing_width: float):
    """
    Compute glyph advance widths from a TrueType font.

    Args:
        ttf_file (BytesIO): Stream containing the TTF font data.
        missing_width (float): Width to use if the font tables are missing.

    Returns:
        list[float]: Widths scaled to PDF text space units (1000/em).
                     Returns a list filled with `missing_width` if tables are missing.
    """
    font = FT_TTFont(ttf_file)
    head_table: Any = font.get(FontHead)
    cmap_table: Any = font.get(FontCmap)
    hmtx_table: Any = font.get(FontHmtx)

    widths: list[float] = []
    if head_table and cmap_table and hmtx_table:
        cmap: Any = cmap_table.getBestCmap()
        units_per_em: int = head_table.unitsPerEm or 1

        for codepoint in range(ENCODING_TABLE_SIZE):
            glyph_name: str = cmap.get(codepoint, FontNotdef)
            advance_width, _ = hmtx_table[glyph_name]
            pdf_width: float = (advance_width / units_per_em) * EM_TO_PDF_FACTOR
            widths.append(pdf_width)
    else:
        widths: list[float] = [missing_width] * ENCODING_TABLE_SIZE

    return widths

def register_font_acroform(pdf: bytes, ttf_stream: bytes, adobe_mode: bool) -> tuple:
    """
    Registers a TrueType font within the PDF's AcroForm dictionary.

    This allows the font to be used when filling form fields within the PDF.
    The function adds the font as a resource to the PDF, making it available
    for use in form fields.

    Args:
        pdf (bytes): The PDF file data as bytes. This is the PDF document that
            will be modified to include the new font.
        ttf_stream (bytes): The font file data in TTF format as bytes. This is the
            raw data of the TrueType font file.
        adobe_mode (bool): A flag indicating whether to use Adobe-specific font parameters.

    Returns:
        tuple: A tuple containing the modified PDF data as bytes and the new font name
            (str) that was assigned to the registered font within the PDF.
    """
    base_font_name = get_base_font_name(ttf_stream)
    reader = PdfReader(stream_to_io(pdf))
    writer = PdfWriter()
    writer.append(reader)

    font_descriptor_params = {}
    font_dict_params = {}
    if adobe_mode:
        font_descriptor_params, font_dict_params = get_additional_font_params(
            pdf, base_font_name
        )

    font_file_stream = StreamObject()
    compressed_ttf = compress(ttf_stream)
    font_file_stream.set_data(compressed_ttf)
    font_file_stream.update(
        {
            NameObject(Length1): NumberObject(len(ttf_stream)),
            NameObject(Length): NumberObject(len(compressed_ttf)),
            NameObject(Filter): NameObject(FlateDecode),
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
    font_descriptor.update(
        {k: v for k, v in font_descriptor_params.items() if k not in font_descriptor}
    )
    font_descriptor_ref = writer._add_object(font_descriptor)  # type: ignore # noqa: SLF001 # # pylint: disable=W0212

    font_dict = DictionaryObject()
    font_dict.update({
            NameObject(Type): NameObject(Font),
            NameObject(Subtype): NameObject(TrueType),
            NameObject(BaseFont): NameObject(base_font_name),
            NameObject(FontDescriptor): font_descriptor_ref,
            NameObject(Encoding): NameObject(WinAnsiEncoding),
    })

    font_dict.update({k: v for k, v in font_dict_params.items() if k not in font_dict})

    if font_dict and Widths in font_dict:
        ttf_bytes_io = BytesIO(ttf_stream)
        missing_width = font_descriptor.get(MissingWidth, DEFAULT_ASSUMED_GLYPH_WIDTH)
        widths = compute_font_glyph_widths(ttf_bytes_io, missing_width)

        font_dict.update({
            NameObject(FirstChat): NumberObject(FIRST_CHAR_CODE),
            NameObject(LastChar): NumberObject(LAST_CHAR_CODE),
            NameObject(Widths): ArrayObject(FloatObject(width) for width in widths)
        })

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


@lru_cache
def get_base_font_name(ttf_stream: bytes) -> str:
    """
    Extracts the base font name from a TrueType font stream.

    This function parses the TTF stream to extract the font's face name,
    which is used as the base font name. The result is cached using lru_cache
    for performance.

    Args:
        ttf_stream (bytes): The font file data in TTF format.

    Returns:
        str: The base font name, prefixed with a forward slash.
    """
    return (
        f"/{TTFont(name='new_font', filename=stream_to_io(ttf_stream)).face.name.ustr}"
    )


def get_new_font_name(fonts: dict) -> str:
    """
    Generates a new unique font name to avoid conflicts with existing fonts in the PDF.

    This function iterates through the existing fonts in the PDF and generates a new
    font name with the prefix '/F' followed by a unique integer.

    Args:
        fonts (dict): A dictionary of existing fonts in the PDF.

    Returns:
        str: A new unique font name.
    """
    existing = set()
    for key in fonts:
        if isinstance(key, str) and key.startswith(FONT_NAME_PREFIX):
            existing.add(int(key[2:]))

    n = 1
    while n in existing:
        n += 1
    return f"{FONT_NAME_PREFIX}{n}"


@lru_cache
def get_all_available_fonts(pdf: bytes) -> dict:
    """
    Retrieves all available fonts from a PDF document's AcroForm.

    This function extracts the font resources from the PDF's AcroForm dictionary
    and returns them as a dictionary.

    Args:
        pdf (bytes): The PDF file data.

    Returns:
        dict: A dictionary of available fonts, where the keys are the font names
            (without the leading slash) and the values are the corresponding font
            identifiers in the PDF. Returns an empty dictionary if no fonts are found.
    """
    reader = PdfReader(stream_to_io(pdf))
    try:
        fonts = reader.root_object[AcroForm][DR][Font]
    except KeyError:
        return {}

    result = {}
    for key, value in fonts.items():
        result[value[BaseFont].replace("/", "")] = key

    return result
