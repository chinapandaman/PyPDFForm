# -*- coding: utf-8 -*-

import os

import pytest
from typer.testing import CliRunner

from PyPDFForm.cli.root import cli_app

runner = CliRunner()


def write_invalid_json(tmp_path, content):
    data_path = tmp_path / "invalid.json"
    data_path.write_text(content, encoding="utf-8")
    return str(data_path)


def assert_cli_error(result, *expected_messages, output_path=None):
    assert result.exit_code == 2
    for message in expected_messages:
        assert message in result.output
    if output_path is not None:
        assert not os.path.exists(output_path)


@pytest.mark.cli_test
def test_root_command_no_arg_help():
    result = runner.invoke(cli_app)

    assert_cli_error(result, "Create, fill, inspect, and update PDF forms.", "Usage:")
    assert "main" not in result.output


@pytest.mark.cli_test
def test_fill_nonexistent_input_pdf(json_samples):
    result = runner.invoke(
        cli_app,
        [
            "fill",
            "missing.pdf",
            "-f",
            os.path.join(json_samples, "test_fill_text_check.json"),
        ],
    )

    assert_cli_error(result, "does not exist")


@pytest.mark.cli_test
def test_fill_wrong_known_field_type(pdf_samples, tmp_path):
    data_path = write_invalid_json(tmp_path, '{"check": "yes"}')
    output_path = os.path.join(tmp_path, "output.pdf")

    result = runner.invoke(
        cli_app,
        [
            "fill",
            os.path.join(pdf_samples, "sample_template.pdf"),
            "-f",
            data_path,
            "-o",
            output_path,
        ],
    )

    assert_cli_error(result, "Invalid JSON file at check", output_path=output_path)


@pytest.mark.cli_test
def test_create_extract_start_after_end(pdf_samples, tmp_path):
    output_path = os.path.join(tmp_path, "output.pdf")

    result = runner.invoke(
        cli_app,
        [
            "create",
            "extract",
            os.path.join(pdf_samples, "sample_template.pdf"),
            "-o",
            output_path,
            "--start",
            "3",
            "--end",
            "1",
        ],
    )

    assert_cli_error(
        result,
        "End page must be greater than or equal to start",
        "page.",
        output_path=output_path,
    )


@pytest.mark.cli_test
def test_create_field_malformed_json(pdf_samples, tmp_path):
    data_path = write_invalid_json(tmp_path, '{"text": [')
    output_path = os.path.join(tmp_path, "output.pdf")

    result = runner.invoke(
        cli_app,
        [
            "create",
            "field",
            os.path.join(pdf_samples, "dummy.pdf"),
            "-f",
            data_path,
            "-o",
            output_path,
        ],
    )

    assert_cli_error(result, "Invalid JSON file", output_path=output_path)


@pytest.mark.cli_test
def test_create_field_schema_error(pdf_samples, tmp_path):
    data_path = write_invalid_json(
        tmp_path,
        (
            '{"text": [{"name": "new_text", "page_number": 1, '
            '"x": 1, "y": 1, "alignment": 3}]}'
        ),
    )
    output_path = os.path.join(tmp_path, "output.pdf")

    result = runner.invoke(
        cli_app,
        [
            "create",
            "field",
            os.path.join(pdf_samples, "dummy.pdf"),
            "-f",
            data_path,
            "-o",
            output_path,
        ],
    )

    assert_cli_error(
        result,
        "Invalid JSON file at text.0.alignment",
        output_path=output_path,
    )


@pytest.mark.cli_test
def test_create_raw_schema_error(pdf_samples, tmp_path):
    data_path = write_invalid_json(
        tmp_path,
        '{"text": [{"text": "hello", "page_number": "1", "x": 1, "y": 1}]}',
    )
    output_path = os.path.join(tmp_path, "output.pdf")

    result = runner.invoke(
        cli_app,
        [
            "create",
            "raw",
            os.path.join(pdf_samples, "dummy.pdf"),
            "-f",
            data_path,
            "-o",
            output_path,
        ],
    )

    assert_cli_error(
        result,
        "Invalid JSON file at text.0.page_number",
        output_path=output_path,
    )


@pytest.mark.cli_test
def test_create_annotation_rejects_multiple_link_destinations(pdf_samples, tmp_path):
    data_path = write_invalid_json(
        tmp_path,
        (
            '{"link": [{"page_number": 1, "x": 1, "y": 1, '
            '"width": 10, "height": 10, "uri": "https://example.com", "page": 2}]}'
        ),
    )
    output_path = os.path.join(tmp_path, "output.pdf")

    result = runner.invoke(
        cli_app,
        [
            "create",
            "annotation",
            os.path.join(pdf_samples, "dummy.pdf"),
            "-f",
            data_path,
            "-o",
            output_path,
        ],
    )

    assert_cli_error(result, "Invalid JSON file at link.0", output_path=output_path)


@pytest.mark.cli_test
def test_create_grid_invalid_range(pdf_samples):
    result = runner.invoke(
        cli_app,
        ["create", "grid", os.path.join(pdf_samples, "dummy.pdf"), "--red", "2"],
    )

    assert_cli_error(result, "is not in the range")


@pytest.mark.cli_test
def test_inspect_location_unknown_field(pdf_samples):
    result = runner.invoke(
        cli_app,
        [
            "inspect",
            "location",
            os.path.join(pdf_samples, "sample_template.pdf"),
            "--field",
            "missing_name",
        ],
    )

    assert_cli_error(result, "Form field 'missing_name' does not exist")


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

    assert_cli_error(result, "is not one of")


@pytest.mark.cli_test
def test_update_rename_rejects_full_widget_name_option(pdf_samples, tmp_path):
    data_path = write_invalid_json(
        tmp_path,
        '[{"Gain de 2 classes.0": {"new_key": "new_name"}}]',
    )
    output_path = os.path.join(tmp_path, "output.pdf")

    result = runner.invoke(
        cli_app,
        [
            "--use-full-widget-name",
            "update",
            "rename",
            os.path.join(pdf_samples, "sample_template_with_full_key.pdf"),
            "-f",
            data_path,
            "-o",
            output_path,
        ],
    )

    assert_cli_error(
        result,
        "Renaming form fields",
        "supported when",
        output_path=output_path,
    )


@pytest.mark.cli_test
def test_update_field_schema_error(pdf_samples, tmp_path):
    data_path = write_invalid_json(tmp_path, '{"test": {"alignment": 3}}')
    output_path = os.path.join(tmp_path, "output.pdf")

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

    assert_cli_error(
        result, "Invalid JSON file at test.alignment", output_path=output_path
    )


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

    assert_cli_error(result, "is not 'open'")
