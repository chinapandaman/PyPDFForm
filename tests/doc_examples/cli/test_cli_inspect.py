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
        "additionalProperties": True,
    }


@pytest.mark.cli_test
def test_data(static_pdfs):
    result = runner.invoke(
        cli_app,
        [
            "inspect",
            "data",
            os.path.join(static_pdfs, "sample_template_filled.pdf"),
        ],
    )
    assert result.exit_code == 0

    assert json.loads(result.output) == {
        "check": True,
        "check_2": True,
        "check_3": True,
        "test": "test",
        "test_2": "test2",
        "test_3": "test3",
    }


@pytest.mark.cli_test
def test_sample_data(static_pdfs):
    result = runner.invoke(
        cli_app,
        [
            "inspect",
            "sample",
            os.path.join(static_pdfs, "sample_template.pdf"),
        ],
    )
    assert result.exit_code == 0

    assert json.loads(result.output) == {
        "check": True,
        "check_2": True,
        "check_3": True,
        "test": "test",
        "test_2": "test_2",
        "test_3": "test_3",
    }
