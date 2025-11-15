# -*- coding: utf-8 -*-
"""
A module for handling PDF appearance streams.

This module provides functionality to manage appearance streams in PDF forms,
which are necessary for form fields to display correctly after being filled.
It uses both pypdf and pikepdf for manipulation.
"""

from functools import lru_cache
from io import BytesIO

from pikepdf import Pdf
from pypdf import PdfReader, PdfWriter
from pypdf.generic import DictionaryObject
from reportlab.pdfbase.pdfmetrics import getFont

from .constants import (AP, DEFAULT_FONT, FONT_SIZE_IDENTIFIER, XFA, AcroForm,
                        Annots, BBox, N, Root, Td)
from .middleware.text import Text
from .template import get_widget_key
from .utils import stream_to_io


@lru_cache
def appearance_streams_handler(pdf: bytes, generate_appearance_streams: bool) -> bytes:
    """
    Handles appearance streams and the /NeedAppearances flag for a PDF form.

    This function prepares a PDF for form filling by:
    1. Removing the XFA dictionary if present, as it can interfere with standard
       AcroForm processing.
    2. Setting the /NeedAppearances flag in the AcroForm dictionary, which instructs
       PDF viewers to generate appearance streams for form fields.
    3. Optionally generating appearance streams explicitly using pikepdf if
       `generate_appearance_streams` is True.

    The result is cached using lru_cache for performance.

    Args:
        pdf (bytes): The PDF file content as a bytes stream.
        generate_appearance_streams (bool): Whether to explicitly generate appearance streams for all form fields.

    Returns:
        bytes: The modified PDF content as a bytes stream.
    """
    reader = PdfReader(stream_to_io(pdf))
    writer = PdfWriter()

    if AcroForm in reader.trailer[Root] and XFA in reader.trailer[Root][AcroForm]:
        del reader.trailer[Root][AcroForm][XFA]

    writer.append(reader)
    writer.set_need_appearances_writer()

    with BytesIO() as f:
        writer.write(f)
        f.seek(0)
        result = f.read()

    if generate_appearance_streams:
        with Pdf.open(stream_to_io(result)) as f:
            f.generate_appearance_streams()
            with BytesIO() as r:
                f.save(r)
                r.seek(0)
                result = r.read()

    return result


def appearance_streams_post_processing(
    pdf: bytes, widgets: dict, use_full_widget_name: bool, available_fonts: dict
) -> bytes:
    reader = PdfReader(stream_to_io(pdf))
    writer = PdfWriter()
    writer.append(reader)

    needs_update = False
    for page in writer.pages:
        for annot in page.get(Annots, []):
            key = get_widget_key(annot, use_full_widget_name)
            widget = widgets[key]

            try:
                needs_update = (
                    needs_update
                    or ap_processing_reportlab_text_field_alignment(
                        annot, widget, available_fonts
                    )
                )
            except Exception:
                pass

    if not needs_update:
        return pdf

    with BytesIO() as f:
        writer.write(f)
        f.seek(0)
        return f.read()


def ap_processing_reportlab_text_field_alignment(
    annot: DictionaryObject, widget: Text, available_fonts: dict
) -> bool:
    if (not widget.alignment) or (not widget.value):
        return False

    ap_stream = annot[AP][N].get_data()
    bbox = annot[AP][N][BBox]

    # calculate width
    font_size = float(
        ap_stream.split(bytes(" " + FONT_SIZE_IDENTIFIER, encoding="utf-8"))[0].split(
            b" "
        )[-1]
    )
    if widget.font:
        width = None
        for k, v in available_fonts.items():
            if v == widget.font:
                width = getFont(k).stringWidth(widget.value, font_size)
                break
    else:
        width = getFont(DEFAULT_FONT).stringWidth(widget.value, font_size)

    # new alignment coordinate stream
    alignment_coord = b" ".join(
        ap_stream.split(b" " + Td)[0].split(b" ")[-2:] + [Td]
    ).split(b"\n")[1]
    new_x_coord = (
        bbox[2] - bbox[1] - width - float(alignment_coord.split(b" ")[0])
        if widget.alignment == 2
        else (bbox[2] - bbox[1] - width) / 2
    )
    new_alignment_coord = b" ".join(
        [
            bytes(str(new_x_coord), encoding="utf-8"),
        ]
        + alignment_coord.split(b" ")[1:]
    )

    annot[AP][N].set_data(ap_stream.replace(alignment_coord, new_alignment_coord))

    return True
