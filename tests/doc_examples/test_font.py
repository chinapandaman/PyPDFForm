# -*- coding: utf-8 -*-

from io import BytesIO
import os
import pytest
from PyPDFForm import PdfWrapper
from PyPDFForm.font import compute_font_glyph_widths
from PyPDFForm.constants import DEFAULT_ASSUMED_GLYPH_WIDTH, ENCODING_TABLE_SIZE
from fontTools.ttLib import TTLibError

def test_register_font(static_pdfs, sample_font_stream):
    obj = PdfWrapper(os.path.join(static_pdfs, "sample_template.pdf"))
    obj.register_font("new_font_name", sample_font_stream)

    assert "new_font_name" in obj.fonts

def test_compute_font_glyph_widths_with_valid_font(sample_font_stream):
    missing_width = 500.0
    widths = compute_font_glyph_widths(BytesIO(sample_font_stream), missing_width)

    assert isinstance(widths, list)
    assert len(widths) == ENCODING_TABLE_SIZE
    assert all(isinstance(w, float) for w in widths)

    # with this font, not all widths should be equal to missing width
    assert any(w != missing_width for w in widths)

def test_compute_font_glyph_widths_with_default_missing_width(sample_font_stream):
    widths = compute_font_glyph_widths(BytesIO(sample_font_stream), DEFAULT_ASSUMED_GLYPH_WIDTH)

    assert isinstance(widths, list)
    assert len(widths) == ENCODING_TABLE_SIZE
    assert all(isinstance(w, float) for w in widths)

    # with this font, not all widths should be equal to missing width
    assert any(w != DEFAULT_ASSUMED_GLYPH_WIDTH for w in widths)

def test_compute_font_widths_raises_for_invalid_ttf():
    broken_stream = BytesIO(b"not a real font")
    with pytest.raises(TTLibError):
        compute_font_glyph_widths(broken_stream, missing_width=DEFAULT_ASSUMED_GLYPH_WIDTH)

def test_pdf_widths_array_has_256_entries(pdf_font_widths_and_missing):
    pdf_widths_array, _ = pdf_font_widths_and_missing
    assert len(pdf_widths_array) == ENCODING_TABLE_SIZE

def test_pdf_widths_match_computed_font_widths(pdf_font_widths_and_missing, sample_font_stream):
    pdf_widths_array, missing_width = pdf_font_widths_and_missing
    computed_widths_array = compute_font_glyph_widths(BytesIO(sample_font_stream), missing_width)
    
    assert len(pdf_widths_array) == len(computed_widths_array)
    
    # Assume that rounding floats to 3 decimal is accurate for most cases
    assert all(round(pdf_width, 3) == round(computed_width, 3) for pdf_width, computed_width in zip(pdf_widths_array, computed_widths_array))
    
def test_pdf_widths_use_missing_width_for_unmapped_glyphs(pdf_font_widths_and_missing):
    pdf_widths_array, missing_width = pdf_font_widths_and_missing

    assert round(missing_width, 3) == round(pdf_widths_array[128], 3)
    assert round(missing_width, 3) == round(pdf_widths_array[129], 3)