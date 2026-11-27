# -*- coding: utf-8 -*-

import json
from io import BytesIO

import pytest
from pikepdf import Array, Pdf
from pypdf import PdfReader, PdfWriter
from pypdf.generic import (
    NameObject,
    NullObject,
    TextStringObject,
)
from typer.testing import CliRunner

from PyPDFForm import PdfWrapper
from PyPDFForm.cli.root import cli_app
from PyPDFForm.lib.constants import (
    DA,
    AcroForm,
    T,
)
from tests.support.builders import with_catalog_extras, without_default_appearance
from tests.support.checks import describe_catalog, without_duplicate_keys


@pytest.mark.cli_test
def test_cli_font_size_of_acroform_default_appearance(template_stream, tmp_path):
    # the field's /DA is the AcroForm default, which raised KeyError('/DA')
    writer = PdfWriter(BytesIO(template_stream))
    field = next(
        annot.get_object()
        for annot in writer.pages[0]["/Annots"]
        if annot.get_object().get(T) == "test"
    )
    writer.root_object[AcroForm][NameObject(DA)] = field[DA]
    del field[DA]
    path = tmp_path / "input.pdf"
    with open(path, "wb") as f:
        writer.write(f)

    result = CliRunner().invoke(
        cli_app, ["update", "field", str(path), "--field", "test", "--font_size", "14"]
    )

    assert result.exit_code == 0, result.output
    reader = PdfReader(path)
    widget = next(
        annot.get_object()
        for annot in reader.pages[0]["/Annots"]
        if annot.get_object().get(T) == "test"
    )
    assert widget[DA] == "/Arial 14 Tf 0 g"
    assert reader.root_object[AcroForm][DA] == "/Arial 0 Tf 0 g"


@pytest.mark.cli_test
def test_cli_font_size_without_default_appearance(template_stream, tmp_path):
    original = without_default_appearance(template_stream, "test")
    path = tmp_path / "input.pdf"
    path.write_bytes(original)

    result = CliRunner().invoke(
        cli_app, ["update", "field", str(path), "--field", "test", "--font_size", "14"]
    )

    assert result.exit_code == 1
    assert isinstance(result.exception, ValueError)
    assert path.read_bytes() == original


@pytest.mark.cli_test
@pytest.mark.parametrize("use_full_widget_name", [False, True])
def test_cli_fill_with_sample_of_field_without_name(
    template_stream, tmp_path, use_full_widget_name
):
    # "test" has a null name, so it has none, and "test_2" is named "null"
    writer = PdfWriter(BytesIO(template_stream))
    for page in writer.pages:
        for annot in page["/Annots"]:
            annot = annot.get_object()
            if annot.get(T) == "test":
                annot[NameObject(T)] = NullObject()
            elif annot.get(T) == "test_2":
                annot[NameObject(T)] = TextStringObject("null")
    path = tmp_path / "input.pdf"
    with open(path, "wb") as f:
        writer.write(f)
    options = ["--use-full-widget-name"] if use_full_widget_name else []
    runner = CliRunner()

    # without full names, JSON can't name the field, so it is left out; with
    # them, its key is ""
    expected = {"check", "null", "check_2", "test_3", "check_3"} | (
        {""} if use_full_widget_name else set()
    )
    for command in ("schema", "data", "sample"):
        result = runner.invoke(cli_app, [*options, "inspect", command, str(path)])
        assert result.exit_code == 0, result.output
        output = json.loads(result.output, object_pairs_hook=without_duplicate_keys)
        assert set(output["properties"] if command == "schema" else output) == expected

    sample = tmp_path / "sample.json"
    sample.write_text(result.output)
    output_path = tmp_path / "output.pdf"
    result = runner.invoke(
        cli_app,
        [*options, "fill", str(path), "-f", str(sample), "-o", str(output_path)],
    )

    assert result.exit_code == 0, result.output
    data = PdfWrapper(str(output_path), use_full_widget_name=use_full_widget_name).data
    assert data["null"] == "null"
    assert data["test_3"] == "test_3"


@pytest.mark.cli_test
def test_remove_fields_cli_without_widgets_on_pages(template_stream, tmp_path):
    source = tmp_path / "input.pdf"
    source.write_bytes(with_catalog_extras(template_stream))
    output = tmp_path / "output.pdf"

    result = CliRunner().invoke(
        cli_app,
        [
            "remove",
            "field",
            str(source),
            "--field",
            "hidden_business_id",
            "-o",
            str(output),
        ],
    )

    assert result.exit_code == 0
    fields = describe_catalog(output.read_bytes())["fields"]
    assert "hidden_business_id" not in fields
    assert "test" in fields

    result = CliRunner().invoke(
        cli_app,
        ["remove", "field", str(source), "--field", "missing_name", "-o", str(output)],
    )

    assert result.exit_code == 2
    assert "Form field 'missing_name' does not exist" in result.output


@pytest.mark.cli_test
def test_remove_fields_cli_widget_not_in_catalog(template_stream, tmp_path):
    # an unsupported widget on a page whose field isn't listed in /Fields
    with Pdf.open(BytesIO(with_catalog_extras(template_stream))) as pdf:
        pdf.Root.AcroForm.Fields = Array(
            [field for field in pdf.Root.AcroForm.Fields if field.T != "submit_button"]
        )
        source = tmp_path / "input.pdf"
        pdf.save(source)
    output = tmp_path / "output.pdf"

    result = CliRunner().invoke(
        cli_app,
        ["remove", "field", str(source), "--field", "submit_button", "-o", str(output)],
    )

    assert result.exit_code == 0
    with Pdf.open(output) as pdf:
        assert all(
            annot.get("/T") != "submit_button"
            for page in pdf.pages
            for annot in page.get("/Annots", [])
        )
