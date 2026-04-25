# -*- coding: utf-8 -*-

import os

import pytest
from pypdf import PdfReader, PdfWriter
from typer.testing import CliRunner

from PyPDFForm import __version__
from PyPDFForm.cli.root import cli_app
from PyPDFForm.lib.constants import AcroForm, Title

runner = CliRunner()


@pytest.mark.cli_test
def test_get_version():
    long = runner.invoke(cli_app, ["--version"])
    short = runner.invoke(cli_app, ["-v"])

    assert long.exit_code == 0
    assert short.exit_code == 0

    assert long.output == f"v{__version__}\n"
    assert long.output == short.output


@pytest.mark.cli_test
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


@pytest.mark.cli_test
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


@pytest.mark.cli_test
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


@pytest.mark.cli_test
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


@pytest.mark.cli_test
def test_use_full_widget_name_option(static_pdfs):
    result = runner.invoke(
        cli_app,
        [
            "--use-full-widget-name",
            "inspect",
            "location",
            os.path.join(static_pdfs, "sample_template_with_full_key.pdf"),
            "--field",
            "Gain de 2 classes.0",
        ],
    )
    assert result.exit_code == 0
