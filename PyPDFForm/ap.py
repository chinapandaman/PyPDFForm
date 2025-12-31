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
from pypdf.generic import DictionaryObject, NameObject, TextStringObject

from .constants import JS, XFA, AcroForm, JavaScript, OpenAction, Root, S
from .utils import stream_to_io


def apply_js_patch(pdf: bytes, widgets: dict) -> bytes:
    """
    Applies a JavaScript patch to a PDF form to set field values upon opening.

    This function constructs a JavaScript snippet that sets the values of specific
    form fields using `this.getField().value`. This snippet is then embedded into
    the PDF as an /OpenAction, ensuring that these values are applied when the
    PDF is opened in a viewer.

    Args:
        pdf (bytes): The PDF file content as a bytes stream.
        widgets (dict): A dictionary of widget objects, where keys are field names.

    Returns:
        bytes: The modified PDF content with the JavaScript patch applied.
    """
    patches = []
    for k, v in widgets.items():
        if v.js_patch_value is not None:
            patches.append((k, v.js_patch_value))

    if not patches:
        return pdf

    reader = PdfReader(stream_to_io(pdf))
    writer = PdfWriter()
    writer.append(reader)

    js_code = ""
    for each in patches:
        js_code += f"this.getField('{each[0]}').value = '{each[1]}';"

    open_action = DictionaryObject()
    open_action[NameObject(S)] = NameObject(JavaScript)
    open_action[NameObject(JS)] = TextStringObject(js_code)

    writer._root_object.update({NameObject(OpenAction): open_action})  # type: ignore # noqa: SLF001 # # pylint: disable=W0212

    with BytesIO() as f:
        writer.write(f)
        f.seek(0)
        return f.read()


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
