# -*- coding: utf-8 -*-


import os

import pytest
from typer.testing import CliRunner

from PyPDFForm.cli import cli_app

runner = CliRunner()


@pytest.mark.cli_test
def test_change_text_font(pdf_samples, static_pdfs, json_samples, data_dict, tmp_path):
    expected_path = os.path.join(pdf_samples, "docs", "test_change_text_font.pdf")
    output_path = os.path.join(tmp_path, "output.pdf")

    result = runner.invoke(
        cli_app,
        [
            "update",
            "field",
            os.path.join(static_pdfs, "sample_template.pdf"),
            "-f",
            os.path.join(json_samples, "test_change_text_font.json"),
            "-o",
            output_path,
        ],
    )
    assert result.exit_code == 0

    runner.invoke(
        cli_app,
        [
            "fill",
            output_path,
            "-f",
            os.path.join(json_samples, "test_fill_text_check.json"),
        ],
    )

    with open(expected_path, "rb") as f1, open(output_path, "rb") as f2:
        expected = f1.read()
        actual = f2.read()

        assert len(expected) == len(actual)
        assert expected == actual
