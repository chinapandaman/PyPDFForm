# -*- coding: utf-8 -*-

import os

import pytest
from typer.testing import CliRunner

from PyPDFForm.cli.root import cli_app

runner = CliRunner()


@pytest.mark.cli_test
def test_js_adapting(expected_pdfs, static_pdfs, yaml_samples, tmp_path, expect_pdf):
    expected_path = os.path.join(
        expected_pdfs, "doc_examples", "lib", "test_acro_js", "test_js_adapting.pdf"
    )
    output_path = os.path.join(tmp_path, "output.pdf")

    result = runner.invoke(
        cli_app,
        [
            "update",
            "field",
            os.path.join(static_pdfs, "sample_template.pdf"),
            "-f",
            os.path.join(yaml_samples, "test_js_adapting.yaml"),
            "-o",
            output_path,
        ],
    )
    assert result.exit_code == 0

    with open(output_path, "rb") as f2:
        actual = f2.read()

        expect_pdf(actual, same_as=expected_path)


@pytest.mark.cli_test
def test_on_hover(expected_pdfs, static_pdfs, yaml_samples, tmp_path, expect_pdf):
    expected_path = os.path.join(
        expected_pdfs, "doc_examples", "lib", "test_acro_js", "test_on_hover.pdf"
    )
    output_path = os.path.join(tmp_path, "output.pdf")

    result = runner.invoke(
        cli_app,
        [
            "update",
            "field",
            os.path.join(static_pdfs, "sample_template.pdf"),
            "-f",
            os.path.join(yaml_samples, "test_on_hover.yaml"),
            "-o",
            output_path,
        ],
    )
    assert result.exit_code == 0

    with open(output_path, "rb") as f2:
        actual = f2.read()

        expect_pdf(actual, same_as=expected_path)


@pytest.mark.cli_test
def test_off_hover(expected_pdfs, static_pdfs, yaml_samples, tmp_path, expect_pdf):
    expected_path = os.path.join(
        expected_pdfs, "doc_examples", "lib", "test_acro_js", "test_off_hover.pdf"
    )
    output_path = os.path.join(tmp_path, "output.pdf")

    result = runner.invoke(
        cli_app,
        [
            "update",
            "field",
            os.path.join(static_pdfs, "sample_template.pdf"),
            "-f",
            os.path.join(yaml_samples, "test_off_hover.yaml"),
            "-o",
            output_path,
        ],
    )
    assert result.exit_code == 0

    with open(output_path, "rb") as f2:
        actual = f2.read()

        expect_pdf(actual, same_as=expected_path)


@pytest.mark.cli_test
def test_mouse_pressed(expected_pdfs, static_pdfs, yaml_samples, tmp_path, expect_pdf):
    expected_path = os.path.join(
        expected_pdfs, "doc_examples", "lib", "test_acro_js", "test_mouse_pressed.pdf"
    )
    output_path = os.path.join(tmp_path, "output.pdf")

    result = runner.invoke(
        cli_app,
        [
            "update",
            "field",
            os.path.join(static_pdfs, "sample_template.pdf"),
            "-f",
            os.path.join(yaml_samples, "test_mouse_pressed.yaml"),
            "-o",
            output_path,
        ],
    )
    assert result.exit_code == 0

    with open(output_path, "rb") as f2:
        actual = f2.read()

        expect_pdf(actual, same_as=expected_path)


@pytest.mark.cli_test
def test_mouse_released(expected_pdfs, static_pdfs, yaml_samples, tmp_path, expect_pdf):
    expected_path = os.path.join(
        expected_pdfs, "doc_examples", "lib", "test_acro_js", "test_mouse_released.pdf"
    )
    output_path = os.path.join(tmp_path, "output.pdf")

    result = runner.invoke(
        cli_app,
        [
            "update",
            "field",
            os.path.join(static_pdfs, "sample_template.pdf"),
            "-f",
            os.path.join(yaml_samples, "test_mouse_released.yaml"),
            "-o",
            output_path,
        ],
    )
    assert result.exit_code == 0

    with open(output_path, "rb") as f2:
        actual = f2.read()

        expect_pdf(actual, same_as=expected_path)


@pytest.mark.cli_test
def test_on_focused(expected_pdfs, static_pdfs, yaml_samples, tmp_path, expect_pdf):
    expected_path = os.path.join(
        expected_pdfs, "doc_examples", "lib", "test_acro_js", "test_on_focused.pdf"
    )
    output_path = os.path.join(tmp_path, "output.pdf")

    result = runner.invoke(
        cli_app,
        [
            "update",
            "field",
            os.path.join(static_pdfs, "sample_template.pdf"),
            "-f",
            os.path.join(yaml_samples, "test_on_focused.yaml"),
            "-o",
            output_path,
        ],
    )
    assert result.exit_code == 0

    with open(output_path, "rb") as f2:
        actual = f2.read()

        expect_pdf(actual, same_as=expected_path)


@pytest.mark.cli_test
def test_off_focused(expected_pdfs, static_pdfs, yaml_samples, tmp_path, expect_pdf):
    expected_path = os.path.join(
        expected_pdfs, "doc_examples", "lib", "test_acro_js", "test_off_focused.pdf"
    )
    output_path = os.path.join(tmp_path, "output.pdf")

    result = runner.invoke(
        cli_app,
        [
            "update",
            "field",
            os.path.join(static_pdfs, "sample_template.pdf"),
            "-f",
            os.path.join(yaml_samples, "test_off_focused.yaml"),
            "-o",
            output_path,
        ],
    )
    assert result.exit_code == 0

    with open(output_path, "rb") as f2:
        actual = f2.read()

        expect_pdf(actual, same_as=expected_path)


@pytest.mark.cli_test
def test_on_open(expected_pdfs, static_pdfs, js_samples, tmp_path, expect_pdf):
    expected_path = os.path.join(
        expected_pdfs, "doc_examples", "lib", "test_acro_js", "test_on_open.pdf"
    )
    output_path = os.path.join(tmp_path, "output.pdf")

    result = runner.invoke(
        cli_app,
        [
            "update",
            "script",
            os.path.join(static_pdfs, "sample_template.pdf"),
            "-s",
            os.path.join(js_samples, "doc_examples", "test_on_open.js"),
            "-o",
            output_path,
        ],
    )
    assert result.exit_code == 0

    with open(output_path, "rb") as f2:
        actual = f2.read()

        expect_pdf(actual, same_as=expected_path)
