# -*- coding: utf-8 -*-

import os

import pytest
from typer.testing import CliRunner

from PyPDFForm import __version__
from PyPDFForm.cli import cli_app

runner = CliRunner()


@pytest.mark.cli_test
def test_root_command():
    result = runner.invoke(cli_app)
    assert result.exit_code == 2

    assert "Create, fill, inspect, and update PDF forms." in result.output
    assert "Usage:" in result.output
    assert "main" not in result.output


@pytest.mark.cli_test
def test_root_command_with_version():
    long = runner.invoke(cli_app, ["--version"])
    short = runner.invoke(cli_app, ["-v"])

    assert long.exit_code == 0
    assert short.exit_code == 0

    assert long.output == f"v{__version__}\n"
    assert long.output == short.output


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

    assert result.exit_code == 2
    assert "does not exist" in result.output
