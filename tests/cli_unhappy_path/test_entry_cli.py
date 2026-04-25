# -*- coding: utf-8 -*-

from types import SimpleNamespace

import pytest

from PyPDFForm.cli.entry import main


@pytest.mark.cli_test
def test_entrypoint_missing_cli_dependency(monkeypatch, capsys):
    def missing_cli_dependency(module_name):
        message = "No module named 'typer'"
        raise ModuleNotFoundError(
            message,
            name="typer",
        )

    monkeypatch.setattr(
        "PyPDFForm.cli.entry.importlib.import_module",
        missing_cli_dependency,
    )

    with pytest.raises(SystemExit) as exc_info:
        main()

    captured = capsys.readouterr()

    assert exc_info.value.code == 1
    assert "PyPDFForm CLI dependencies are not installed" in captured.err
    assert "pip install 'PyPDFForm[cli]'" in captured.err


@pytest.mark.cli_test
def test_entrypoint_reraises_non_cli_dependency(monkeypatch, capsys):
    def missing_non_cli_dependency(module_name):
        message = "No module named 'missing_dependency'"
        raise ModuleNotFoundError(
            message,
            name="missing_dependency",
        )

    monkeypatch.setattr(
        "PyPDFForm.cli.entry.importlib.import_module",
        missing_non_cli_dependency,
    )

    with pytest.raises(ModuleNotFoundError) as exc_info:
        main()

    captured = capsys.readouterr()

    assert exc_info.value.name == "missing_dependency"
    assert captured.err == ""


@pytest.mark.cli_test
def test_entrypoint_runs_cli_app(monkeypatch):
    state = {"called": False}

    def cli_app():
        state["called"] = True

    def import_cli_module(module_name):
        assert module_name == "PyPDFForm.cli.root"
        return SimpleNamespace(cli_app=cli_app)

    monkeypatch.setattr(
        "PyPDFForm.cli.entry.importlib.import_module",
        import_cli_module,
    )

    main()

    assert state["called"]
