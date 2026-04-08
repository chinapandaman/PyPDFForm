# -*- coding: utf-8 -*-

import os

from pypdf import PdfReader
from typer.testing import CliRunner

from PyPDFForm.cli import cli_app
from PyPDFForm.lib.constants import Title

runner = CliRunner()


def test_change_title(static_pdfs, tmp_path):
    output_path = os.path.join(tmp_path, "output.pdf")
    result = runner.invoke(
        cli_app,
        [
            "update",
            "title",
            os.path.join(static_pdfs, "sample_template.pdf"),
            "-t",
            "My PDF",
            "-o",
            output_path,
        ],
    )
    assert result.exit_code == 0

    reader = PdfReader(output_path)
    assert (reader.metadata or {}).get(Title) == "My PDF"
