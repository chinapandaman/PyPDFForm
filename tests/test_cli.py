# -*- coding: utf-8 -*-

import pytest
from typer.testing import CliRunner

from PyPDFForm import __version__
from PyPDFForm.cli import cli_app

runner = CliRunner()


@pytest.mark.cli_test
def test_root_command():
    result = runner.invoke(cli_app)
    assert result.exit_code == 2

    assert "PyPDFForm command-line interface." in result.output
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
def test_coordinate_command():
    result = runner.invoke(cli_app, ["coordinate"])
    assert result.exit_code == 2

    assert "Usage:" in result.output


@pytest.mark.cli_test
def test_update_command():
    result = runner.invoke(cli_app, ["update"])
    assert result.exit_code == 2

    assert "Usage:" in result.output
