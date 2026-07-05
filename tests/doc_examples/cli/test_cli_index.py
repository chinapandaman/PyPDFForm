# -*- coding: utf-8 -*-

import json
import os

import pytest
from typer.testing import CliRunner

from PyPDFForm.cli.root import cli_app

runner = CliRunner()


@pytest.mark.requires_zlib_over_zlib_ng
@pytest.mark.cli_test
def test_index_snippets(pdf_samples, yaml_samples, tmp_path):
    expected_path = os.path.join(pdf_samples, "docs", "test_index_snippets.pdf")
    output_path = os.path.join(tmp_path, "output.pdf")

    runner.invoke(cli_app, ["create", "blank", "-o", output_path])

    runner.invoke(
        cli_app,
        [
            "create",
            "raw",
            output_path,
            "-f",
            os.path.join(yaml_samples, "landing_doc_examples", "labels.yaml"),
        ],
    )

    runner.invoke(
        cli_app,
        [
            "create",
            "field",
            output_path,
            "-f",
            os.path.join(yaml_samples, "landing_doc_examples", "fields.yaml"),
        ],
    )

    inspect_result = runner.invoke(cli_app, ["inspect", "schema", output_path])
    assert inspect_result.exit_code == 0
    inspect_result = json.loads(inspect_result.output)
    assert inspect_result["properties"]["my_textfield"]["type"] == "string"
    assert inspect_result["properties"]["my_checkbox"]["type"] == "boolean"

    runner.invoke(
        cli_app,
        [
            "update",
            "field",
            output_path,
            "-f",
            os.path.join(yaml_samples, "landing_doc_examples", "styles.yaml"),
        ],
    )

    runner.invoke(
        cli_app,
        [
            "fill",
            output_path,
            "-f",
            os.path.join(yaml_samples, "landing_doc_examples", "data.yaml"),
        ],
    )

    with open(expected_path, "rb") as f1, open(output_path, "rb") as f2:
        expected = f1.read()
        actual = f2.read()

        assert len(expected) == len(actual)
        assert expected == actual
