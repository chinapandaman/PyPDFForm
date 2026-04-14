# -*- coding: utf-8 -*-

import os

import pytest
from typer.testing import CliRunner

from PyPDFForm.cli import cli_app

runner = CliRunner()


@pytest.mark.cli_test
def test_fill_text_check(pdf_samples, static_pdfs, json_samples, tmp_path):
    expected_path = os.path.join(pdf_samples, "docs", "test_fill_text_check.pdf")
    output_path = os.path.join(tmp_path, "output.pdf")

    result = runner.invoke(
        cli_app,
        [
            "fill",
            os.path.join(static_pdfs, "sample_template.pdf"),
            "-f",
            os.path.join(json_samples, "test_fill_text_check.json"),
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
def test_fill_radio(pdf_samples, static_pdfs, json_samples, tmp_path):
    expected_path = os.path.join(pdf_samples, "docs", "test_fill_radio.pdf")
    output_path = os.path.join(tmp_path, "output.pdf")

    result = runner.invoke(
        cli_app,
        [
            "fill",
            os.path.join(static_pdfs, "sample_template_with_radio_button.pdf"),
            "-f",
            os.path.join(json_samples, "test_fill_radio.json"),
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
def test_fill_dropdown(pdf_samples, static_pdfs, json_samples, tmp_path):
    expected_path = os.path.join(pdf_samples, "docs", "test_fill_dropdown.pdf")
    output_path = os.path.join(tmp_path, "output.pdf")

    result = runner.invoke(
        cli_app,
        [
            "fill",
            os.path.join(static_pdfs, "sample_template_with_dropdown.pdf"),
            "-f",
            os.path.join(json_samples, "test_fill_dropdown.json"),
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
def test_fill_dropdown_via_str(pdf_samples, static_pdfs, json_samples, tmp_path):
    expected_path = os.path.join(pdf_samples, "docs", "test_fill_dropdown.pdf")
    output_path = os.path.join(tmp_path, "output.pdf")

    result = runner.invoke(
        cli_app,
        [
            "fill",
            os.path.join(static_pdfs, "sample_template_with_dropdown.pdf"),
            "-f",
            os.path.join(json_samples, "test_fill_dropdown_via_str.json"),
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


@pytest.mark.posix_only
@pytest.mark.cli_test
def test_fill_sig(pdf_samples, static_pdfs, json_samples, tmp_path):
    expected_path = os.path.join(pdf_samples, "docs", "test_fill_sig.pdf")
    output_path = os.path.join(tmp_path, "output.pdf")

    result = runner.invoke(
        cli_app,
        [
            "fill",
            os.path.join(static_pdfs, "sample_template_with_signature.pdf"),
            "-f",
            os.path.join(json_samples, "test_fill_sig.json"),
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


@pytest.mark.posix_only
@pytest.mark.cli_test
def test_fill_sig_ratio(pdf_samples, static_pdfs, json_samples, tmp_path):
    expected_path = os.path.join(pdf_samples, "docs", "test_fill_sig_ratio.pdf")
    output_path = os.path.join(tmp_path, "output.pdf")

    result = runner.invoke(
        cli_app,
        [
            "fill",
            os.path.join(static_pdfs, "sample_template_with_signature.pdf"),
            "-f",
            os.path.join(json_samples, "test_fill_sig_ratio.json"),
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
def test_fill_image(pdf_samples, static_pdfs, json_samples, tmp_path):
    expected_path = os.path.join(pdf_samples, "docs", "test_fill_image.pdf")
    output_path = os.path.join(tmp_path, "output.pdf")

    result = runner.invoke(
        cli_app,
        [
            "fill",
            os.path.join(static_pdfs, "sample_template_with_image_field.pdf"),
            "-f",
            os.path.join(json_samples, "test_fill_image.json"),
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
def test_fill_image_ratio(pdf_samples, static_pdfs, json_samples, tmp_path):
    expected_path = os.path.join(pdf_samples, "docs", "test_fill_image_ratio.pdf")
    output_path = os.path.join(tmp_path, "output.pdf")

    result = runner.invoke(
        cli_app,
        [
            "fill",
            os.path.join(static_pdfs, "sample_template_with_image_field.pdf"),
            "-f",
            os.path.join(json_samples, "test_fill_image_ratio.json"),
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
