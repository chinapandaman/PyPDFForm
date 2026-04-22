# -*- coding: utf-8 -*-

import os

import pytest
from typer.testing import CliRunner

from PyPDFForm.cli import cli_app

runner = CliRunner()


@pytest.mark.cli_test
def test_update_title_missing_title(pdf_samples):
    result = runner.invoke(
        cli_app,
        ["update", "title", os.path.join(pdf_samples, "sample_template.pdf")],
    )

    assert result.exit_code == 2
    assert "Missing option" in result.output
    assert "--title" in result.output


@pytest.mark.cli_test
def test_update_version_invalid_version(pdf_samples):
    result = runner.invoke(
        cli_app,
        [
            "update",
            "version",
            os.path.join(pdf_samples, "dummy.pdf"),
            "--version",
            "3.0",
        ],
    )

    assert result.exit_code == 2
    assert "is not one of" in result.output


@pytest.mark.cli_test
def test_update_bounds_missing_field(pdf_samples):
    result = runner.invoke(
        cli_app,
        [
            "update",
            "bounds",
            os.path.join(pdf_samples, "sample_template.pdf"),
            "--x",
            "1",
        ],
    )

    assert result.exit_code == 2
    assert "Missing option" in result.output
    assert "--field" in result.output


@pytest.mark.parametrize("option", ["--width", "--height"])
@pytest.mark.cli_test
def test_update_bounds_invalid_size(pdf_samples, option):
    result = runner.invoke(
        cli_app,
        [
            "update",
            "bounds",
            os.path.join(pdf_samples, "sample_template.pdf"),
            "--field",
            "test",
            option,
            "-1",
        ],
    )

    assert result.exit_code == 2
    assert "is not in the range" in result.output


@pytest.mark.cli_test
def test_update_bounds_unknown_field(pdf_samples, tmp_path):
    output_path = tmp_path / "output.pdf"
    result = runner.invoke(
        cli_app,
        [
            "update",
            "bounds",
            os.path.join(pdf_samples, "sample_template.pdf"),
            "--field",
            "missing_name",
            "--x",
            "1",
            "-o",
            str(output_path),
        ],
    )

    assert result.exit_code == 2
    assert "Form field 'missing_name' does not exist" in result.output
    assert not output_path.exists()


@pytest.mark.cli_test
def test_update_script_missing_script(pdf_samples):
    result = runner.invoke(
        cli_app,
        ["update", "script", os.path.join(pdf_samples, "sample_template.pdf")],
    )

    assert result.exit_code == 2
    assert "Missing option" in result.output
    assert "--script" in result.output


@pytest.mark.cli_test
def test_update_script_nonexistent_script(pdf_samples):
    result = runner.invoke(
        cli_app,
        [
            "update",
            "script",
            os.path.join(pdf_samples, "sample_template.pdf"),
            "--script",
            "missing.js",
        ],
    )

    assert result.exit_code == 2
    assert "does not exist" in result.output


@pytest.mark.cli_test
def test_update_script_invalid_event(pdf_samples, js_samples):
    result = runner.invoke(
        cli_app,
        [
            "update",
            "script",
            os.path.join(pdf_samples, "sample_template.pdf"),
            "--script",
            os.path.join(js_samples, "test_file_path_scripts.js"),
            "--event",
            "close",
        ],
    )

    assert result.exit_code == 2
    assert "is not 'open'" in result.output
