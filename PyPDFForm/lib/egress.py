# -*- coding: utf-8 -*-
"""
A module for egress functions.

This module provides functionalities that prepare the final PDF for output (egress),
ensuring that it is properly formatted and ready for the end-user. This includes
managing appearance streams (so form fields display correctly after being filled),
handling the /NeedAppearances flag, and preserving or updating document-level
properties like metadata, title, and OpenAction scripts. It can also rebuild the
AcroForm `/Fields` array from the widget annotations present on each page. These
functions are typically called right before the final PDF byte stream is returned by
the wrapper module.
"""

from functools import lru_cache
from io import BytesIO
from warnings import catch_warnings, filterwarnings

from pikepdf import Pdf
from pypdf import PdfReader, PdfWriter
from pypdf.generic import ArrayObject, DictionaryObject, NameObject, TextStringObject

from .constants import (
    JS,
    XFA,
    AcroForm,
    Annots,
    Fields,
    JavaScript,
    OpenAction,
    Root,
    S,
    Title,
)
from .template import get_widget_key


@lru_cache(maxsize=128)
def appearance_streams_handler(pdf: bytes, generate_appearance_streams: bool) -> bytes:
    """
    Handles appearance streams and the /NeedAppearances flag for a PDF form.

    This function prepares a PDF for output by:
    1. Removing the XFA dictionary if present, as it can interfere with standard
       AcroForm processing.
    2. Setting the /NeedAppearances flag in the AcroForm dictionary, which asks
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
    reader = PdfReader(BytesIO(pdf))
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
        with Pdf.open(BytesIO(result)) as f, catch_warnings():
            filterwarnings(
                "ignore", message=".*/AcroForm.*"
            )  # handled by rebuild_acroform_fields

            f.generate_appearance_streams()
            with BytesIO() as r:
                f.save(r, deterministic_id=True)
                r.seek(0)
                result = r.read()

    return result


def preserve_pdf_properties(
    pdf: bytes, title: str, script: str, metadata: dict
) -> bytes:
    """
    Preserves and updates PDF properties such as metadata, title, and OpenAction scripts.

    This function allows setting or updating the PDF's title and metadata, and
    attaching a JavaScript script that executes when the PDF is opened. Metadata
    is merged into the reader's current metadata when provided; the title and
    OpenAction JavaScript are written only when non-empty values are supplied.

    Args:
        pdf (bytes): The PDF file content as a bytes stream.
        title (str): The title to be set in the PDF metadata.
        script (str): JavaScript code to be executed when the PDF is opened.
        metadata (dict): The original metadata to preserve.

    Returns:
        bytes: The modified PDF content as a bytes stream.
    """
    reader = PdfReader(BytesIO(pdf))
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


def rebuild_acroform_fields(
    pdf: bytes, widget_keys: set, use_full_widget_name: bool
) -> bytes:
    """
    Rebuilds the AcroForm `/Fields` array from matching page annotations.

    The existing `/Fields` array is replaced, creating an AcroForm dictionary
    when necessary. Each page annotation is resolved to a widget key, and only
    annotations whose keys are present in `widget_keys` are added to the new
    array. Page annotation arrays are left unchanged.

    Args:
        pdf (bytes): The PDF stream whose AcroForm fields should be rebuilt.
        widget_keys (set): Widget keys to include in the rebuilt `/Fields` array.
        use_full_widget_name (bool): Whether to resolve annotations using their
            full widget names, including parent names.

    Returns:
        bytes: The PDF stream with a rebuilt AcroForm `/Fields` array.
    """
    writer = PdfWriter(BytesIO(pdf))
    root = writer._root_object  # type: ignore # noqa: SLF001 # # pylint: disable=W0212

    if AcroForm not in root:
        root[NameObject(AcroForm)] = DictionaryObject({})
    root[AcroForm][NameObject(Fields)] = ArrayObject([])

    for page in writer.pages:
        for annot in page.get(Annots, []):
            key = get_widget_key(annot.get_object(), use_full_widget_name)
            if key in widget_keys:
                root[AcroForm][Fields].append(annot)

    with BytesIO() as f:
        writer.write(f)
        f.seek(0)
        return f.read()
