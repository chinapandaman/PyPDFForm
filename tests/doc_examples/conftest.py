import io
import os

from pypdf import PdfWriter
import pytest
from PyPDFForm import PdfWrapper
from PyPDFForm.constants import DEFAULT_ASSUMED_GLYPH_WIDTH

@pytest.fixture
def pdf_font_widths_and_missing(static_pdfs, sample_font_stream):
    path = os.path.join(static_pdfs, "sample_template.pdf")
    obj = PdfWrapper(path, adobe_mode=True)
    obj.register_font("new_font_name", sample_font_stream)

    writer = PdfWriter(io.BytesIO(obj.read()))
    fonts = writer._root_object["/AcroForm"]["/DR"]["/Font"]  # type: ignore
    font_obj = fonts[obj._available_fonts["new_font_name"]].get_object()  # type: ignore

    pdf_widths_array = font_obj.get("/Widths", [])
    descriptor_obj = font_obj["/FontDescriptor"].get_object()
    missing_width = descriptor_obj.get("/MissingWidth", DEFAULT_ASSUMED_GLYPH_WIDTH)

    return pdf_widths_array, missing_width
