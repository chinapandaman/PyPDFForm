# -*- coding: utf-8 -*-

import os

from typer.testing import CliRunner

from PyPDFForm.cli import cli_app

runner = CliRunner()


def test_coordinate_grid_view(pdf_samples, static_pdfs, tmp_path):
    expected_path = os.path.join(pdf_samples, "docs", "test_coordinate_grid_view.pdf")
    output_path = os.path.join(tmp_path, "output.pdf")

    result = runner.invoke(
        cli_app,
        [
            "coordinate",
            "grid",
            os.path.join(static_pdfs, "sample_template.pdf"),
            "-r",
            "1",
            "-g",
            "0",
            "-b",
            "0",
            "-m",
            "100",
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
