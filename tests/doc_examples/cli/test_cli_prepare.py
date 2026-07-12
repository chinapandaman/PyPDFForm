# -*- coding: utf-8 -*-

import os

import pytest
import yaml
from typer.testing import CliRunner

from PyPDFForm.cli.root import cli_app

runner = CliRunner()


@pytest.mark.cli_test
def test_create_field_dynamic_options(pdf_samples, tmp_path):
    data_path = os.path.join(tmp_path, "data.yaml")
    file_output_path = os.path.join(tmp_path, "file-output.pdf")
    options_output_path = os.path.join(tmp_path, "options-output.pdf")
    with open(data_path, "w", encoding="utf-8") as f:
        yaml.safe_dump(
            {"text": [{"name": "new_text", "page_number": 1, "x": 100, "y": 100}]},
            f,
        )

    base_args = ["create", "field", os.path.join(pdf_samples, "dummy.pdf")]
    file_result = runner.invoke(
        cli_app,
        [
            *base_args,
            "-f",
            data_path,
            "--type",
            "unsupported",
            "--ignored",
            "value",
            "-o",
            file_output_path,
        ],
    )
    options_result = runner.invoke(
        cli_app,
        [
            *base_args,
            "--type",
            "text",
            "--name",
            "new_text",
            "--page_number",
            "1",
            "--x",
            "100",
            "--y",
            "100",
            "-o",
            options_output_path,
        ],
    )

    assert file_result.exit_code == 0
    assert options_result.exit_code == 0
    with open(file_output_path, "rb") as f1, open(options_output_path, "rb") as f2:
        assert len(f1.read()) == len(f2.read())
        assert f1.read() == f2.read()


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
