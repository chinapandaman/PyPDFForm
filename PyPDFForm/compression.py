# -*- coding: utf-8 -*-

from io import BytesIO
from zlib import compress

from pypdf import PageObject, PdfReader, PdfWriter
from pypdf.generic import NameObject, NumberObject, StreamObject

from .constants import Contents, Filter, FlateDecode, Length
from .utils import stream_to_io


def compress_page_content_stream(writer: PdfWriter, page: PageObject) -> None:
    content = page.get_contents()
    if not content:
        return

    compressed_data = compress(content.get_data())
    stream = StreamObject()
    stream.set_data(compressed_data)
    stream[NameObject(Filter)] = NameObject(FlateDecode)
    stream[NameObject(Length)] = NumberObject(len(compressed_data))
    page[NameObject(Contents)] = writer._add_object(stream)  # type: ignore # noqa: SLF001 # # pylint: disable=W0212


def compress_pdf(pdf: bytes) -> bytes:
    reader = PdfReader(stream_to_io(pdf))
    writer = PdfWriter()

    for page in reader.pages:
        compress_page_content_stream(writer, page)
        writer.add_page(page)

    with BytesIO() as f:
        writer.write(f)
        f.seek(0)

        return f.read()
