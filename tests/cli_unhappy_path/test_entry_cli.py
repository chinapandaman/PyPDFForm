# -*- coding: utf-8 -*-

import pytest

from PyPDFForm.cli_entry import main


@pytest.mark.cli_test
def test_entrypoint_missing_cli_dependency(monkeypatch, capsys):
    def missing_cli_dependency(module_name):
        message = "No module named 'typer'"
        raise ModuleNotFoundError(
            message,
            name="typer",
        )

    monkeypatch.setattr(
        "PyPDFForm.cli_entry.importlib.import_module",
        missing_cli_dependency,
    )

    with pytest.raises(SystemExit) as exc_info:
        main()

    captured = capsys.readouterr()

    assert exc_info.value.code == 1
    assert "PyPDFForm CLI dependencies are not installed" in captured.err
    assert "pip install 'PyPDFForm[cli]'" in captured.err
