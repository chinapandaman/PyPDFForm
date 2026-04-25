# -*- coding: utf-8 -*-

import os

import pytest
from typer.testing import CliRunner

from PyPDFForm.cli.root import cli_app

runner = CliRunner()


@pytest.mark.cli_test
def test_update_title_missing_title(pdf_samples):
    result = runner.invoke(
        cli_app,
        ["update", "title", os.path.join(pdf_samples, "sample_template.pdf")],
    )

    assert result.exit_code == 2
    assert "Missing option" in result.output


@pytest.mark.cli_test
def test_update_version_invalid_version(pdf_samples):
    result = runner.invoke(
        cli_app,
        [
            "update",
            "version",
            os.path.join(pdf_samples, "dummy.pdf"),
            "--version",
            "3.0",
        ],
    )

    assert result.exit_code == 2
    assert "is not one of" in result.output


@pytest.mark.cli_test
def test_update_bounds_missing_field(pdf_samples):
    result = runner.invoke(
        cli_app,
        [
            "update",
            "bounds",
            os.path.join(pdf_samples, "sample_template.pdf"),
            "--x",
            "1",
        ],
    )

    assert result.exit_code == 2
    assert "Missing option" in result.output


@pytest.mark.parametrize("option", ["--width", "--height"])
@pytest.mark.cli_test
def test_update_bounds_invalid_size(pdf_samples, option):
    result = runner.invoke(
        cli_app,
        [
            "update",
            "bounds",
            os.path.join(pdf_samples, "sample_template.pdf"),
            "--field",
            "test",
            option,
            "-1",
        ],
    )

    assert result.exit_code == 2
    assert "is not in the range" in result.output


@pytest.mark.cli_test
def test_update_bounds_unknown_field(pdf_samples, tmp_path):
    output_path = os.path.join(tmp_path, "output.pdf")

    result = runner.invoke(
        cli_app,
        [
            "update",
            "bounds",
            os.path.join(pdf_samples, "sample_template.pdf"),
            "--field",
            "missing_name",
            "--x",
            "1",
            "-o",
            output_path,
        ],
    )

    assert result.exit_code == 2
    assert "Form field 'missing_name' does not exist" in result.output
    assert not os.path.exists(output_path)


@pytest.mark.cli_test
def test_update_rename_missing_new_key(pdf_samples, tmp_path):
    data_path = os.path.join(tmp_path, "invalid.json")
    output_path = os.path.join(tmp_path, "output.pdf")
    with open(data_path, "w", encoding="utf-8") as f:
        f.write('[{"test": {"index": 0}}]')

    result = runner.invoke(
        cli_app,
        [
            "update",
            "rename",
            os.path.join(pdf_samples, "sample_template.pdf"),
            "-f",
            data_path,
            "-o",
            output_path,
        ],
    )

    assert result.exit_code == 2
    assert "Invalid JSON file" in result.output
    assert not os.path.exists(output_path)


@pytest.mark.cli_test
def test_update_rename_unknown_field(pdf_samples, tmp_path):
    data_path = os.path.join(tmp_path, "invalid.json")
    output_path = os.path.join(tmp_path, "output.pdf")
    with open(data_path, "w", encoding="utf-8") as f:
        f.write('[{"missing_name": {"new_key": "new_name"}}]')

    result = runner.invoke(
        cli_app,
        [
            "update",
            "rename",
            os.path.join(pdf_samples, "sample_template.pdf"),
            "-f",
            data_path,
            "-o",
            output_path,
        ],
    )

    assert result.exit_code == 2
    assert "Form field 'missing_name' does not exist" in result.output
    assert not os.path.exists(output_path)


@pytest.mark.cli_test
def test_update_field_wrong_property_type(pdf_samples, tmp_path):
    data_path = os.path.join(tmp_path, "invalid.json")
    output_path = os.path.join(tmp_path, "output.pdf")
    with open(data_path, "w", encoding="utf-8") as f:
        f.write('{"test": {"font_color": "red"}}')

    result = runner.invoke(
        cli_app,
        [
            "update",
            "field",
            os.path.join(pdf_samples, "sample_template.pdf"),
            "-f",
            data_path,
            "-o",
            output_path,
        ],
    )

    assert result.exit_code == 2
    assert "Invalid JSON file at test.font_color" in result.output
    assert not os.path.exists(output_path)


@pytest.mark.cli_test
def test_update_field_font_color_rejects_alpha_channel(pdf_samples, tmp_path):
    data_path = os.path.join(tmp_path, "invalid.json")
    output_path = os.path.join(tmp_path, "output.pdf")
    with open(data_path, "w", encoding="utf-8") as f:
        f.write('{"test": {"font_color": [1, 0, 0, 1]}}')

    result = runner.invoke(
        cli_app,
        [
            "update",
            "field",
            os.path.join(pdf_samples, "sample_template.pdf"),
            "-f",
            data_path,
            "-o",
            output_path,
        ],
    )

    assert result.exit_code == 2
    assert "Invalid JSON file at test.font_color" in result.output
    assert not os.path.exists(output_path)


@pytest.mark.cli_test
def test_update_field_font_color_rejects_channel_out_of_range(pdf_samples, tmp_path):
    data_path = os.path.join(tmp_path, "invalid.json")
    output_path = os.path.join(tmp_path, "output.pdf")
    with open(data_path, "w", encoding="utf-8") as f:
        f.write('{"test": {"font_color": [1.1, 0, 0]}}')

    result = runner.invoke(
        cli_app,
        [
            "update",
            "field",
            os.path.join(pdf_samples, "sample_template.pdf"),
            "-f",
            data_path,
            "-o",
            output_path,
        ],
    )

    assert result.exit_code == 2
    assert "Invalid JSON file at test.font_color.0" in result.output
    assert not os.path.exists(output_path)


@pytest.mark.cli_test
def test_update_field_rejects_negative_size(pdf_samples, tmp_path):
    data_path = os.path.join(tmp_path, "invalid.json")
    output_path = os.path.join(tmp_path, "output.pdf")
    with open(data_path, "w", encoding="utf-8") as f:
        f.write('{"check": {"size": -1}}')

    result = runner.invoke(
        cli_app,
        [
            "update",
            "field",
            os.path.join(pdf_samples, "sample_template.pdf"),
            "-f",
            data_path,
            "-o",
            output_path,
        ],
    )

    assert result.exit_code == 2
    assert "Invalid JSON file at check.size" in result.output
    assert not os.path.exists(output_path)


@pytest.mark.cli_test
def test_update_field_rejects_x_property(pdf_samples, tmp_path):
    data_path = os.path.join(tmp_path, "invalid.json")
    output_path = os.path.join(tmp_path, "output.pdf")
    with open(data_path, "w", encoding="utf-8") as f:
        f.write('{"test": {"x": 1}}')

    result = runner.invoke(
        cli_app,
        [
            "update",
            "field",
            os.path.join(pdf_samples, "sample_template.pdf"),
            "-f",
            data_path,
            "-o",
            output_path,
        ],
    )

    assert result.exit_code == 2
    assert "Invalid JSON file at test" in result.output
    assert not os.path.exists(output_path)


@pytest.mark.cli_test
def test_update_field_rejects_width_property(pdf_samples, tmp_path):
    data_path = os.path.join(tmp_path, "invalid.json")
    output_path = os.path.join(tmp_path, "output.pdf")
    with open(data_path, "w", encoding="utf-8") as f:
        f.write('{"test": {"width": 1}}')

    result = runner.invoke(
        cli_app,
        [
            "update",
            "field",
            os.path.join(pdf_samples, "sample_template.pdf"),
            "-f",
            data_path,
            "-o",
            output_path,
        ],
    )

    assert result.exit_code == 2
    assert "Invalid JSON file at test" in result.output
    assert not os.path.exists(output_path)


@pytest.mark.cli_test
def test_update_field_invalid_text_alignment(pdf_samples, tmp_path):
    data_path = os.path.join(tmp_path, "invalid.json")
    output_path = os.path.join(tmp_path, "output.pdf")
    with open(data_path, "w", encoding="utf-8") as f:
        f.write('{"test": {"alignment": 3}}')

    result = runner.invoke(
        cli_app,
        [
            "update",
            "field",
            os.path.join(pdf_samples, "sample_template.pdf"),
            "-f",
            data_path,
            "-o",
            output_path,
        ],
    )

    assert result.exit_code == 2
    assert "Invalid JSON file at test.alignment" in result.output
    assert not os.path.exists(output_path)


@pytest.mark.cli_test
def test_update_field_unknown_field(pdf_samples, tmp_path):
    data_path = os.path.join(tmp_path, "invalid.json")
    output_path = os.path.join(tmp_path, "output.pdf")
    with open(data_path, "w", encoding="utf-8") as f:
        f.write('{"missing_name": {"font_size": 12}}')

    result = runner.invoke(
        cli_app,
        [
            "update",
            "field",
            os.path.join(pdf_samples, "sample_template.pdf"),
            "-f",
            data_path,
            "-o",
            output_path,
        ],
    )

    assert result.exit_code == 2
    assert "Form field 'missing_name' does not exist" in result.output
    assert not os.path.exists(output_path)


@pytest.mark.cli_test
def test_update_script_missing_script(pdf_samples):
    result = runner.invoke(
        cli_app,
        ["update", "script", os.path.join(pdf_samples, "sample_template.pdf")],
    )

    assert result.exit_code == 2
    assert "Missing option" in result.output


@pytest.mark.cli_test
def test_update_script_nonexistent_script(pdf_samples):
    result = runner.invoke(
        cli_app,
        [
            "update",
            "script",
            os.path.join(pdf_samples, "sample_template.pdf"),
            "--script",
            "missing.js",
        ],
    )

    assert result.exit_code == 2
    assert "does not exist" in result.output


@pytest.mark.cli_test
def test_update_script_invalid_event(pdf_samples, js_samples):
    result = runner.invoke(
        cli_app,
        [
            "update",
            "script",
            os.path.join(pdf_samples, "sample_template.pdf"),
            "--script",
            os.path.join(js_samples, "test_file_path_scripts.js"),
            "--event",
            "close",
        ],
    )

    assert result.exit_code == 2
    assert "is not 'open'" in result.output
