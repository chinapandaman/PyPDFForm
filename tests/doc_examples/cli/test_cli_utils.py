# -*- coding: utf-8 -*-

import os

import pytest
from typer.testing import CliRunner

from PyPDFForm import PdfWrapper
from PyPDFForm.cli.root import cli_app

runner = CliRunner()


@pytest.mark.posix_only
@pytest.mark.cli_test
def test_blank_page(pdf_samples, tmp_path):
    expected_path = os.path.join(pdf_samples, "docs", "test_blank_page.pdf")
    output_path = os.path.join(tmp_path, "output.pdf")

    result = runner.invoke(
        cli_app,
        [
            "create",
            "blank",
            "-o",
            output_path,
        ],
    )
    assert result.exit_code == 0

    with open(expected_path, "rb") as f1, open(output_path, "rb") as f2:
        expected = f1.read()
        actual = f2.read()

        assert len(expected) == len(actual)


@pytest.mark.posix_only
@pytest.mark.cli_test
def test_blank_page_custom_dimensions(pdf_samples, tmp_path):
    expected_path = os.path.join(
        pdf_samples, "docs", "test_blank_page_custom_dimensions.pdf"
    )
    output_path = os.path.join(tmp_path, "output.pdf")

    result = runner.invoke(
        cli_app,
        [
            "create",
            "blank",
            "-o",
            output_path,
            "--width",
            "595.35",
            "--height",
            "841.995",
        ],
    )
    assert result.exit_code == 0

    with open(expected_path, "rb") as f1, open(output_path, "rb") as f2:
        expected = f1.read()
        actual = f2.read()

        assert len(expected) == len(actual)


@pytest.mark.posix_only
@pytest.mark.cli_test
def test_blank_page_multiply(pdf_samples, tmp_path):
    expected_path = os.path.join(pdf_samples, "docs", "test_blank_page_multiply.pdf")
    output_path = os.path.join(tmp_path, "output.pdf")

    result = runner.invoke(
        cli_app,
        ["create", "blank", "-o", output_path, "-c", "3"],
    )
    assert result.exit_code == 0

    with open(expected_path, "rb") as f1, open(output_path, "rb") as f2:
        expected = f1.read()
        actual = f2.read()

        assert len(expected) == len(actual)


@pytest.mark.cli_test
def test_extract_pages(static_pdfs, pdf_samples, json_samples, tmp_path):
    expected_path = os.path.join(pdf_samples, "docs", "test_extract_pages.pdf")
    output_path = os.path.join(tmp_path, "output.pdf")

    extract_result = runner.invoke(
        cli_app,
        [
            "create",
            "extract",
            os.path.join(static_pdfs, "sample_template.pdf"),
            "--start",
            "1",
            "--end",
            "1",
            "-o",
            output_path,
        ],
    )
    assert extract_result.exit_code == 0

    fill_result = runner.invoke(
        cli_app,
        [
            "fill",
            output_path,
            "-f",
            os.path.join(json_samples, "test_extract_pages.json"),
            "-o",
            output_path,
        ],
    )
    assert fill_result.exit_code == 0

    with open(expected_path, "rb") as f1, open(output_path, "rb") as f2:
        expected = f1.read()
        actual = f2.read()

        assert len(expected) == len(actual)
        assert expected == actual


@pytest.mark.cli_test
def test_merge(static_pdfs, pdf_samples, tmp_path):
    expected_path = os.path.join(pdf_samples, "docs", "test_merge.pdf")
    output_path = os.path.join(tmp_path, "output.pdf")

    result = runner.invoke(
        cli_app,
        [
            "create",
            "merge",
            os.path.join(pdf_samples, "dummy.pdf"),
            os.path.join(static_pdfs, "sample_template.pdf"),
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
def test_reorg_pages(static_pdfs, pdf_samples, tmp_path):
    expected_path = os.path.join(pdf_samples, "docs", "test_reorg_pages.pdf")
    first_page_path = os.path.join(tmp_path, "first_page.pdf")
    remaining_pages_path = os.path.join(tmp_path, "remaining_pages.pdf")
    output_path = os.path.join(tmp_path, "output.pdf")

    first_page_result = runner.invoke(
        cli_app,
        [
            "create",
            "extract",
            os.path.join(static_pdfs, "sample_template.pdf"),
            "--start",
            "1",
            "--end",
            "1",
            "-o",
            first_page_path,
        ],
    )
    assert first_page_result.exit_code == 0

    remaining_pages_result = runner.invoke(
        cli_app,
        [
            "create",
            "extract",
            os.path.join(static_pdfs, "sample_template.pdf"),
            "--start",
            "2",
            "-o",
            remaining_pages_path,
        ],
    )
    assert remaining_pages_result.exit_code == 0

    combine_result = runner.invoke(
        cli_app,
        [
            "create",
            "merge",
            first_page_path,
            os.path.join(pdf_samples, "dummy.pdf"),
            remaining_pages_path,
            "-o",
            output_path,
        ],
    )
    assert combine_result.exit_code == 0

    with open(expected_path, "rb") as f1, open(output_path, "rb") as f2:
        expected = f1.read()
        actual = f2.read()

        assert len(expected) == len(actual)
        assert expected == actual


@pytest.mark.cli_test
def test_change_version(static_pdfs, tmp_path):
    output_path = os.path.join(tmp_path, "output.pdf")

    result = runner.invoke(
        cli_app,
        [
            "update",
            "version",
            os.path.join(static_pdfs, "sample_template.pdf"),
            "-v",
            "2.0",
            "-o",
            output_path,
        ],
    )
    assert result.exit_code == 0

    assert PdfWrapper(output_path).version == "2.0"
