# -*- coding: utf-8 -*-

import os

from pypdf import PdfReader, PdfWriter
from typer.testing import CliRunner

from PyPDFForm.cli import cli_app
from PyPDFForm.lib.constants import AcroForm, Title

runner = CliRunner()


def test_change_title(static_pdfs, tmp_path):
    output_path = os.path.join(tmp_path, "output.pdf")
    result = runner.invoke(
        cli_app,
        [
            "update",
            "title",
            os.path.join(static_pdfs, "sample_template.pdf"),
            "-t",
            "My PDF",
            "-o",
            output_path,
        ],
    )
    assert result.exit_code == 0

    reader = PdfReader(output_path)
    assert (reader.metadata or {}).get(Title) == "My PDF"


def test_need_appearances_option(static_pdfs, tmp_path):
    output_path = os.path.join(tmp_path, "output.pdf")
    result = runner.invoke(
        cli_app,
        [
            "--need-appearances",
            "update",
            "title",
            os.path.join(static_pdfs, "sample_template.pdf"),
            "-t",
            "My PDF",
            "-o",
            output_path,
        ],
    )
    assert result.exit_code == 0

    reader = PdfReader(output_path)
    assert reader.root_object[AcroForm]["/NeedAppearances"]


def test_generate_appearance_streams_option(static_pdfs, tmp_path):
    output_path = os.path.join(tmp_path, "output.pdf")
    result = runner.invoke(
        cli_app,
        [
            "--generate-appearance-streams",
            "update",
            "title",
            os.path.join(static_pdfs, "sample_template.pdf"),
            "-t",
            "My PDF",
            "-o",
            output_path,
        ],
    )
    assert result.exit_code == 0

    reader = PdfReader(output_path)
    assert "/NeedAppearances" not in reader.root_object[AcroForm]


def test_preserve_metadata_option(static_pdfs, tmp_path):
    with_metadata = os.path.join(tmp_path, "metadata.pdf")
    output_path = os.path.join(tmp_path, "output.pdf")
    writer = PdfWriter(os.path.join(static_pdfs, "sample_template.pdf"))
    writer.add_metadata({"/foo": "bar"})
    writer.write(with_metadata)

    result = runner.invoke(
        cli_app,
        [
            "--preserve-metadata",
            "update",
            "title",
            with_metadata,
            "-t",
            "My PDF",
            "-o",
            output_path,
        ],
    )
    assert result.exit_code == 0

    reader = PdfReader(output_path)
    assert (reader.metadata or {}).get(Title) == "My PDF"
    assert (reader.metadata or {}).get("/foo") == "bar"


def test_use_full_widget_name_option(static_pdfs, tmp_path):
    output_path = os.path.join(tmp_path, "output.pdf")
    result = runner.invoke(
        cli_app,
        [
            "--use-full-widget-name",
            "update",
            "title",
            os.path.join(static_pdfs, "sample_template_with_full_key.pdf"),
            "-t",
            "My PDF",
            "-o",
            output_path,
        ],
    )
    assert result.exit_code == 0

    # TODO: finish this test
