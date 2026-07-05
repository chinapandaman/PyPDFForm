# -*- coding: utf-8 -*-

import os

import pytest
from typer.testing import CliRunner

from PyPDFForm.cli.root import cli_app

runner = CliRunner()


@pytest.mark.requires_zlib_over_zlib_ng
@pytest.mark.cli_test
def test_bulk_create_fields(pdf_samples, yaml_samples, tmp_path):
    expected_path = os.path.join(pdf_samples, "docs", "test_bulk_create_fields.pdf")
    output_path = os.path.join(tmp_path, "output.pdf")

    result = runner.invoke(
        cli_app,
        [
            "create",
            "field",
            os.path.join(pdf_samples, "dummy.pdf"),
            "-f",
            os.path.join(yaml_samples, "test_bulk_create_fields.yaml"),
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


@pytest.mark.requires_zlib_over_zlib_ng
@pytest.mark.cli_test
def test_create_text(pdf_samples, yaml_samples, tmp_path):
    expected_path = os.path.join(pdf_samples, "docs", "test_create_text.pdf")
    output_path = os.path.join(tmp_path, "output.pdf")

    result = runner.invoke(
        cli_app,
        [
            "create",
            "field",
            os.path.join(pdf_samples, "dummy.pdf"),
            "-f",
            os.path.join(yaml_samples, "test_create_text.yaml"),
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


@pytest.mark.requires_zlib_over_zlib_ng
@pytest.mark.cli_test
def test_create_check(pdf_samples, yaml_samples, tmp_path):
    expected_path = os.path.join(pdf_samples, "docs", "test_create_check.pdf")
    output_path = os.path.join(tmp_path, "output.pdf")

    result = runner.invoke(
        cli_app,
        [
            "create",
            "field",
            os.path.join(pdf_samples, "dummy.pdf"),
            "-f",
            os.path.join(yaml_samples, "test_create_check.yaml"),
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


@pytest.mark.requires_zlib_over_zlib_ng
@pytest.mark.cli_test
def test_create_radio(pdf_samples, yaml_samples, tmp_path):
    expected_path = os.path.join(pdf_samples, "docs", "test_create_radio.pdf")
    output_path = os.path.join(tmp_path, "output.pdf")

    result = runner.invoke(
        cli_app,
        [
            "create",
            "field",
            os.path.join(pdf_samples, "dummy.pdf"),
            "-f",
            os.path.join(yaml_samples, "test_create_radio.yaml"),
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


@pytest.mark.requires_zlib_over_zlib_ng
@pytest.mark.cli_test
def test_create_dropdown(pdf_samples, yaml_samples, tmp_path):
    expected_path = os.path.join(pdf_samples, "docs", "test_create_dropdown.pdf")
    output_path = os.path.join(tmp_path, "output.pdf")

    result = runner.invoke(
        cli_app,
        [
            "create",
            "field",
            os.path.join(pdf_samples, "dummy.pdf"),
            "-f",
            os.path.join(yaml_samples, "test_create_dropdown.yaml"),
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


@pytest.mark.requires_zlib_over_zlib_ng
@pytest.mark.cli_test
def test_create_dropdown_with_export_values(pdf_samples, yaml_samples, tmp_path):
    expected_path = os.path.join(
        pdf_samples, "docs", "test_create_dropdown_with_export_values.pdf"
    )
    output_path = os.path.join(tmp_path, "output.pdf")

    result = runner.invoke(
        cli_app,
        [
            "create",
            "field",
            os.path.join(pdf_samples, "dummy.pdf"),
            "-f",
            os.path.join(yaml_samples, "test_create_dropdown_with_export_values.yaml"),
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
def test_create_sig(pdf_samples, yaml_samples, tmp_path):
    expected_path = os.path.join(pdf_samples, "docs", "test_create_sig.pdf")
    output_path = os.path.join(tmp_path, "output.pdf")

    result = runner.invoke(
        cli_app,
        [
            "create",
            "field",
            os.path.join(pdf_samples, "dummy.pdf"),
            "-f",
            os.path.join(yaml_samples, "test_create_sig.yaml"),
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
def test_create_image(pdf_samples, yaml_samples, tmp_path):
    expected_path = os.path.join(pdf_samples, "docs", "test_create_image.pdf")
    output_path = os.path.join(tmp_path, "output.pdf")

    result = runner.invoke(
        cli_app,
        [
            "create",
            "field",
            os.path.join(pdf_samples, "dummy.pdf"),
            "-f",
            os.path.join(yaml_samples, "test_create_image.yaml"),
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
