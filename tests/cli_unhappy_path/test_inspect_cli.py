# -*- coding: utf-8 -*-

import os

import pytest
from typer.testing import CliRunner

from PyPDFForm.cli.root import cli_app

runner = CliRunner()


@pytest.mark.cli_test
def test_inspect_missing_pdf_path():
    result = runner.invoke(cli_app, ["inspect", "schema"])

    assert result.exit_code == 2
    assert "Usage:" in result.output
    assert "PDF" in result.output


@pytest.mark.cli_test
def test_inspect_nonexistent_pdf():
    result = runner.invoke(cli_app, ["inspect", "schema", "missing.pdf"])

    assert result.exit_code == 2
    assert "does not exist" in result.output


@pytest.mark.cli_test
def test_inspect_location_missing_field(pdf_samples):
    result = runner.invoke(
        cli_app,
        ["inspect", "location", os.path.join(pdf_samples, "sample_template.pdf")],
    )

    assert result.exit_code == 2
    assert "Missing option" in result.output


@pytest.mark.cli_test
def test_inspect_location_unknown_field(pdf_samples):
    result = runner.invoke(
        cli_app,
        [
            "inspect",
            "location",
            os.path.join(pdf_samples, "sample_template.pdf"),
            "--field",
            "missing_name",
        ],
    )

    assert result.exit_code == 2
    assert "Form field 'missing_name' does not exist" in result.output
