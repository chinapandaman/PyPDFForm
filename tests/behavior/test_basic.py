# -*- coding: utf-8 -*-

import os
import stat
from contextlib import contextmanager
from io import BytesIO
from pathlib import Path

import pytest
from pikepdf import Pdf
from pypdf import PdfReader
from typer.testing import CliRunner

from PyPDFForm import PdfWrapper
from PyPDFForm.cli.root import cli_app
from PyPDFForm.lib import egress
from PyPDFForm.lib.constants import V
from PyPDFForm.lib.deprecation import deprecation_notice


def test_deprecation_warning():
    class MockClass:
        @deprecation_notice(to_replace="new_method")
        def old_method(self):
            return "result"

    obj = MockClass()
    with pytest.warns(
        DeprecationWarning,
        match="MockClass.old_method will be deprecated soon. Use MockClass.new_method instead.",
    ):
        assert obj.old_method() == "result"


def test_deprecation_warning_with_param():
    class MockClass:
        @deprecation_notice(to_replace="old_method.new_param", param="old_param")
        def old_method(self):
            return "result"

    obj = MockClass()
    with pytest.warns(
        DeprecationWarning,
        match="MockClass.old_method.old_param will be deprecated soon. Use MockClass.old_method.new_param instead.",
    ):
        assert obj.old_method() == "result"


def test_deprecation_warning_empty_replace():
    class MockClass:
        @deprecation_notice(to_replace="")
        def old_method(self):
            return "result"

    obj = MockClass()
    with pytest.warns(
        DeprecationWarning,
        match="MockClass.old_method will be deprecated soon.",
    ) as record:
        assert obj.old_method() == "result"
    assert "Use" not in str(record[0].message)


def test_deprecation_warning_direct_call():
    class MockClass:
        def my_method(self, use_legacy=False):
            if use_legacy:
                deprecation_notice(to_replace="", param="use_legacy").emit_notice(
                    self, "my_method"
                )
            return "result"

    obj = MockClass()
    assert obj.my_method(use_legacy=False) == "result"
    with pytest.warns(
        DeprecationWarning,
        match="MockClass.my_method.use_legacy will be deprecated soon.",
    ):
        assert obj.my_method(use_legacy=True) == "result"


def test_deprecation_warning_direct_call_with_replace():
    class MockClass:
        def my_method(self, use_legacy=False):
            if use_legacy:
                deprecation_notice(
                    to_replace="my_method.new_param", param="use_legacy"
                ).emit_notice(self, "my_method")
            return "result"

    obj = MockClass()
    with pytest.warns(
        DeprecationWarning,
        match="MockClass.my_method.use_legacy will be deprecated soon. Use MockClass.my_method.new_param instead.",
    ):
        assert obj.my_method(use_legacy=True) == "result"


def test_write(template_stream, tmp_path):
    destination = tmp_path / "sample_template.pdf"
    obj = PdfWrapper(template_stream).fill({"test": "transactional"})
    assert obj.write(str(destination)) is obj
    assert PdfWrapper(str(destination)).data["test"] == "transactional"
    fields = PdfReader(str(destination)).get_fields()
    assert fields is not None
    assert fields["test"][V] == "transactional"
    with Pdf.open(destination) as reopened:
        assert not reopened.check_pdf_syntax()
    if os.name != "nt":
        assert stat.S_IMODE(destination.stat().st_mode) == 0o600
        destination.chmod(0o640)

    expected = obj.read()
    assert obj.write(os.fsencode(destination)) is obj
    assert destination.read_bytes() == expected
    if os.name != "nt":
        assert stat.S_IMODE(destination.stat().st_mode) == 0o640
    with pytest.raises(OSError, match="regular file"):
        obj.write(tmp_path)
    assert set(tmp_path.iterdir()) == {destination}


@pytest.mark.parametrize("failure", ["hook", "appearance", "write", "close", "replace"])
@pytest.mark.parametrize(
    "operation",
    [
        "library",
        pytest.param("cli_in_place", marks=pytest.mark.cli_test),
        pytest.param("cli_output", marks=pytest.mark.cli_test),
    ],
)
def test_write_failure_preserves_destination(
    template_stream, tmp_path, monkeypatch, failure, operation
):
    source = tmp_path / "input.pdf"
    source.write_bytes(template_stream)
    destination = source if operation == "cli_in_place" else tmp_path / "output.pdf"
    if destination != source:
        destination.write_bytes(b"existing output")
    original = destination.read_bytes()
    original_entries = set(tmp_path.iterdir())
    error = OSError(f"injected {failure} failure")

    def fail(*_args):
        raise error

    if failure == "hook":
        monkeypatch.setattr("PyPDFForm.lib.hooks.update_text_field_font_size", fail)
    elif failure == "appearance":
        egress.appearance_streams_handler.cache_clear()
        monkeypatch.setattr(Pdf, "generate_appearance_streams", fail)
    elif failure in ("write", "close"):
        temporary_file = egress.NamedTemporaryFile

        @contextmanager
        def failing_temporary_file(**kwargs):
            with temporary_file(**kwargs) as temporary:
                if failure == "write":
                    real_write = temporary.write
                    monkeypatch.setattr(
                        temporary, "write", lambda content: real_write(content[:10])
                    )
                else:
                    monkeypatch.setattr(temporary.file, "flush", fail)
                yield temporary

        monkeypatch.setattr(egress, "NamedTemporaryFile", failing_temporary_file)
    else:
        monkeypatch.setattr(egress.os, "replace", fail)
        real_unlink = os.unlink

        def readonly_unlink(path):
            # Exercise cleanup when Windows treats the temporary file as read-only.
            monkeypatch.setattr(egress.os, "unlink", real_unlink)
            raise PermissionError(path)

        monkeypatch.setattr(egress.os, "unlink", readonly_unlink)

    if operation == "library":
        obj = PdfWrapper(template_stream, generate_appearance_streams=True)
        obj.widgets["test"].font_size = 14
        with pytest.raises(OSError, match="injected|incomplete"):
            obj.write(destination)
    else:
        args = [
            "--generate-appearance-streams",
            "update",
            "field",
            str(source),
            "--field",
            "test",
            "--font_size",
            "14",
        ]
        if operation == "cli_output":
            args.extend(["-o", str(destination)])
        result = CliRunner().invoke(cli_app, args)
        assert result.exit_code == 1
        assert isinstance(result.exception, OSError)

    assert destination.read_bytes() == original
    assert source.read_bytes() == template_stream
    assert set(tmp_path.iterdir()) == original_entries


def test_write_follows_symlink(template_stream, tmp_path):
    directory = tmp_path / "targets"
    directory.mkdir()
    target = directory / "output.pdf"
    symlink = tmp_path / "link.pdf"
    try:
        symlink.symlink_to("targets/output.pdf")
    except OSError:
        pytest.skip("Creating symlinks requires platform support and permissions")

    obj = PdfWrapper(template_stream).fill({"test": "first output"})
    obj.write(symlink)
    original = target.read_bytes()
    other_link = directory / "other.pdf"
    os.link(target, other_link)
    obj.fill({"test": "second output"}).write(symlink)

    assert symlink.is_symlink()
    assert os.readlink(symlink) == "targets/output.pdf"
    assert PdfWrapper(str(target)).data["test"] == "second output"
    assert other_link.read_bytes() == original
    assert not os.path.samefile(target, other_link)
    assert set(directory.iterdir()) == {target, other_link}


def test_write_io(template_stream):
    buff = BytesIO()
    obj = PdfWrapper(template_stream)
    obj.write(buff)
    buff.seek(0)

    assert PdfWrapper(buff.read()).widgets.keys() == obj.widgets.keys()


@pytest.mark.parametrize(
    ("kwargs", "match"),
    [
        (
            {"flatten": True},
            r"'flatten'\. It was removed in PyPDFForm 6\.0\.0\. Use readonly=True",
        ),
        ({"flatten": False}, r"'flatten'\. It was removed in PyPDFForm 6\.0\.0\."),
        ({"read_only": True}, r"'read_only'\. Supported keyword arguments: readonly\."),
    ],
)
def test_fill_rejects_unsupported_kwargs(template_stream, data_dict, kwargs, match):
    obj = PdfWrapper(template_stream)
    original = obj.read()
    original_data = obj.data

    with pytest.raises(TypeError, match=r"^PdfWrapper\.fill\(\) got .*" + match):
        obj.fill(data_dict, **kwargs)

    assert obj.read() == original
    assert obj.data == original_data
    assert not any(
        widget.readonly for widget in PdfWrapper(obj.read()).widgets.values()
    )


@pytest.mark.parametrize(
    ("kwargs", "match"),
    [
        (
            {"preserve_metadata": True},
            r"'preserve_metadata'\. It was removed in PyPDFForm 6\.0\.0\. Remove it",
        ),
        (
            {"use_full_widget_names": True},
            (
                r"'use_full_widget_names'\. Supported keyword arguments: "
                r"use_full_widget_name, need_appearances, generate_appearance_streams, title\."
            ),
        ),
    ],
)
def test_init_rejects_unsupported_kwargs(template_stream, kwargs, match):
    with pytest.raises(TypeError, match=r"^PdfWrapper\(\) got .*" + match):
        PdfWrapper(template_stream, **kwargs)


def test_template_inputs(template_stream, pdf_samples, tmp_path):
    expected = PdfWrapper(template_stream).read()
    obj = PdfWrapper(Path(pdf_samples) / "sample_template.pdf")
    assert obj.read() == expected
    assert obj.widgets.keys() == PdfWrapper(template_stream).widgets.keys()

    for obj in (PdfWrapper(), PdfWrapper(b""), PdfWrapper(BytesIO())):
        assert obj.read() == b""
        assert obj.widgets == {}

    for missing in (str(tmp_path / "missing.pdf"), tmp_path / "missing.pdf"):
        with pytest.raises(FileNotFoundError):
            PdfWrapper(missing)
    # Windows reports opening a directory as PermissionError
    with pytest.raises((IsADirectoryError, PermissionError)):
        PdfWrapper(str(tmp_path))
    for unsupported in (None, 123):
        with pytest.raises(TypeError, match="readable binary stream, got"):
            PdfWrapper(unsupported)


def test_register_bad_fonts(tmp_path):
    assert not PdfWrapper().register_font("foo", b"foo").read()
    with pytest.raises(FileNotFoundError):
        PdfWrapper().register_font("foo", str(tmp_path / "missing.ttf"))

    obj = PdfWrapper().register_font("foo", b"foo")
    assert "foo" not in obj.fonts
