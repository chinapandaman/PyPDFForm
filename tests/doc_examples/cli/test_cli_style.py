# -*- coding: utf-8 -*-


import json
import os

import pytest
from typer.testing import CliRunner

from PyPDFForm.cli import cli_app

runner = CliRunner()


@pytest.mark.posix_only
@pytest.mark.cli_test
def test_change_text_font(pdf_samples, static_pdfs, json_samples, tmp_path):
    expected_path = os.path.join(pdf_samples, "docs", "test_change_text_font.pdf")
    output_path = os.path.join(tmp_path, "output.pdf")

    result = runner.invoke(
        cli_app,
        [
            "update",
            "field",
            os.path.join(static_pdfs, "sample_template.pdf"),
            "-f",
            os.path.join(json_samples, "test_change_text_font.json"),
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
            os.path.join(json_samples, "test_fill_text_check.json"),
        ],
    )

    with open(expected_path, "rb") as f1, open(output_path, "rb") as f2:
        expected = f1.read()
        actual = f2.read()

        assert len(expected) == len(actual)
        assert expected == actual


@pytest.mark.cli_test
def test_change_text_font_size(pdf_samples, static_pdfs, json_samples, tmp_path):
    expected_path = os.path.join(pdf_samples, "docs", "test_change_text_font_size.pdf")
    output_path = os.path.join(tmp_path, "output.pdf")

    result = runner.invoke(
        cli_app,
        [
            "update",
            "field",
            os.path.join(static_pdfs, "sample_template.pdf"),
            "-f",
            os.path.join(json_samples, "test_change_text_font_size.json"),
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
            os.path.join(json_samples, "test_fill_text_check.json"),
        ],
    )

    with open(expected_path, "rb") as f1, open(output_path, "rb") as f2:
        expected = f1.read()
        actual = f2.read()

        assert len(expected) == len(actual)
        assert expected == actual


@pytest.mark.cli_test
def test_change_text_font_color(pdf_samples, static_pdfs, json_samples, tmp_path):
    expected_path = os.path.join(pdf_samples, "docs", "test_change_text_font_color.pdf")
    output_path = os.path.join(tmp_path, "output.pdf")

    result = runner.invoke(
        cli_app,
        [
            "update",
            "field",
            os.path.join(static_pdfs, "sample_template.pdf"),
            "-f",
            os.path.join(json_samples, "test_change_text_font_color.json"),
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
            os.path.join(json_samples, "test_fill_text_check.json"),
        ],
    )

    with open(expected_path, "rb") as f1, open(output_path, "rb") as f2:
        expected = f1.read()
        actual = f2.read()

        assert len(expected) == len(actual)
        assert expected == actual


@pytest.mark.cli_test
def test_change_text_alignment(pdf_samples, static_pdfs, json_samples, tmp_path):
    expected_path = os.path.join(pdf_samples, "docs", "test_change_text_alignment.pdf")
    output_path = os.path.join(tmp_path, "output.pdf")

    result = runner.invoke(
        cli_app,
        [
            "update",
            "field",
            os.path.join(static_pdfs, "sample_template.pdf"),
            "-f",
            os.path.join(json_samples, "test_change_text_alignment.json"),
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
            os.path.join(json_samples, "test_fill_text_check.json"),
        ],
    )

    with open(expected_path, "rb") as f1, open(output_path, "rb") as f2:
        expected = f1.read()
        actual = f2.read()

        assert len(expected) == len(actual)
        assert expected == actual


@pytest.mark.cli_test
def test_change_text_max_length(pdf_samples, static_pdfs, json_samples, tmp_path):
    expected_path = os.path.join(pdf_samples, "docs", "test_change_text_max_length.pdf")
    output_path = os.path.join(tmp_path, "output.pdf")

    result = runner.invoke(
        cli_app,
        [
            "update",
            "field",
            os.path.join(static_pdfs, "sample_template.pdf"),
            "-f",
            os.path.join(json_samples, "test_change_text_max_length.json"),
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
            os.path.join(json_samples, "test_fill_text_check.json"),
        ],
    )

    with open(expected_path, "rb") as f1, open(output_path, "rb") as f2:
        expected = f1.read()
        actual = f2.read()

        assert len(expected) == len(actual)
        assert expected == actual


@pytest.mark.cli_test
def test_change_text_comb(pdf_samples, static_pdfs, json_samples, tmp_path):
    expected_path = os.path.join(pdf_samples, "docs", "test_change_text_comb.pdf")
    output_path = os.path.join(tmp_path, "output.pdf")

    result = runner.invoke(
        cli_app,
        [
            "update",
            "field",
            os.path.join(static_pdfs, "sample_template.pdf"),
            "-f",
            os.path.join(json_samples, "test_change_text_comb.json"),
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
            os.path.join(json_samples, "test_fill_text_check.json"),
        ],
    )

    with open(expected_path, "rb") as f1, open(output_path, "rb") as f2:
        expected = f1.read()
        actual = f2.read()

        assert len(expected) == len(actual)
        assert expected == actual


@pytest.mark.cli_test
def test_change_text_multiline(pdf_samples, static_pdfs, json_samples, tmp_path):
    expected_path = os.path.join(pdf_samples, "docs", "test_change_text_multiline.pdf")
    output_path = os.path.join(tmp_path, "output.pdf")
    data_json = os.path.join(tmp_path, "data.json")
    with open(data_json, "w", encoding="utf-8") as f:
        json.dump(
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
            os.path.join(json_samples, "test_change_text_multiline.json"),
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
            data_json,
        ],
    )

    with open(expected_path, "rb") as f1, open(output_path, "rb") as f2:
        expected = f1.read()
        actual = f2.read()

        assert len(expected) == len(actual)
        assert expected == actual


@pytest.mark.cli_test
def test_change_check_size(pdf_samples, static_pdfs, json_samples, tmp_path):
    expected_path = os.path.join(pdf_samples, "docs", "test_change_check_size.pdf")
    output_path = os.path.join(tmp_path, "output.pdf")
    data_json = os.path.join(tmp_path, "data.json")
    with open(data_json, "w", encoding="utf-8") as f:
        json.dump(
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
            os.path.join(json_samples, "test_change_check_size.json"),
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
            data_json,
        ],
    )

    with open(expected_path, "rb") as f1, open(output_path, "rb") as f2:
        expected = f1.read()
        actual = f2.read()

        assert len(expected) == len(actual)
        assert expected == actual


@pytest.mark.cli_test
def test_change_dropdown_choices(pdf_samples, static_pdfs, json_samples, tmp_path):
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
            os.path.join(json_samples, "test_change_dropdown_choices.json"),
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
    pdf_samples, static_pdfs, json_samples, tmp_path
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
                json_samples, "test_change_dropdown_choices_with_export_values.json"
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


@pytest.mark.posix_only
@pytest.mark.cli_test
def test_change_dropdown_font(pdf_samples, static_pdfs, json_samples, tmp_path):
    expected_path = os.path.join(pdf_samples, "docs", "test_change_dropdown_font.pdf")
    output_path = os.path.join(tmp_path, "output.pdf")

    result = runner.invoke(
        cli_app,
        [
            "update",
            "field",
            os.path.join(static_pdfs, "sample_template_with_dropdown.pdf"),
            "-f",
            os.path.join(json_samples, "test_change_dropdown_font.json"),
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
def test_change_dropdown_font_size(pdf_samples, static_pdfs, json_samples, tmp_path):
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
            os.path.join(json_samples, "test_change_dropdown_font_size.json"),
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
def test_change_dropdown_font_color(pdf_samples, static_pdfs, json_samples, tmp_path):
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
            os.path.join(json_samples, "test_change_dropdown_font_color.json"),
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
def test_change_field_editability(pdf_samples, static_pdfs, json_samples, tmp_path):
    expected_path = os.path.join(
        pdf_samples, "docs", "test_change_field_editability.pdf"
    )
    output_path = os.path.join(tmp_path, "output.pdf")
    data_json = os.path.join(tmp_path, "data.json")
    with open(data_json, "w", encoding="utf-8") as f:
        json.dump(
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
            data_json,
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
            os.path.join(json_samples, "test_change_field_editability.json"),
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
def test_change_field_visibility(pdf_samples, static_pdfs, json_samples, tmp_path):
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
            os.path.join(json_samples, "test_change_field_visibility.json"),
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
