# -*- coding: utf-8 -*-


import os

import pytest
import yaml
from typer.testing import CliRunner

from PyPDFForm.cli.root import cli_app

runner = CliRunner()


@pytest.mark.cli_test
def test_create_annotation_dynamic_options(static_pdfs, tmp_path):
    data_path = os.path.join(tmp_path, "data.yaml")
    file_output_path = os.path.join(tmp_path, "file-output.pdf")
    options_output_path = os.path.join(tmp_path, "options-output.pdf")
    with open(data_path, "w", encoding="utf-8") as f:
        yaml.safe_dump(
            {
                "link": [
                    {
                        "page_number": 1,
                        "x": 70,
                        "y": 705,
                        "width": 95,
                        "height": 20,
                        "page": 2,
                    }
                ]
            },
            f,
        )

    base_args = [
        "create",
        "annotation",
        os.path.join(static_pdfs, "sample_template.pdf"),
    ]
    file_result = runner.invoke(
        cli_app, [*base_args, "-f", data_path, "-o", file_output_path]
    )
    options_result = runner.invoke(
        cli_app,
        [
            *base_args,
            "--type",
            "link",
            "--page_number",
            "1",
            "--x",
            "70",
            "--y",
            "705",
            "--width",
            "95",
            "--height",
            "20",
            "--page",
            "2",
            "-o",
            options_output_path,
        ],
    )

    assert file_result.exit_code == 0
    assert options_result.exit_code == 0
    with open(file_output_path, "rb") as f1, open(options_output_path, "rb") as f2:
        assert f1.read() == f2.read()


@pytest.mark.cli_test
def test_text_annotations(pdf_samples, static_pdfs, yaml_samples, tmp_path):
    expected_path = os.path.join(pdf_samples, "docs", "test_text_annotations.pdf")
    output_path = os.path.join(tmp_path, "output.pdf")

    result = runner.invoke(
        cli_app,
        [
            "create",
            "annotation",
            os.path.join(static_pdfs, "sample_template.pdf"),
            "-f",
            os.path.join(yaml_samples, "test_text_annotations.yaml"),
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
def test_uri_link_annotations(pdf_samples, static_pdfs, yaml_samples, tmp_path):
    expected_path = os.path.join(pdf_samples, "docs", "test_uri_link_annotations.pdf")
    output_path = os.path.join(tmp_path, "output.pdf")

    result = runner.invoke(
        cli_app,
        [
            "create",
            "annotation",
            os.path.join(static_pdfs, "sample_template.pdf"),
            "-f",
            os.path.join(yaml_samples, "test_uri_link_annotations.yaml"),
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
def test_page_link_annotations(pdf_samples, static_pdfs, yaml_samples, tmp_path):
    expected_path = os.path.join(pdf_samples, "docs", "test_page_link_annotations.pdf")
    output_path = os.path.join(tmp_path, "output.pdf")

    result = runner.invoke(
        cli_app,
        [
            "create",
            "annotation",
            os.path.join(static_pdfs, "sample_template.pdf"),
            "-f",
            os.path.join(yaml_samples, "test_page_link_annotations.yaml"),
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
def test_highlight_annotations(pdf_samples, static_pdfs, yaml_samples, tmp_path):
    expected_path = os.path.join(pdf_samples, "docs", "test_highlight_annotations.pdf")
    output_path = os.path.join(tmp_path, "output.pdf")

    result = runner.invoke(
        cli_app,
        [
            "create",
            "annotation",
            os.path.join(static_pdfs, "sample_template.pdf"),
            "-f",
            os.path.join(yaml_samples, "test_highlight_annotations.yaml"),
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
def test_underline_annotations(pdf_samples, static_pdfs, yaml_samples, tmp_path):
    expected_path = os.path.join(pdf_samples, "docs", "test_underline_annotations.pdf")
    output_path = os.path.join(tmp_path, "output.pdf")

    result = runner.invoke(
        cli_app,
        [
            "create",
            "annotation",
            os.path.join(static_pdfs, "sample_template.pdf"),
            "-f",
            os.path.join(yaml_samples, "test_underline_annotations.yaml"),
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
def test_squiggly_annotations(pdf_samples, static_pdfs, yaml_samples, tmp_path):
    expected_path = os.path.join(pdf_samples, "docs", "test_squiggly_annotations.pdf")
    output_path = os.path.join(tmp_path, "output.pdf")

    result = runner.invoke(
        cli_app,
        [
            "create",
            "annotation",
            os.path.join(static_pdfs, "sample_template.pdf"),
            "-f",
            os.path.join(yaml_samples, "test_squiggly_annotations.yaml"),
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
def test_strikeout_annotations(pdf_samples, static_pdfs, yaml_samples, tmp_path):
    expected_path = os.path.join(pdf_samples, "docs", "test_strikeout_annotations.pdf")
    output_path = os.path.join(tmp_path, "output.pdf")

    result = runner.invoke(
        cli_app,
        [
            "create",
            "annotation",
            os.path.join(static_pdfs, "sample_template.pdf"),
            "-f",
            os.path.join(yaml_samples, "test_strikeout_annotations.yaml"),
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
def test_rubber_stamp_annotations(pdf_samples, static_pdfs, yaml_samples, tmp_path):
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
            os.path.join(yaml_samples, "test_rubber_stamp_annotations.yaml"),
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
