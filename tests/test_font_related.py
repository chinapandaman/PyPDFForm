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
from reportlab.pdfbase.pdfmetrics import _fonts
from reportlab.pdfbase.ttfonts import TTFError, TTFont

from PyPDFForm import PdfWrapper, RawElements
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
from PyPDFForm.lib.font import compute_font_glyph_widths, temporary_font_registration


@pytest.fixture
def font_registry():
    original = dict(_fonts)
    yield _fonts
    # Restore shared state even when a regression assertion fails.
    _fonts.clear()
    _fonts.update(original)


def test_temporary_font_registration_cleans_up_setup_failure(
    sample_font_stream, font_registry
):
    original = dict(font_registry)
    fonts = [("same", sample_font_stream)] * 2 + [("bad", b"invalid font")]
    with pytest.raises(TTFError), temporary_font_registration(fonts):
        pytest.fail("Invalid font setup must fail before entering the context")

    assert font_registry == original


def test_temporary_font_registration_preserves_other_registrations_on_failure(
    sample_font_stream, font_registry
):
    original = dict(font_registry)
    error = RuntimeError("drawing failed")
    external = TTFont("external", BytesIO(sample_font_stream))

    def fail_drawing():
        font_registry["external"] = external
        raise error

    with temporary_font_registration([("same", sample_font_stream)]):
        outer_state = dict(font_registry)
        with (
            pytest.raises(RuntimeError, match="drawing failed") as caught,
            temporary_font_registration([("same", sample_font_stream)] * 2),
        ):
            fail_drawing()

        assert caught.value is error
        assert font_registry == {**outer_state, "external": external}

    assert font_registry == {**original, "external": external}


def test_temporary_font_registration_only_removes_owned_entries(
    sample_font_stream, font_registry
):
    existing = TTFont("existing", BytesIO(sample_font_stream))
    font_registry["existing"] = existing
    original = dict(font_registry)
    with patch("PyPDFForm.lib.font.uuid4") as uuid:
        uuid.side_effect = [MagicMock(hex="existing"), MagicMock(hex="temporary")]
        with temporary_font_registration([("same", sample_font_stream)]) as mapping:
            assert mapping == {"same": "temporary"}
            assert font_registry["existing"] is existing
            font_registry[mapping["same"]] = existing

    assert font_registry == {**original, "temporary": existing}


@pytest.mark.parametrize("need_appearances", [False, True])
def test_repeated_draws_with_duplicate_font_aliases(
    template_stream, sample_font_stream, font_samples, font_registry, need_appearances
):
    # Initialize ReportLab's lazily loaded built-in fonts before taking a snapshot.
    PdfWrapper(template_stream).draw([RawElements.RawText("Warm up", 1, 100, 100)])
    form = PdfWrapper(template_stream, need_appearances=need_appearances)
    form.register_font("same", os.path.join(font_samples, "LiberationSerif-Italic.ttf"))
    form.register_font("same", sample_font_stream)
    original = dict(font_registry)
    original_fields = set(form.widgets)

    for index in range(3):
        text = f"Font lifecycle {index}"
        form.draw([RawElements.RawText(text, 1, 100, 100 + index * 25, font="same")])
        stream = form.read()
        assert font_registry == original

        reopened = PdfWrapper(stream)
        assert set(reopened.widgets) == original_fields
        assert "LiberationSerif-BoldItalic" in reopened.fonts
        page = PdfReader(BytesIO(stream)).pages[0]
        assert text in page.extract_text()
        assert any(
            font["/BaseFont"].endswith("LiberationSerif-BoldItalic")
            and font["/FontDescriptor"]["/FontFile2"].get_data()
            for font in (
                ref.get_object() for ref in page["/Resources"]["/Font"].values()
            )
        )


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
