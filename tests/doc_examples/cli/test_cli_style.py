# -*- coding: utf-8 -*-


import json
import os

import pytest
import yaml
from pypdf import PdfReader
from typer.testing import CliRunner

from PyPDFForm.cli.root import cli_app
from PyPDFForm.lib.constants import Title

runner = CliRunner()


@pytest.mark.cli_test
def test_change_title(static_pdfs, tmp_path):
    output_path = os.path.join(tmp_path, "output.pdf")
    result = runner.invoke(
        cli_app,
        [
            "update",
            "title",
            os.path.join(static_pdfs, "sample_template.pdf"),
            "-t",
            "My PDF",
            "-o",
            output_path,
        ],
    )
    assert result.exit_code == 0

    reader = PdfReader(output_path)
    assert (reader.metadata or {}).get(Title) == "My PDF"


@pytest.mark.requires_zlib_over_zlib_ng
@pytest.mark.cli_test
def test_change_text_font(pdf_samples, static_pdfs, yaml_samples, tmp_path):
    expected_path = os.path.join(pdf_samples, "docs", "test_change_text_font.pdf")
    output_path = os.path.join(tmp_path, "output.pdf")

    result = runner.invoke(
        cli_app,
        [
            "update",
            "field",
            os.path.join(static_pdfs, "sample_template.pdf"),
            "-f",
            os.path.join(yaml_samples, "test_change_text_font.yaml"),
            "-o",
            output_path,
        ],
    )
    assert result.exit_code == 0

    runner.invoke(
        cli_app,
        [
            "fill",
            output_path,
            "-f",
            os.path.join(yaml_samples, "test_fill_text_check.yaml"),
        ],
    )

    with open(expected_path, "rb") as f1, open(output_path, "rb") as f2:
        expected = f1.read()
        actual = f2.read()

        assert len(expected) == len(actual)
        assert expected == actual


@pytest.mark.cli_test
def test_change_text_font_size(pdf_samples, static_pdfs, yaml_samples, tmp_path):
    expected_path = os.path.join(pdf_samples, "docs", "test_change_text_font_size.pdf")
    output_path = os.path.join(tmp_path, "output.pdf")

    result = runner.invoke(
        cli_app,
        [
            "update",
            "field",
            os.path.join(static_pdfs, "sample_template.pdf"),
            "-f",
            os.path.join(yaml_samples, "test_change_text_font_size.yaml"),
            "-o",
            output_path,
        ],
    )
    assert result.exit_code == 0

    runner.invoke(
        cli_app,
        [
            "fill",
            output_path,
            "-f",
            os.path.join(yaml_samples, "test_fill_text_check.yaml"),
        ],
    )

    with open(expected_path, "rb") as f1, open(output_path, "rb") as f2:
        expected = f1.read()
        actual = f2.read()

        assert len(expected) == len(actual)
        assert expected == actual


@pytest.mark.cli_test
def test_change_text_font_color(pdf_samples, static_pdfs, yaml_samples, tmp_path):
    expected_path = os.path.join(pdf_samples, "docs", "test_change_text_font_color.pdf")
    output_path = os.path.join(tmp_path, "output.pdf")

    result = runner.invoke(
        cli_app,
        [
            "update",
            "field",
            os.path.join(static_pdfs, "sample_template.pdf"),
            "-f",
            os.path.join(yaml_samples, "test_change_text_font_color.yaml"),
            "-o",
            output_path,
        ],
    )
    assert result.exit_code == 0

    runner.invoke(
        cli_app,
        [
            "fill",
            output_path,
            "-f",
            os.path.join(yaml_samples, "test_fill_text_check.yaml"),
        ],
    )

    with open(expected_path, "rb") as f1, open(output_path, "rb") as f2:
        expected = f1.read()
        actual = f2.read()

        assert len(expected) == len(actual)
        assert expected == actual


@pytest.mark.cli_test
def test_change_text_alignment(pdf_samples, static_pdfs, yaml_samples, tmp_path):
    expected_path = os.path.join(pdf_samples, "docs", "test_change_text_alignment.pdf")
    output_path = os.path.join(tmp_path, "output.pdf")

    result = runner.invoke(
        cli_app,
        [
            "update",
            "field",
            os.path.join(static_pdfs, "sample_template.pdf"),
            "-f",
            os.path.join(yaml_samples, "test_change_text_alignment.yaml"),
            "-o",
            output_path,
        ],
    )
    assert result.exit_code == 0

    runner.invoke(
        cli_app,
        [
            "fill",
            output_path,
            "-f",
            os.path.join(yaml_samples, "test_fill_text_check.yaml"),
        ],
    )

    with open(expected_path, "rb") as f1, open(output_path, "rb") as f2:
        expected = f1.read()
        actual = f2.read()

        assert len(expected) == len(actual)
        assert expected == actual


@pytest.mark.cli_test
def test_change_text_max_length(pdf_samples, static_pdfs, yaml_samples, tmp_path):
    expected_path = os.path.join(pdf_samples, "docs", "test_change_text_max_length.pdf")
    output_path = os.path.join(tmp_path, "output.pdf")

    result = runner.invoke(
        cli_app,
        [
            "update",
            "field",
            os.path.join(static_pdfs, "sample_template.pdf"),
            "-f",
            os.path.join(yaml_samples, "test_change_text_max_length.yaml"),
            "-o",
            output_path,
        ],
    )
    assert result.exit_code == 0

    runner.invoke(
        cli_app,
        [
            "fill",
            output_path,
            "-f",
            os.path.join(yaml_samples, "test_change_text_max_length_comb_data.yaml"),
        ],
    )

    with open(expected_path, "rb") as f1, open(output_path, "rb") as f2:
        expected = f1.read()
        actual = f2.read()

        assert len(expected) == len(actual)
        assert expected == actual


@pytest.mark.cli_test
def test_change_text_comb(pdf_samples, static_pdfs, yaml_samples, tmp_path):
    expected_path = os.path.join(pdf_samples, "docs", "test_change_text_comb.pdf")
    output_path = os.path.join(tmp_path, "output.pdf")

    result = runner.invoke(
        cli_app,
        [
            "update",
            "field",
            os.path.join(static_pdfs, "sample_template.pdf"),
            "-f",
            os.path.join(yaml_samples, "test_change_text_comb.yaml"),
            "-o",
            output_path,
        ],
    )
    assert result.exit_code == 0

    runner.invoke(
        cli_app,
        [
            "fill",
            output_path,
            "-f",
            os.path.join(yaml_samples, "test_change_text_max_length_comb_data.yaml"),
        ],
    )

    with open(expected_path, "rb") as f1, open(output_path, "rb") as f2:
        expected = f1.read()
        actual = f2.read()

        assert len(expected) == len(actual)
        assert expected == actual


@pytest.mark.cli_test
def test_change_text_multiline(pdf_samples, static_pdfs, yaml_samples, tmp_path):
    expected_path = os.path.join(pdf_samples, "docs", "test_change_text_multiline.pdf")
    output_path = os.path.join(tmp_path, "output.pdf")
    data_yaml = os.path.join(tmp_path, "data.yaml")
    with open(data_yaml, "w", encoding="utf-8") as f:
        yaml.safe_dump(
            {
                "test": "test_1\ntest_1",
                "check": True,
                "test_2": "test_2\ntest_2",
                "check_2": False,
                "test_3": "test_3\ntest_3",
                "check_3": True,
            },
            f,
        )

    result = runner.invoke(
        cli_app,
        [
            "update",
            "field",
            os.path.join(static_pdfs, "sample_template.pdf"),
            "-f",
            os.path.join(yaml_samples, "test_change_text_multiline.yaml"),
            "-o",
            output_path,
        ],
    )
    assert result.exit_code == 0

    runner.invoke(
        cli_app,
        [
            "fill",
            output_path,
            "-f",
            data_yaml,
        ],
    )

    with open(expected_path, "rb") as f1, open(output_path, "rb") as f2:
        expected = f1.read()
        actual = f2.read()

        assert len(expected) == len(actual)
        assert expected == actual


@pytest.mark.cli_test
def test_change_check_size(pdf_samples, static_pdfs, yaml_samples, tmp_path):
    expected_path = os.path.join(pdf_samples, "docs", "test_change_check_size.pdf")
    output_path = os.path.join(tmp_path, "output.pdf")
    data_yaml = os.path.join(tmp_path, "data.yaml")
    with open(data_yaml, "w", encoding="utf-8") as f:
        yaml.safe_dump(
            {
                "check": True,
                "check_2": True,
                "check_3": True,
            },
            f,
        )

    result = runner.invoke(
        cli_app,
        [
            "update",
            "field",
            os.path.join(static_pdfs, "sample_template.pdf"),
            "-f",
            os.path.join(yaml_samples, "test_change_check_size.yaml"),
            "-o",
            output_path,
        ],
    )
    assert result.exit_code == 0

    runner.invoke(
        cli_app,
        [
            "fill",
            output_path,
            "-f",
            data_yaml,
        ],
    )

    with open(expected_path, "rb") as f1, open(output_path, "rb") as f2:
        expected = f1.read()
        actual = f2.read()

        assert len(expected) == len(actual)
        assert expected == actual


@pytest.mark.cli_test
def test_change_dropdown_choices(pdf_samples, static_pdfs, yaml_samples, tmp_path):
    expected_path = os.path.join(
        pdf_samples, "docs", "test_change_dropdown_choices.pdf"
    )
    output_path = os.path.join(tmp_path, "output.pdf")

    result = runner.invoke(
        cli_app,
        [
            "update",
            "field",
            os.path.join(static_pdfs, "sample_template_with_dropdown.pdf"),
            "-f",
            os.path.join(yaml_samples, "test_change_dropdown_choices.yaml"),
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
def test_change_dropdown_choices_with_export_values(
    pdf_samples, static_pdfs, yaml_samples, tmp_path
):
    expected_path = os.path.join(
        pdf_samples, "docs", "test_change_dropdown_choices_with_export_values.pdf"
    )
    output_path = os.path.join(tmp_path, "output.pdf")

    result = runner.invoke(
        cli_app,
        [
            "update",
            "field",
            os.path.join(static_pdfs, "sample_template_with_dropdown.pdf"),
            "-f",
            os.path.join(
                yaml_samples, "test_change_dropdown_choices_with_export_values.yaml"
            ),
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
def test_change_dropdown_font(pdf_samples, static_pdfs, yaml_samples, tmp_path):
    expected_path = os.path.join(pdf_samples, "docs", "test_change_dropdown_font.pdf")
    output_path = os.path.join(tmp_path, "output.pdf")

    result = runner.invoke(
        cli_app,
        [
            "update",
            "field",
            os.path.join(static_pdfs, "sample_template_with_dropdown.pdf"),
            "-f",
            os.path.join(yaml_samples, "test_change_dropdown_font.yaml"),
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
def test_change_dropdown_font_size(pdf_samples, static_pdfs, yaml_samples, tmp_path):
    expected_path = os.path.join(
        pdf_samples, "docs", "test_change_dropdown_font_size.pdf"
    )
    output_path = os.path.join(tmp_path, "output.pdf")

    result = runner.invoke(
        cli_app,
        [
            "update",
            "field",
            os.path.join(static_pdfs, "sample_template_with_dropdown.pdf"),
            "-f",
            os.path.join(yaml_samples, "test_change_dropdown_font_size.yaml"),
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
def test_change_dropdown_font_color(pdf_samples, static_pdfs, yaml_samples, tmp_path):
    expected_path = os.path.join(
        pdf_samples, "docs", "test_change_dropdown_font_color.pdf"
    )
    output_path = os.path.join(tmp_path, "output.pdf")

    result = runner.invoke(
        cli_app,
        [
            "update",
            "field",
            os.path.join(static_pdfs, "sample_template_with_dropdown.pdf"),
            "-f",
            os.path.join(yaml_samples, "test_change_dropdown_font_color.yaml"),
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
def test_update_key(static_pdfs, yaml_samples, tmp_path):
    output_path = os.path.join(tmp_path, "output.pdf")

    result = runner.invoke(
        cli_app,
        [
            "update",
            "rename",
            os.path.join(static_pdfs, "sample_template.pdf"),
            "-f",
            os.path.join(yaml_samples, "test_update_key.yaml"),
            "-o",
            output_path,
        ],
    )
    assert result.exit_code == 0

    result = runner.invoke(cli_app, ["inspect", "sample", output_path])

    sample_data = json.loads(result.output)

    assert "test" not in sample_data
    assert "test_text" in sample_data

    assert "test_2" not in sample_data
    assert "test_text_2" in sample_data


@pytest.mark.cli_test
def test_update_key_index(pdf_samples, static_pdfs, yaml_samples, tmp_path):
    expected_path = os.path.join(pdf_samples, "docs", "test_update_key_index.pdf")
    output_path = os.path.join(tmp_path, "output.pdf")
    sample_data = os.path.join(tmp_path, "sample_data.yaml")

    result = runner.invoke(
        cli_app,
        [
            "update",
            "rename",
            os.path.join(static_pdfs, "733.pdf"),
            "-f",
            os.path.join(yaml_samples, "test_update_key_index.yaml"),
            "-o",
            output_path,
        ],
    )
    assert result.exit_code == 0

    result = runner.invoke(
        cli_app,
        ["inspect", "sample", output_path],
    )

    with open(sample_data, "w", encoding="utf-8") as f:
        yaml.safe_dump(json.loads(result.output), f)

    runner.invoke(
        cli_app,
        [
            "fill",
            output_path,
            "-f",
            sample_data,
        ],
    )

    with open(expected_path, "rb") as f1, open(output_path, "rb") as f2:
        expected = f1.read()
        actual = f2.read()

        assert len(expected) == len(actual)
        assert expected == actual


@pytest.mark.cli_test
def test_change_field_editability(pdf_samples, static_pdfs, yaml_samples, tmp_path):
    expected_path = os.path.join(
        pdf_samples, "docs", "test_change_field_editability.pdf"
    )
    output_path = os.path.join(tmp_path, "output.pdf")
    data_yaml = os.path.join(tmp_path, "data.yaml")
    with open(data_yaml, "w", encoding="utf-8") as f:
        yaml.safe_dump(
            {
                "test_1": "test_1",
                "test_2": "test_2",
                "test_3": "test_3",
                "check_1": True,
                "check_2": True,
                "check_3": True,
                "radio_1": 1,
                "dropdown_1": 0,
            },
            f,
        )

    runner.invoke(
        cli_app,
        [
            "fill",
            os.path.join(static_pdfs, "sample_template_with_dropdown.pdf"),
            "-f",
            data_yaml,
            "-o",
            output_path,
            "--flatten",
        ],
    )

    result = runner.invoke(
        cli_app,
        [
            "update",
            "field",
            output_path,
            "-f",
            os.path.join(yaml_samples, "test_change_field_editability.yaml"),
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
def test_change_field_visibility(pdf_samples, static_pdfs, yaml_samples, tmp_path):
    expected_path = os.path.join(
        pdf_samples, "docs", "test_change_field_visibility.pdf"
    )
    output_path = os.path.join(tmp_path, "output.pdf")

    result = runner.invoke(
        cli_app,
        [
            "update",
            "field",
            os.path.join(static_pdfs, "sample_template.pdf"),
            "-f",
            os.path.join(yaml_samples, "test_change_field_visibility.yaml"),
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
def test_remove_fields(pdf_samples, static_pdfs, tmp_path):
    expected_path = os.path.join(pdf_samples, "docs", "test_remove_fields.pdf")
    output_path = os.path.join(tmp_path, "output.pdf")

    result = runner.invoke(
        cli_app,
        [
            "remove",
            "field",
            os.path.join(static_pdfs, "sample_template.pdf"),
            "--field",
            "test",
            "--field",
            "test_2",
            "--field",
            "check_2",
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
