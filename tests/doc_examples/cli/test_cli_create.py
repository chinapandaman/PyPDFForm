# -*- coding: utf-8 -*-

import os

import pytest
from typer.testing import CliRunner

from PyPDFForm.cli import cli_app

runner = CliRunner()


@pytest.mark.cli_test
def test_bulk_create_fields(pdf_samples, json_samples, tmp_path):
    expected_path = os.path.join(pdf_samples, "docs", "test_bulk_create_fields.pdf")
    output_path = os.path.join(tmp_path, "output.pdf")

    result = runner.invoke(
        cli_app,
        [
            "create",
            "field",
            os.path.join(pdf_samples, "dummy.pdf"),
            "-f",
            os.path.join(json_samples, "test_bulk_create_fields.json"),
            "-o",
            output_path,
        ],
    )
    assert result.exit_code == 0

    with open(expected_path, "rb") as f1, open(output_path, "rb") as f2:
        expected = f1.read()
        actual = f2.read()

        assert len(expected) == len(actual)
        assert expected == actual


@pytest.mark.cli_test
def test_create_text(pdf_samples, json_samples, tmp_path):
    expected_path = os.path.join(pdf_samples, "docs", "test_create_text.pdf")
    output_path = os.path.join(tmp_path, "output.pdf")

    result = runner.invoke(
        cli_app,
        [
            "create",
            "field",
            os.path.join(pdf_samples, "dummy.pdf"),
            "-f",
            os.path.join(json_samples, "test_create_text.json"),
            "-o",
            output_path,
        ],
    )
    assert result.exit_code == 0

    with open(expected_path, "rb") as f1, open(output_path, "rb") as f2:
        expected = f1.read()
        actual = f2.read()

        assert len(expected) == len(actual)
        assert expected == actual
