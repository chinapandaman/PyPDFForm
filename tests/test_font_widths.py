# -*- coding: utf-8 -*-

# https://github.com/chinapandaman/PyPDFForm/issues/1142
# https://github.com/chinapandaman/PyPDFForm/pull/1154

import os
from io import BytesIO
from unittest.mock import MagicMock, patch

import pytest
from fontTools.ttLib import TTLibError
from pypdf import PdfWriter

from PyPDFForm import PdfWrapper
from PyPDFForm.constants import (DEFAULT_ASSUMED_GLYPH_WIDTH, DR,
                                 ENCODING_TABLE_SIZE, AcroForm, Font,
                                 FontDescriptor, MissingWidth, Widths)
from PyPDFForm.font import compute_font_glyph_widths


@pytest.fixture
def pdf_font_widths_and_missing(static_pdfs, sample_font_stream):
    path = os.path.join(static_pdfs, "sample_template.pdf")
    obj = PdfWrapper(path, adobe_mode=True)
    obj.register_font("new_font_name", sample_font_stream)

    writer = PdfWriter(BytesIO(obj.read()))
    fonts = writer._root_object[AcroForm][DR][Font]  # type: ignore # noqa: SLF001
    font_obj = fonts[obj._available_fonts["new_font_name"]].get_object()  # type: ignore # noqa: SLF001

    pdf_widths_array = font_obj.get(Widths, [])
    descriptor_obj = font_obj[FontDescriptor].get_object()
    missing_width = descriptor_obj.get(MissingWidth, DEFAULT_ASSUMED_GLYPH_WIDTH)

    return pdf_widths_array, missing_width


def test_compute_font_glyph_widths_with_valid_font(sample_font_stream):
    missing_width = 500.0
    widths = compute_font_glyph_widths(BytesIO(sample_font_stream), missing_width)

    assert isinstance(widths, list)
    assert len(widths) == ENCODING_TABLE_SIZE
    assert all(isinstance(w, float) for w in widths)

    # with this font, not all widths should be equal to missing width
    assert any(w != missing_width for w in widths)


def test_compute_font_glyph_widths_with_default_missing_width(sample_font_stream):
    widths = compute_font_glyph_widths(
        BytesIO(sample_font_stream), DEFAULT_ASSUMED_GLYPH_WIDTH
    )

    assert isinstance(widths, list)
    assert len(widths) == ENCODING_TABLE_SIZE
    assert all(isinstance(w, float) for w in widths)

    # with this font, not all widths should be equal to missing width
    assert any(w != DEFAULT_ASSUMED_GLYPH_WIDTH for w in widths)


def test_compute_font_widths_raises_for_invalid_ttf():
    broken_stream = BytesIO(b"not a real font")
    with pytest.raises(TTLibError):
        compute_font_glyph_widths(
            broken_stream, missing_width=DEFAULT_ASSUMED_GLYPH_WIDTH
        )


def test_compute_font_glyph_widths_with_missing_tables():
    with patch("PyPDFForm.font.FT_TTFont") as mock_ttfont:
        mock_font = MagicMock()
        mock_font.get.side_effect = lambda table: None
        mock_ttfont.return_value = mock_font

        dummy_stream = BytesIO(b"anything")
        widths = compute_font_glyph_widths(dummy_stream, DEFAULT_ASSUMED_GLYPH_WIDTH)

    assert len(widths) == ENCODING_TABLE_SIZE
    assert all(w == DEFAULT_ASSUMED_GLYPH_WIDTH for w in widths)


def test_pdf_widths_array_has_256_entries(pdf_font_widths_and_missing):
    pdf_widths_array, _ = pdf_font_widths_and_missing
    assert len(pdf_widths_array) == ENCODING_TABLE_SIZE


def test_pdf_widths_match_computed_font_widths(
    pdf_font_widths_and_missing, sample_font_stream
):
    pdf_widths_array, missing_width = pdf_font_widths_and_missing
    computed_widths_array = compute_font_glyph_widths(
        BytesIO(sample_font_stream), missing_width
    )

    assert len(pdf_widths_array) == len(computed_widths_array)

    # Assume that rounding floats to 3 decimal is accurate for most cases
    assert all(
        round(pdf_width, 3) == round(computed_width, 3)
        for pdf_width, computed_width in zip(
            pdf_widths_array, computed_widths_array, strict=True
        )
    )


def test_pdf_widths_use_missing_width_for_unmapped_glyphs(pdf_font_widths_and_missing):
    pdf_widths_array, missing_width = pdf_font_widths_and_missing

    # Assume that rounding floats to 3 decimal is accurate for most cases
    assert round(missing_width, 3) == round(pdf_widths_array[128], 3)
    assert round(missing_width, 3) == round(pdf_widths_array[129], 3)
