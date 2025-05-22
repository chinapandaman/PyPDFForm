# -*- coding: utf-8 -*-

from functools import lru_cache
from io import BytesIO
from math import sqrt
from typing import Union

from pypdf import PdfReader, PdfWriter
from pypdf.generic import (ArrayObject, DictionaryObject, NameObject,
                           NumberObject, StreamObject)
from reportlab.pdfbase.pdfmetrics import registerFont
from reportlab.pdfbase.ttfonts import TTFError, TTFont

from .constants import (DR, FONT_NAME_PREFIX, AcroForm, BaseFont, Encoding,
                        Fields, Font, FontDescriptor, FontFile2, FontName,
                        Length1, Rect, Subtype, TrueType, Type,
                        WinAnsiEncoding)
from .utils import stream_to_io


def register_font(font_name: str, ttf_stream: bytes) -> bool:
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
    base_font_name = get_base_font_name(ttf_stream)
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


@lru_cache
def get_base_font_name(ttf_stream: bytes) -> str:
    return (
        f"/{TTFont(name='new_font', filename=stream_to_io(ttf_stream)).face.name.ustr}"
    )


def get_new_font_name(fonts: dict) -> str:
    existing = set()
    for key in fonts:
        if isinstance(key, str) and key.startswith(FONT_NAME_PREFIX):
            existing.add(int(key[2:]))

    n = 1
    while n in existing:
        n += 1
    return f"{FONT_NAME_PREFIX}{n}"


def get_all_available_fonts(pdf: bytes) -> dict:
    reader = PdfReader(stream_to_io(pdf))
    try:
        fonts = reader.root_object[AcroForm][DR][Font]
    except KeyError:
        return {}

    result = {}
    for key, value in fonts.items():
        result[value[BaseFont].replace("/", "")] = key

    return result


def checkbox_radio_font_size(widget: dict) -> Union[float, int]:
    area = abs(float(widget[Rect][0]) - float(widget[Rect][2])) * abs(
        float(widget[Rect][1]) - float(widget[Rect][3])
    )

    return sqrt(area) * 72 / 96
