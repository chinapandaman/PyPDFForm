# -*- coding: utf-8 -*-

import json
import os

import pytest
from typer.testing import CliRunner

from PyPDFForm import PdfWrapper
from PyPDFForm.cli import cli_app

runner = CliRunner()


@pytest.mark.cli_test
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


@pytest.mark.cli_test
def test_field_coordinates_dimensions(static_pdfs):
    expected_path = os.path.join(static_pdfs, "sample_template.pdf")

    result = runner.invoke(
        cli_app,
        ["coordinate", "inspect", expected_path, "-f", "test"],
    )
    assert result.exit_code == 0

    wrapper = PdfWrapper(expected_path)
    obj = json.loads(result.output)
    assert obj["x"] == wrapper.widgets["test"].x
    assert obj["y"] == wrapper.widgets["test"].y
    assert obj["width"] == wrapper.widgets["test"].width
    assert obj["height"] == wrapper.widgets["test"].height


@pytest.mark.cli_test
def test_change_field_coordinates_dimensions(pdf_samples, static_pdfs, tmp_path):
    expected_path = os.path.join(
        pdf_samples, "docs", "test_change_field_coordinates_dimensions.pdf"
    )
    output_path = os.path.join(tmp_path, "output.pdf")

    result = runner.invoke(
        cli_app,
        [
            "coordinate",
            "modify",
            os.path.join(static_pdfs, "sample_template.pdf"),
            "-f",
            "test",
            "-o",
            output_path,
            "--x",
            "68.3365",
            "--y",
            "657.692",
            "--width",
            "242.4235",
            "--height",
            "31.067999999999984",
        ],
    )
    assert result.exit_code == 0

    with open(expected_path, "rb") as f1, open(output_path, "rb") as f2:
        expected = f1.read()
        output = f2.read()

        assert len(expected) == len(output)
        assert expected == output
