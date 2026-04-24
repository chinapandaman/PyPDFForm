# -*- coding: utf-8 -*-

import os

import pytest
from typer.testing import CliRunner

from PyPDFForm.cli import cli_app

runner = CliRunner()


@pytest.mark.cli_test
def test_js_adapting(pdf_samples, static_pdfs, json_samples, tmp_path):
    expected_path = os.path.join(pdf_samples, "docs", "test_js_adapting.pdf")
    output_path = os.path.join(tmp_path, "output.pdf")

    result = runner.invoke(
        cli_app,
        [
            "update",
            "field",
            os.path.join(static_pdfs, "sample_template.pdf"),
            "-f",
            os.path.join(json_samples, "test_js_adapting.json"),
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
def test_on_hover(pdf_samples, static_pdfs, json_samples, tmp_path):
    expected_path = os.path.join(pdf_samples, "docs", "test_on_hover.pdf")
    output_path = os.path.join(tmp_path, "output.pdf")

    result = runner.invoke(
        cli_app,
        [
            "update",
            "field",
            os.path.join(static_pdfs, "sample_template.pdf"),
            "-f",
            os.path.join(json_samples, "test_on_hover.json"),
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
def test_off_hover(pdf_samples, static_pdfs, json_samples, tmp_path):
    expected_path = os.path.join(pdf_samples, "docs", "test_off_hover.pdf")
    output_path = os.path.join(tmp_path, "output.pdf")

    result = runner.invoke(
        cli_app,
        [
            "update",
            "field",
            os.path.join(static_pdfs, "sample_template.pdf"),
            "-f",
            os.path.join(json_samples, "test_off_hover.json"),
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
def test_mouse_pressed(pdf_samples, static_pdfs, json_samples, tmp_path):
    expected_path = os.path.join(pdf_samples, "docs", "test_mouse_pressed.pdf")
    output_path = os.path.join(tmp_path, "output.pdf")

    result = runner.invoke(
        cli_app,
        [
            "update",
            "field",
            os.path.join(static_pdfs, "sample_template.pdf"),
            "-f",
            os.path.join(json_samples, "test_mouse_pressed.json"),
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
def test_mouse_released(pdf_samples, static_pdfs, json_samples, tmp_path):
    expected_path = os.path.join(pdf_samples, "docs", "test_mouse_released.pdf")
    output_path = os.path.join(tmp_path, "output.pdf")

    result = runner.invoke(
        cli_app,
        [
            "update",
            "field",
            os.path.join(static_pdfs, "sample_template.pdf"),
            "-f",
            os.path.join(json_samples, "test_mouse_released.json"),
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
def test_on_focused(pdf_samples, static_pdfs, json_samples, tmp_path):
    expected_path = os.path.join(pdf_samples, "docs", "test_on_focused.pdf")
    output_path = os.path.join(tmp_path, "output.pdf")

    result = runner.invoke(
        cli_app,
        [
            "update",
            "field",
            os.path.join(static_pdfs, "sample_template.pdf"),
            "-f",
            os.path.join(json_samples, "test_on_focused.json"),
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
def test_off_focused(pdf_samples, static_pdfs, json_samples, tmp_path):
    expected_path = os.path.join(pdf_samples, "docs", "test_off_focused.pdf")
    output_path = os.path.join(tmp_path, "output.pdf")

    result = runner.invoke(
        cli_app,
        [
            "update",
            "field",
            os.path.join(static_pdfs, "sample_template.pdf"),
            "-f",
            os.path.join(json_samples, "test_off_focused.json"),
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
def test_on_open(pdf_samples, static_pdfs, js_samples, tmp_path):
    expected_path = os.path.join(pdf_samples, "docs", "test_on_open.pdf")
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

    with open(expected_path, "rb") as f1, open(output_path, "rb") as f2:
        expected = f1.read()
        actual = f2.read()

        assert len(expected) == len(actual)
        assert expected == actual
