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

from .constants import XFA, AcroForm, Root
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
