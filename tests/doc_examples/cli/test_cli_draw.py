# -*- coding: utf-8 -*-


import os

import pytest
from typer.testing import CliRunner

from PyPDFForm.cli import cli_app

runner = CliRunner()


@pytest.mark.cli_test
def test_draw_text(pdf_samples, static_pdfs, json_samples, tmp_path):
    expected_path = os.path.join(pdf_samples, "docs", "test_draw_text.pdf")
    output_path = os.path.join(tmp_path, "output.pdf")

    result = runner.invoke(
        cli_app,
        [
            "create",
            "raw",
            os.path.join(static_pdfs, "sample_template.pdf"),
            "-f",
            os.path.join(json_samples, "test_draw_text.json"),
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
def test_draw_image(pdf_samples, static_pdfs, json_samples, tmp_path):
    expected_path = os.path.join(pdf_samples, "docs", "test_draw_image.pdf")
    output_path = os.path.join(tmp_path, "output.pdf")

    result = runner.invoke(
        cli_app,
        [
            "create",
            "raw",
            os.path.join(static_pdfs, "sample_template.pdf"),
            "-f",
            os.path.join(json_samples, "test_draw_image.json"),
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
def test_draw_line(pdf_samples, static_pdfs, json_samples, tmp_path):
    expected_path = os.path.join(pdf_samples, "docs", "test_draw_line.pdf")
    output_path = os.path.join(tmp_path, "output.pdf")

    result = runner.invoke(
        cli_app,
        [
            "create",
            "raw",
            os.path.join(static_pdfs, "sample_template.pdf"),
            "-f",
            os.path.join(json_samples, "test_draw_line.json"),
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
def test_draw_rect(pdf_samples, static_pdfs, json_samples, tmp_path):
    expected_path = os.path.join(pdf_samples, "docs", "test_draw_rect.pdf")
    output_path = os.path.join(tmp_path, "output.pdf")

    result = runner.invoke(
        cli_app,
        [
            "create",
            "raw",
            os.path.join(static_pdfs, "sample_template.pdf"),
            "-f",
            os.path.join(json_samples, "test_draw_rect.json"),
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
def test_draw_circle(pdf_samples, static_pdfs, json_samples, tmp_path):
    expected_path = os.path.join(pdf_samples, "docs", "test_draw_circle.pdf")
    output_path = os.path.join(tmp_path, "output.pdf")

    result = runner.invoke(
        cli_app,
        [
            "create",
            "raw",
            os.path.join(static_pdfs, "sample_template.pdf"),
            "-f",
            os.path.join(json_samples, "test_draw_circle.json"),
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
