# -*- coding: utf-8 -*-

import os

import pytest
from typer.testing import CliRunner

from PyPDFForm.cli.root import cli_app

runner = CliRunner()


@pytest.mark.cli_test
def test_root_command_no_arg_help():
    result = runner.invoke(cli_app)
    assert result.exit_code == 2

    assert "Create, fill, inspect, and update PDF forms." in result.output
    assert "Usage:" in result.output
    assert "main" not in result.output


@pytest.mark.cli_test
def test_fill_nonexistent_input_pdf(json_samples):
    result = runner.invoke(
        cli_app,
        [
            "fill",
            "missing.pdf",
            "-f",
            os.path.join(json_samples, "test_fill_text_check.json"),
        ],
    )

    assert result.exit_code == 2
    assert "does not exist" in result.output


@pytest.mark.cli_test
def test_fill_wrong_known_field_type(pdf_samples, tmp_path):
    data_path = os.path.join(tmp_path, "invalid.json")
    output_path = os.path.join(tmp_path, "output.pdf")
    with open(data_path, "w", encoding="utf-8") as f:
        f.write('{"check": "yes"}')

    result = runner.invoke(
        cli_app,
        [
            "fill",
            os.path.join(pdf_samples, "sample_template.pdf"),
            "-f",
            data_path,
            "-o",
            output_path,
        ],
    )

    assert result.exit_code == 2
    assert "Invalid JSON file at check" in result.output
    assert not os.path.exists(output_path)
