# -*- coding: utf-8 -*-

# https://github.com/chinapandaman/PyPDFForm/issues/1142
# https://github.com/chinapandaman/PyPDFForm/pull/1154

import math
import os
from io import BytesIO
from unittest.mock import MagicMock, patch

import pytest
from fontTools.ttLib import TTLibError
from pypdf import PdfReader, PdfWriter
from pypdf.generic import NameObject

from PyPDFForm import PdfWrapper
from PyPDFForm.lib.constants import (
    DEFAULT_ASSUMED_GLYPH_WIDTH,
    DR,
    ENCODING_TABLE_SIZE,
    AcroForm,
    Font,
    FontDescriptor,
    MissingWidth,
    Widths,
)
from PyPDFForm.lib.font import compute_font_glyph_widths


@pytest.fixture
def pdf_font_widths_and_missing(static_pdfs, sample_font_stream):
    path = os.path.join(static_pdfs, "sample_template.pdf")
    obj = PdfWrapper(path, need_appearances=True)
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
    assert any(
        not math.isclose(w, missing_width, rel_tol=1e-09, abs_tol=1e-09) for w in widths
    )


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
    with patch("PyPDFForm.lib.font.FT_TTFont") as mock_ttfont:
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


@pytest.mark.parametrize("need_appearances", [False, True])
@pytest.mark.parametrize(
    ("resource_names", "expected_name"),
    [
        pytest.param([], "/F1", id="no-numbered-resources"),
        pytest.param(["/F1", "/F2"], "/F3", id="consecutive-resources"),
        pytest.param(["/F9"], "/F1", id="unused-first-number"),
        pytest.param(
            ["/FontA", "/FCustom", "/F1", "/F9", "/Other"],
            "/F2",
            id="arbitrary-and-sparse-resources",
        ),
        pytest.param(["/F01", "/F9"], "/F2", id="leading-zero-resource"),
        pytest.param(
            ["/F", "/F+1", "/F-1", "/F 1", "/F1.5", "/F1tail", "/F1\n"],
            "/F1",
            id="non-numeric-suffixes",
        ),
        pytest.param(["/F\u0661", "/F\u00b2"], "/F1", id="non-ascii-digits"),
    ],
)
def test_register_font_preserves_resource_names(
    template_stream, sample_font_stream, need_appearances, resource_names, expected_name
):
    writer = PdfWriter(BytesIO(template_stream))
    fonts = writer.root_object["/AcroForm"]["/DR"]["/Font"]
    original_font = next(iter(fonts.values()))
    for name in resource_names:
        fonts[NameObject(name)] = original_font
    original_fonts = {
        name: (font["/Type"], font["/Subtype"], font["/BaseFont"])
        for name, font in fonts.items()
    }
    with BytesIO() as stream:
        writer.write(stream)
        form = PdfWrapper(stream.getvalue(), need_appearances=need_appearances)

    form.register_font("new_font", sample_font_stream)
    registered_stream = form.read()
    registered = PdfReader(BytesIO(registered_stream))
    registered_fonts = registered.root_object["/AcroForm"]["/DR"]["/Font"]
    assert set(registered_fonts) == set(original_fonts) | {expected_name}
    assert expected_name not in original_fonts
    for name, definition in original_fonts.items():
        font = registered_fonts[name]
        assert (font["/Type"], font["/Subtype"], font["/BaseFont"]) == definition

    new_font = registered_fonts[expected_name]
    assert new_font["/Type"] == "/Font"
    assert new_font["/Subtype"] == "/TrueType"
    assert new_font["/FontDescriptor"]["/FontFile2"].get_data() == sample_font_stream

    reopened = PdfWrapper(registered_stream, generate_appearance_streams=True)
    font_name = new_font["/BaseFont"][1:]
    assert font_name in reopened.fonts
    reopened.widgets["test"].font = font_name
    reopened.fill({"test": "Font regression"})
    filled_stream = reopened.read()
    assert PdfWrapper(filled_stream).widgets["test"].value == "Font regression"

    filled = PdfReader(BytesIO(filled_stream))
    filled_fonts = filled.root_object["/AcroForm"]["/DR"]["/Font"]
    assert set(filled_fonts) == set(registered_fonts)
    for name, definition in original_fonts.items():
        font = filled_fonts[name]
        assert (font["/Type"], font["/Subtype"], font["/BaseFont"]) == definition

    annotation = next(
        annot.get_object()
        for annot in filled.pages[0]["/Annots"]
        if annot.get_object().get("/T") == "test"
    )
    assert annotation["/DA"].split()[0] == expected_name
    appearance = annotation["/AP"]["/N"]
    assert f"{expected_name} ".encode() in appearance.get_data()
    assert b"(Font regression) Tj" in appearance.get_data()
    appearance_font = appearance["/Resources"]["/Font"][expected_name]
    assert appearance_font["/BaseFont"] == new_font["/BaseFont"]
    assert (
        appearance_font["/FontDescriptor"]["/FontFile2"].get_data()
        == sample_font_stream
    )
