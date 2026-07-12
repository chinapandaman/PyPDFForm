# -*- coding: utf-8 -*-


import os

import pytest
import yaml
from typer.testing import CliRunner

from PyPDFForm.cli.root import cli_app

runner = CliRunner()


@pytest.mark.cli_test
def test_create_raw_dynamic_options(static_pdfs, tmp_path):
    data_path = os.path.join(tmp_path, "data.yaml")
    file_output_path = os.path.join(tmp_path, "file-output.pdf")
    options_output_path = os.path.join(tmp_path, "options-output.pdf")
    with open(data_path, "w", encoding="utf-8") as f:
        yaml.safe_dump(
            {
                "rectangle": [
                    {
                        "page_number": 1,
                        "x": 100,
                        "y": 100,
                        "width": 200,
                        "height": 100,
                    }
                ]
            },
            f,
        )

    base_args = [
        "create",
        "raw",
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
            "rectangle",
            "--page_number",
            "1",
            "--x",
            "100",
            "--y",
            "100",
            "--width",
            "200",
            "--height",
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
def test_draw_text(pdf_samples, static_pdfs, yaml_samples, tmp_path):
    expected_path = os.path.join(pdf_samples, "docs", "test_draw_text.pdf")
    output_path = os.path.join(tmp_path, "output.pdf")

    result = runner.invoke(
        cli_app,
        [
            "create",
            "raw",
            os.path.join(static_pdfs, "sample_template.pdf"),
            "-f",
            os.path.join(yaml_samples, "test_draw_text.yaml"),
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
def test_draw_image(pdf_samples, static_pdfs, yaml_samples, tmp_path):
    expected_path = os.path.join(pdf_samples, "docs", "test_draw_image.pdf")
    output_path = os.path.join(tmp_path, "output.pdf")

    result = runner.invoke(
        cli_app,
        [
            "create",
            "raw",
            os.path.join(static_pdfs, "sample_template.pdf"),
            "-f",
            os.path.join(yaml_samples, "test_draw_image.yaml"),
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
def test_draw_line(pdf_samples, static_pdfs, yaml_samples, tmp_path):
    expected_path = os.path.join(pdf_samples, "docs", "test_draw_line.pdf")
    output_path = os.path.join(tmp_path, "output.pdf")

    result = runner.invoke(
        cli_app,
        [
            "create",
            "raw",
            os.path.join(static_pdfs, "sample_template.pdf"),
            "-f",
            os.path.join(yaml_samples, "test_draw_line.yaml"),
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
def test_draw_rect(pdf_samples, static_pdfs, yaml_samples, tmp_path):
    expected_path = os.path.join(pdf_samples, "docs", "test_draw_rect.pdf")
    output_path = os.path.join(tmp_path, "output.pdf")

    result = runner.invoke(
        cli_app,
        [
            "create",
            "raw",
            os.path.join(static_pdfs, "sample_template.pdf"),
            "-f",
            os.path.join(yaml_samples, "test_draw_rect.yaml"),
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
def test_draw_circle(pdf_samples, static_pdfs, yaml_samples, tmp_path):
    expected_path = os.path.join(pdf_samples, "docs", "test_draw_circle.pdf")
    output_path = os.path.join(tmp_path, "output.pdf")

    result = runner.invoke(
        cli_app,
        [
            "create",
            "raw",
            os.path.join(static_pdfs, "sample_template.pdf"),
            "-f",
            os.path.join(yaml_samples, "test_draw_circle.yaml"),
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
def test_draw_ellipse(pdf_samples, static_pdfs, yaml_samples, tmp_path):
    expected_path = os.path.join(pdf_samples, "docs", "test_draw_ellipse.pdf")
    output_path = os.path.join(tmp_path, "output.pdf")

    result = runner.invoke(
        cli_app,
        [
            "create",
            "raw",
            os.path.join(static_pdfs, "sample_template.pdf"),
            "-f",
            os.path.join(yaml_samples, "test_draw_ellipse.yaml"),
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
