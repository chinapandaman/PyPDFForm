# -*- coding: utf-8 -*-

import pytest
from typer.testing import CliRunner

from PyPDFForm import __version__
from PyPDFForm.cli.root import cli_app

runner = CliRunner()


@pytest.mark.cli_test
def test_get_version():
    long = runner.invoke(cli_app, ["--version"])
    short = runner.invoke(cli_app, ["-v"])

    assert long.exit_code == 0
    assert short.exit_code == 0

    assert long.output == f"v{__version__}\n"
    assert long.output == short.output
