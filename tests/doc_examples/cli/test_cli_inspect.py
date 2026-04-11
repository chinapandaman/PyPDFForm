# -*- coding: utf-8 -*-

import json
import os

import pytest
from typer.testing import CliRunner

from PyPDFForm.cli import cli_app

runner = CliRunner()


@pytest.mark.cli_test
def test_schema(static_pdfs):
    result = runner.invoke(
        cli_app,
        [
            "inspect",
            "schema",
            os.path.join(static_pdfs, "sample_template.pdf"),
        ],
    )
    assert result.exit_code == 0

    assert json.loads(result.output) == {
        "type": "object",
        "properties": {
            "test": {"type": "string"},
            "check": {"type": "boolean"},
            "test_2": {"type": "string"},
            "check_2": {"type": "boolean"},
            "test_3": {"type": "string"},
            "check_3": {"type": "boolean"},
        },
    }
