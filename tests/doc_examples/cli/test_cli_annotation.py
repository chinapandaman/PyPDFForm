# -*- coding: utf-8 -*-


import os

import pytest
from typer.testing import CliRunner

from PyPDFForm.cli.root import cli_app

runner = CliRunner()


@pytest.mark.cli_test
def test_text_annotations(pdf_samples, static_pdfs, json_samples, tmp_path):
    expected_path = os.path.join(pdf_samples, "docs", "test_text_annotations.pdf")
    output_path = os.path.join(tmp_path, "output.pdf")

    result = runner.invoke(
        cli_app,
        [
            "create",
            "annotation",
            os.path.join(static_pdfs, "sample_template.pdf"),
            "-f",
            os.path.join(json_samples, "test_text_annotations.json"),
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
def test_uri_link_annotations(pdf_samples, static_pdfs, json_samples, tmp_path):
    expected_path = os.path.join(pdf_samples, "docs", "test_uri_link_annotations.pdf")
    output_path = os.path.join(tmp_path, "output.pdf")

    result = runner.invoke(
        cli_app,
        [
            "create",
            "annotation",
            os.path.join(static_pdfs, "sample_template.pdf"),
            "-f",
            os.path.join(json_samples, "test_uri_link_annotations.json"),
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
def test_page_link_annotations(pdf_samples, static_pdfs, json_samples, tmp_path):
    expected_path = os.path.join(pdf_samples, "docs", "test_page_link_annotations.pdf")
    output_path = os.path.join(tmp_path, "output.pdf")

    result = runner.invoke(
        cli_app,
        [
            "create",
            "annotation",
            os.path.join(static_pdfs, "sample_template.pdf"),
            "-f",
            os.path.join(json_samples, "test_page_link_annotations.json"),
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
def test_highlight_annotations(pdf_samples, static_pdfs, json_samples, tmp_path):
    expected_path = os.path.join(pdf_samples, "docs", "test_highlight_annotations.pdf")
    output_path = os.path.join(tmp_path, "output.pdf")

    result = runner.invoke(
        cli_app,
        [
            "create",
            "annotation",
            os.path.join(static_pdfs, "sample_template.pdf"),
            "-f",
            os.path.join(json_samples, "test_highlight_annotations.json"),
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
def test_underline_annotations(pdf_samples, static_pdfs, json_samples, tmp_path):
    expected_path = os.path.join(pdf_samples, "docs", "test_underline_annotations.pdf")
    output_path = os.path.join(tmp_path, "output.pdf")

    result = runner.invoke(
        cli_app,
        [
            "create",
            "annotation",
            os.path.join(static_pdfs, "sample_template.pdf"),
            "-f",
            os.path.join(json_samples, "test_underline_annotations.json"),
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
def test_squiggly_annotations(pdf_samples, static_pdfs, json_samples, tmp_path):
    expected_path = os.path.join(pdf_samples, "docs", "test_squiggly_annotations.pdf")
    output_path = os.path.join(tmp_path, "output.pdf")

    result = runner.invoke(
        cli_app,
        [
            "create",
            "annotation",
            os.path.join(static_pdfs, "sample_template.pdf"),
            "-f",
            os.path.join(json_samples, "test_squiggly_annotations.json"),
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
def test_strikeout_annotations(pdf_samples, static_pdfs, json_samples, tmp_path):
    expected_path = os.path.join(pdf_samples, "docs", "test_strikeout_annotations.pdf")
    output_path = os.path.join(tmp_path, "output.pdf")

    result = runner.invoke(
        cli_app,
        [
            "create",
            "annotation",
            os.path.join(static_pdfs, "sample_template.pdf"),
            "-f",
            os.path.join(json_samples, "test_strikeout_annotations.json"),
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
def test_rubber_stamp_annotations(pdf_samples, static_pdfs, json_samples, tmp_path):
    expected_path = os.path.join(
        pdf_samples, "docs", "test_rubber_stamp_annotations.pdf"
    )
    output_path = os.path.join(tmp_path, "output.pdf")

    result = runner.invoke(
        cli_app,
        [
            "create",
            "annotation",
            os.path.join(static_pdfs, "sample_template.pdf"),
            "-f",
            os.path.join(json_samples, "test_rubber_stamp_annotations.json"),
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
