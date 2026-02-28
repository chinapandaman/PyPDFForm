# -*- coding: utf-8 -*-
"""
A module for egress functions.

This module provides functionalities that prepare the final PDF for output (egress),
ensuring that it is properly formatted and ready for the end-user. This includes
managing appearance streams (so form fields display correctly after being filled),
handling the /NeedAppearances flag, and preserving or updating document-level
properties like the title and OpenAction scripts. These functions are typically
called right before the final PDF byte stream is returned by the wrapper module.
"""

from functools import lru_cache
from io import BytesIO

from pikepdf import Pdf
from pypdf import PdfReader, PdfWriter
from pypdf.generic import DictionaryObject, NameObject, TextStringObject

from .constants import (JS, XFA, AcroForm, JavaScript, OpenAction, Root, S,
                        Title)
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


def preserve_pdf_properties(
    pdf: bytes, title: str, script: str, metadata: dict = None
) -> bytes:
    """
    Preserves and updates PDF properties such as title and OpenAction scripts.

    This function allows setting or updating the PDF's title in its metadata and
    attaching a JavaScript script that executes when the PDF is opened.

    Args:
        pdf (bytes): The PDF file content as a bytes stream.
        title (str): The title to be set in the PDF metadata.
        script (str): JavaScript code to be executed when the PDF is opened.
        metadata (dict): The original metadata to preserve.

    Returns:
        bytes: The modified PDF content as a bytes stream.
    """
    reader = PdfReader(stream_to_io(pdf))
    writer = PdfWriter()
    writer.append(reader)

    if title or metadata:
        _metadata = reader.metadata or {}
        if metadata:
            _metadata.update(metadata)
        if title:
            _metadata[NameObject(Title)] = TextStringObject(title)

        writer.add_metadata(_metadata)

    if script:
        open_action = DictionaryObject()
        open_action[NameObject(S)] = NameObject(JavaScript)
        open_action[NameObject(JS)] = TextStringObject(script)

        writer._root_object.update({NameObject(OpenAction): open_action})  # type: ignore # noqa: SLF001 # # pylint: disable=W0212

    with BytesIO() as f:
        writer.write(f)
        f.seek(0)
        return f.read()
