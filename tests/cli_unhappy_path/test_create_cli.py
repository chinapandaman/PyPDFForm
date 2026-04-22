# -*- coding: utf-8 -*-

import os

import pytest
from typer.testing import CliRunner

from PyPDFForm.cli import cli_app

runner = CliRunner()


@pytest.mark.cli_test
def test_create_blank_missing_output():
    result = runner.invoke(cli_app, ["create", "blank"])

    assert result.exit_code == 2
    assert "Usage:" in result.output


@pytest.mark.parametrize(
    "args",
    [
        ["create", "blank", "-o", "output.pdf", "--count", "0"],
        ["create", "blank", "-o", "output.pdf", "--width", "-1"],
        ["create", "blank", "-o", "output.pdf", "--height", "-1"],
    ],
)
@pytest.mark.cli_test
def test_create_blank_invalid_ranges(args):
    result = runner.invoke(cli_app, args)

    assert result.exit_code == 2
    assert "is not in the range" in result.output


@pytest.mark.parametrize(
    "option",
    ["--start", "--end"],
)
@pytest.mark.cli_test
def test_create_extract_invalid_page_bounds(pdf_samples, tmp_path, option):
    output_path = os.path.join(tmp_path, "output.pdf")

    result = runner.invoke(
        cli_app,
        [
            "create",
            "extract",
            os.path.join(pdf_samples, "dummy.pdf"),
            "-o",
            output_path,
            option,
            "0",
        ],
    )

    assert result.exit_code == 2
    assert "is not in the range" in result.output


@pytest.mark.cli_test
def test_create_merge_nonexistent_pdf(tmp_path):
    output_path = os.path.join(tmp_path, "output.pdf")

    result = runner.invoke(
        cli_app,
        [
            "create",
            "merge",
            "missing.pdf",
            "-o",
            output_path,
        ],
    )

    assert result.exit_code == 2
    assert "does not exist" in result.output
    assert not os.path.exists(output_path)


@pytest.mark.parametrize(
    ("option", "value"),
    [
        ("--red", "2"),
        ("--green", "-1"),
        ("--blue", "2"),
        ("--margin", "-1"),
    ],
)
@pytest.mark.cli_test
def test_create_grid_invalid_ranges(pdf_samples, option, value):
    result = runner.invoke(
        cli_app,
        ["create", "grid", os.path.join(pdf_samples, "dummy.pdf"), option, value],
    )

    assert result.exit_code == 2
    assert "is not in the range" in result.output
