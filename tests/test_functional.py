# -*- coding: utf-8 -*-

import os
import stat
from contextlib import contextmanager
from copy import deepcopy
from io import BytesIO
from pathlib import Path
from unittest.mock import patch

import pytest
from jsonschema import ValidationError, validate
from pikepdf import Dictionary, Name, Pdf
from pypdf import PdfReader
from typer.testing import CliRunner

from PyPDFForm import (
    Annotations,
    BlankPage,
    Fields,
    PdfArray,
    PdfWrapper,
    RawElements,
)
from PyPDFForm.cli.root import cli_app
from PyPDFForm.lib import egress
from PyPDFForm.lib.constants import (
    DA,
    UNIQUE_SUFFIX_LENGTH,
    AcroForm,
    T,
    V,
)
from PyPDFForm.lib.constants import (
    Fields as FieldsConst,
)
from PyPDFForm.lib.deprecation import deprecation_notice
from PyPDFForm.lib.middleware.base import Widget
from PyPDFForm.lib.template import get_widget_key, get_widgets_by_page
from PyPDFForm.lib.utils import get_version, set_version


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


def test_base_schema_definition():
    assert Widget("foo").schema_definition == {}


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


def test_fill_readonly_then_editable(template_stream, pdf_samples, data_dict, request):
    expected_path = os.path.join(pdf_samples, "test_fill_readonly_then_editable.pdf")
    with open(expected_path, "rb+") as f:
        obj = PdfWrapper(template_stream).fill(data_dict, readonly=True)
        obj.widgets["test_2"].readonly = False
        obj.widgets["check_3"].readonly = False

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()
        assert len(obj.read()) == len(obj.read())
        assert obj.read() == obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


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


@pytest.mark.requires_zlib_over_zlib_ng
def test_fill_with_customized_widgets(
    template_stream, pdf_samples, sample_font_stream, data_dict, request
):
    expected_path = os.path.join(pdf_samples, "test_fill_with_customized_widgets.pdf")
    with open(
        expected_path,
        "rb+",
    ) as f:
        obj = PdfWrapper(template_stream).register_font(
            "new_font",
            sample_font_stream,
        )
        obj.widgets["test"].font = "new_font"
        obj.widgets["test"].font_size = 20
        obj.widgets["test"].font_color = (1, 0, 0)
        obj.widgets["test_2"].font_color = (0, 1, 0)
        obj.fill(
            data_dict,
        )

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


@pytest.mark.requires_zlib_over_zlib_ng
def test_fill_with_customized_widgets_readonly(
    template_stream, pdf_samples, sample_font_stream, data_dict, request
):
    expected_path = os.path.join(
        pdf_samples, "test_fill_with_customized_widgets_readonly.pdf"
    )
    with open(
        expected_path,
        "rb+",
    ) as f:
        obj = PdfWrapper(template_stream).register_font(
            "new_font",
            sample_font_stream,
        )
        obj.widgets["test"].font = "new_font"
        obj.widgets["test"].font_size = 20
        obj.widgets["test"].font_color = (1, 0, 0)
        obj.widgets["test_2"].font_color = (0, 1, 0)
        obj.fill(
            data_dict,
            readonly=True,
        )

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


def test_fill_with_varied_int_values(template_stream, pdf_samples, request):
    expected_path = os.path.join(pdf_samples, "test_fill_with_varied_int_values.pdf")
    with open(expected_path, "rb+") as f:
        obj = PdfWrapper(template_stream).fill(
            {
                "test": 100,
                "test_2": -250,
                "test_3": 0,
            }
        )

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


def test_fill_radiobutton_readonly(
    template_with_radiobutton_stream, pdf_samples, request
):
    expected_path = os.path.join(pdf_samples, "test_fill_radiobutton_readonly.pdf")
    with open(
        expected_path,
        "rb+",
    ) as f:
        obj = PdfWrapper(template_with_radiobutton_stream).fill(
            {
                "radio_1": 0,
                "radio_2": 1,
                "radio_3": 2,
            },
            readonly=True,
        )

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


def test_fill_radiobutton_readonly_then_editable(
    template_with_radiobutton_stream, pdf_samples, request
):
    expected_path = os.path.join(
        pdf_samples, "test_fill_radiobutton_readonly_then_editable.pdf"
    )
    with open(
        expected_path,
        "rb+",
    ) as f:
        obj = PdfWrapper(template_with_radiobutton_stream).fill(
            {
                "radio_1": 0,
                "radio_2": 1,
                "radio_3": 2,
            },
            readonly=True,
        )
        obj.widgets["radio_2"].readonly = False

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


def test_fill_sejda(sejda_template, pdf_samples, sejda_data, request):
    expected_path = os.path.join(pdf_samples, "test_fill_sejda.pdf")
    with open(
        expected_path,
        "rb+",
    ) as f:
        obj = PdfWrapper(sejda_template).fill(sejda_data)

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


def test_fill_sejda_readonly(sejda_template, pdf_samples, sejda_data, request):
    expected_path = os.path.join(pdf_samples, "test_fill_sejda_readonly.pdf")
    with open(
        expected_path,
        "rb+",
    ) as f:
        obj = PdfWrapper(sejda_template).fill(
            sejda_data,
            readonly=True,
        )

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


def test_fill_sejda_readonly_then_editable(
    sejda_template, pdf_samples, sejda_data, request
):
    expected_path = os.path.join(
        pdf_samples, "test_fill_sejda_readonly_then_editable.pdf"
    )
    with open(
        expected_path,
        "rb+",
    ) as f:
        obj = PdfWrapper(sejda_template).fill(
            sejda_data,
            readonly=True,
        )
        obj.widgets["buyer_name"].readonly = False
        obj.widgets["at_future_date"].readonly = False
        obj.widgets["purchase_option"].readonly = False

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


def test_addition_operator_3_times(template_stream, data_dict):
    result = PdfWrapper()

    for _ in range(3):
        result += PdfWrapper(template_stream).fill(data_dict)

    assert len((result + PdfWrapper()).read()) == len(result.read())
    assert (result + PdfWrapper()).read() == result.read()
    assert len(result.pages) == len(PdfWrapper(template_stream).pages) * 3

    result_2 = PdfWrapper()

    for _ in range(3):
        result_2 += PdfWrapper(template_stream).fill(data_dict).pages

    assert len(result_2.pages) == len(result.pages)


def test_merging_unique_suffix(template_stream):
    result = PdfWrapper()

    for i in range(10):
        obj = PdfWrapper(
            PdfWrapper(template_stream).fill({"test": f"value-{i}"}).read()
        )
        result += obj

    merged = PdfWrapper(result.read())

    for page, widgets in get_widgets_by_page(result.read()).items():
        for widget in widgets:
            assert widget[T] in merged.widgets
            if widget[T] == "test":
                assert widget[V] == "value-0"
            elif V in widget and "value-" in widget[V]:
                assert widget[V] == f"value-{page // 3}"
                assert widget[T].split("-")[0] == "test"
                assert len(widget[T].split("-")[1]) == UNIQUE_SUFFIX_LENGTH


def test_merge_preserve_font_and_data(template_stream, sample_font_stream):
    result = PdfWrapper()

    for i in range(10):
        obj = PdfWrapper(template_stream).register_font("new_font", sample_font_stream)
        obj.widgets["test"].font = "new_font"
        result += obj.fill({"test": f"test_{i}"})

    for page, widgets in get_widgets_by_page(result.read()).items():
        for widget in widgets:
            if widget[T] == "test":
                assert widget[V] == "test_0"
                assert widget[DA].startswith("/F1")
            elif widget[T].startswith("test-"):
                assert widget[V] == f"test_{page // 3}"
                assert widget[DA].startswith("/F1")


def test_schema(sample_template_with_comb_text_field):
    data = {
        "FirstName": "John",
        "MiddleName": "Joe",
        "LastName": "XXXXXXX",
        "Awesomeness": True,
        "Gender": 0,
    }
    schema = PdfWrapper(sample_template_with_comb_text_field).schema

    assert schema["type"] == "object"
    properties = schema["properties"]
    for key, value in data.items():
        if key == "LastName":
            assert properties[key]["maxLength"] == 7
        if isinstance(value, str):
            assert properties[key]["type"] == "string"
        elif isinstance(value, bool):
            assert properties[key]["type"] == "boolean"
        elif isinstance(value, int):
            assert properties[key]["type"] == "integer"
            assert properties[key]["maximum"] == 1

    validate(instance=data, schema=schema)

    data["LastName"] = "XXXXXXXX"
    try:
        validate(instance=data, schema=schema)
        raise AssertionError
    except ValidationError:
        pass

    data["LastName"] = "XXXXXXX"
    data["Gender"] = 1
    validate(instance=data, schema=schema)

    data["Gender"] = 2
    try:
        validate(instance=data, schema=schema)
        raise AssertionError
    except ValidationError:
        pass


def test_sample_data(sejda_template_complex):
    obj = PdfWrapper(sejda_template_complex)
    try:
        validate(instance=obj.sample_data, schema=obj.schema)
    except ValidationError:
        raise AssertionError from ValidationError

    widget = Widget("foo")
    try:
        widget.sample_value()
        raise AssertionError
    except NotImplementedError:
        pass


@pytest.mark.parametrize("field_name", ["dropdown_1", "radio_1"])
@pytest.mark.parametrize("option_count", [0, 1])
def test_sample_data_choice_boundaries(
    sample_template_with_dropdown, field_name, option_count
):
    form = PdfWrapper(sample_template_with_dropdown)
    widget = form.widgets[field_name]
    if field_name == "dropdown_1":
        choices = widget.choices
        assert choices is not None
        widget.choices = choices[:option_count]
    else:
        widget.number_of_options = option_count
    widget.value = None

    sample = form.sample_data
    if option_count:
        assert widget.sample_value == 0
        assert sample[field_name] == 0
    else:
        assert widget.sample_value is None
        assert field_name not in sample
    validate(sample, form.schema)
    form.fill(sample)
    assert widget.value == (0 if option_count else None)
    if field_name == "dropdown_1":
        reopened = PdfWrapper(form.read())
        assert reopened.widgets[field_name].choices == tuple(widget.choices)
        assert (field_name in reopened.sample_data) == bool(option_count)


def test_sample_data_max_boundary(sample_template_with_comb_text_field):
    obj = PdfWrapper(sample_template_with_comb_text_field)
    try:
        validate(instance=obj.sample_data, schema=obj.schema)
    except ValidationError:
        raise AssertionError from ValidationError

    assert obj.sample_data["LastName"] == "LastNam"
    assert obj.sample_data["Gender"] == 1


def test_fill_right_aligned(
    sample_template_with_right_aligned_text_field, pdf_samples, request
):
    expected_path = os.path.join(pdf_samples, "test_fill_right_aligned.pdf")
    with open(expected_path, "rb+") as f:
        obj = PdfWrapper(sample_template_with_right_aligned_text_field).fill(
            {
                "name": "Hans Mustermann",
                "fulladdress": "Musterstr. 12, 82903 Musterdorf, Musterland",
                "advisorname": "Karl Test",
            },
        )

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


def test_version(pdf_samples):
    versions = ["1.0", "1.1", "1.2", "1.3", "1.4", "1.5", "1.6", "1.7", "2.0"]

    for version in versions:
        obj = PdfWrapper(os.path.join(pdf_samples, "versions", f"{version}.pdf"))
        assert obj.version == version
        assert obj.change_version("2.0").version == "2.0"

    obj = PdfWrapper(os.path.join(pdf_samples, "versions", "unknown.pdf"))
    assert obj.version is None
    stream = obj.read()
    assert stream.startswith(b"%PDF-2.1")
    assert get_version(b"not a pdf") is None
    assert set_version(stream, obj.version, None) == stream
    assert set_version(b"not a pdf", None, "2.0") == b"not a pdf"
    assert set_version(b"prefix %PDF-1.7\n", "1.7", "2.0") == b"prefix %PDF-2.0\n"
    assert obj.change_version("2.0").version == "2.0"
    assert obj.read().startswith(b"%PDF-2.0")


@pytest.mark.requires_zlib_over_zlib_ng
def test_fill_font_color(sample_template_with_font_colors, pdf_samples, request):
    expected_path = os.path.join(pdf_samples, "test_fill_font_color.pdf")
    with open(expected_path, "rb+") as f:
        obj = PdfWrapper(sample_template_with_font_colors).fill(
            {
                "red_12": "red",
                "green_14": "green",
                "blue_16": "blue",
                "mixed_auto": "mixed",
            },
        )

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


@pytest.mark.requires_zlib_over_zlib_ng
def test_fill_complex_fonts(sample_template_with_complex_fonts, pdf_samples, request):
    expected_path = os.path.join(pdf_samples, "test_fill_complex_fonts.pdf")
    with open(expected_path, "rb+") as f:
        obj = PdfWrapper(sample_template_with_complex_fonts).fill(
            {
                "Courier": "Test",
                "Courier-Bold": "Test",
                "Courier-BoldOblique": "Test",
                "Courier-Oblique": "Test",
                "Helvetica": "Test",
                "Helvetica-Bold": "Test",
                "Helvetica-BoldOblique": "Test",
                "Helvetica-Oblique": "Test",
                "Times-Bold": "Test",
                "Times-BoldItalic": "Test",
                "Times-Italic": "Test",
                "Times-Roman": "Test",
            },
        )

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


@pytest.mark.requires_zlib_over_zlib_ng
def test_pages_preserve_font(template_stream, pdf_samples, sample_font_stream, request):
    expected_path = os.path.join(pdf_samples, "pages", "test_pages_preserve_font.pdf")
    obj = PdfWrapper(template_stream)
    obj.register_font("new_font", sample_font_stream)
    obj.widgets["test_2"].font = "new_font"

    with open(expected_path, "rb+") as f:
        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.pages[1].read()
        assert obj.pages[1].read() == f.read()


def test_sejda_pages_1(sejda_template, pdf_samples, request):
    expected_path = os.path.join(pdf_samples, "pages", "test_sejda_pages_1.pdf")
    obj = PdfWrapper(sejda_template)

    with open(expected_path, "rb+") as f:
        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.pages[0].read()
        assert obj.pages[0].read() == f.read()


def test_sejda_pages_2(sejda_template, pdf_samples, request):
    expected_path = os.path.join(pdf_samples, "pages", "test_sejda_pages_2.pdf")
    obj = PdfWrapper(sejda_template)

    with open(expected_path, "rb+") as f:
        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.pages[1].read()
        assert obj.pages[1].read() == f.read()


def test_radio_pages_1(template_with_radiobutton_stream, pdf_samples, request):
    expected_path = os.path.join(pdf_samples, "pages", "test_radio_pages_1.pdf")
    obj = PdfWrapper(template_with_radiobutton_stream)

    with open(expected_path, "rb+") as f:
        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.pages[0].read()
        assert obj.pages[0].read() == f.read()


def test_radio_pages_2(template_with_radiobutton_stream, pdf_samples, request):
    expected_path = os.path.join(pdf_samples, "pages", "test_radio_pages_2.pdf")
    obj = PdfWrapper(template_with_radiobutton_stream)

    with open(expected_path, "rb+") as f:
        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.pages[1].read()
        assert obj.pages[1].read() == f.read()


def test_radio_pages_3(template_with_radiobutton_stream, pdf_samples, request):
    expected_path = os.path.join(pdf_samples, "pages", "test_radio_pages_3.pdf")
    obj = PdfWrapper(template_with_radiobutton_stream)

    with open(expected_path, "rb+") as f:
        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.pages[2].read()
        assert obj.pages[2].read() == f.read()


def test_pages_inherit_attributes(template_stream):
    obj = PdfWrapper(
        template_stream,
        use_full_widget_name=True,
    )

    for page in obj.pages:
        assert getattr(page, "use_full_widget_name")


def test_generate_coordinate_grid_margin_50(template_stream, pdf_samples, request):
    expected_path = os.path.join(
        pdf_samples, "test_generate_coordinate_grid_margin_50.pdf"
    )
    with open(expected_path, "rb+") as f:
        obj = PdfWrapper(template_stream).generate_coordinate_grid((1, 0, 1), margin=50)

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


def test_update_radio_key(template_with_radiobutton_stream, pdf_samples, request):
    expected_path = os.path.join(pdf_samples, "test_update_radio_key.pdf")
    with open(expected_path, "rb+") as f:
        obj = PdfWrapper(template_with_radiobutton_stream)
        obj.update_widget_key("radio_3", "RADIO")
        obj.commit_widget_key_updates()
        obj.fill({"RADIO": 0})

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


def test_update_sejda_key(sejda_template, pdf_samples, request):
    expected_path = os.path.join(pdf_samples, "test_update_sejda_key.pdf")
    with open(expected_path, "rb+") as f:
        obj = PdfWrapper(sejda_template)
        obj.update_widget_key("year", "YEAR")
        obj.update_widget_key("at_future_date", "FUTURE_DATE")
        obj.update_widget_key("purchase_option", "PURCHASE_OPTION")
        obj.update_widget_key("buyer_signed_date", "BUYER_SIGNED_DATE")
        obj.commit_widget_key_updates()
        obj.fill(
            {
                "YEAR": "12",
                "FUTURE_DATE": True,
                "PURCHASE_OPTION": 1,
                "BUYER_SIGNED_DATE": "2012-01-01",
            }
        )

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


def test_uncheck_checkbox(pdf_samples, request):
    expected_path = os.path.join(pdf_samples, "test_uncheck_checkbox.pdf")
    with open(
        expected_path,
        "rb+",
    ) as f:
        obj = PdfWrapper(os.path.join(pdf_samples, "sample_template_filled.pdf")).fill(
            {"check": False, "check_2": False, "check_3": False},
        )

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


@pytest.mark.requires_zlib_over_zlib_ng
def test_blank_page(pdf_samples, request):
    expected_path = os.path.join(pdf_samples, "test_blank_page.pdf")
    with open(expected_path, "rb+") as f:
        obj = PdfWrapper(BlankPage() * 1)

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)

        assert not obj.widgets
        assert len(obj.pages) == 1

        request.config.results["skip_regenerate"] = len(obj.read()) == len(expected)


@pytest.mark.requires_zlib_over_zlib_ng
def test_blank_page_custom_size_multiply(pdf_samples, request):
    expected_path = os.path.join(
        pdf_samples, "test_blank_page_custom_size_multiply.pdf"
    )
    with open(expected_path, "rb+") as f:
        obj = PdfWrapper(BlankPage(595.35, 841.995) * 3)

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)

        assert not obj.widgets
        assert len(obj.pages) == 3

        request.config.results["skip_regenerate"] = len(obj.read()) == len(expected)


def test_widget_coord_resolution():
    obj = PdfWrapper(BlankPage()).bulk_create_fields(
        [
            Fields.TextField("text", 1, 50, 100, width=200, height=150),
            Fields.CheckBoxField("check", 1, 150, 200, size=60),
            Fields.RadioGroup("radio", 1, [400, 500, 600], [450, 550, 650], size=10),
            Fields.DropdownField(
                "dropdown", 1, 400, 100, width=250, height=200, options=["foo", "bar"]
            ),
            Fields.ImageField("image", 1, 300, 400, width=400, height=300),
            Fields.SignatureField("signature", 1, 500, 600, width=600, height=500),
        ]
    )

    assert obj.widgets["text"].page_number == 1
    assert obj.widgets["text"].x == 50
    assert obj.widgets["text"].y == 100
    assert obj.widgets["text"].width == 200
    assert obj.widgets["text"].height == 150

    assert obj.widgets["check"].page_number == 1
    assert obj.widgets["check"].x == 150
    assert obj.widgets["check"].y == 200
    assert obj.widgets["check"].width == 60
    assert obj.widgets["check"].height == 60

    assert obj.widgets["radio"].page_number == 1
    assert obj.widgets["radio"].x == [400, 500, 600]
    assert obj.widgets["radio"].y == [450, 550, 650]
    assert obj.widgets["radio"].width == 10
    assert obj.widgets["radio"].height == 10

    assert obj.widgets["dropdown"].page_number == 1
    assert obj.widgets["dropdown"].x == 400
    assert obj.widgets["dropdown"].y == 100
    assert obj.widgets["dropdown"].width == 250
    assert obj.widgets["dropdown"].height == 200

    assert obj.widgets["image"].page_number == 1
    assert obj.widgets["image"].x == 300
    assert obj.widgets["image"].y == 400
    assert obj.widgets["image"].width == 400
    assert obj.widgets["image"].height == 300

    assert obj.widgets["signature"].page_number == 1
    assert obj.widgets["signature"].x == 500
    assert obj.widgets["signature"].y == 600
    assert obj.widgets["signature"].width == 600
    assert obj.widgets["signature"].height == 500


def test_hidden_text_check(template_stream, pdf_samples, request):
    expected_path = os.path.join(pdf_samples, "test_hidden_text_check.pdf")
    with open(expected_path, "rb+") as f:
        obj = PdfWrapper(template_stream)
        obj.widgets["test"].hidden = True
        obj.widgets["check_2"].hidden = True

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


def test_hidden_radio(template_with_radiobutton_stream, pdf_samples, request):
    expected_path = os.path.join(pdf_samples, "test_hidden_radio.pdf")
    with open(expected_path, "rb+") as f:
        obj = PdfWrapper(template_with_radiobutton_stream)
        obj.widgets["radio_2"].hidden = True

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


def test_hidden_sejda(sejda_template, pdf_samples, request):
    expected_path = os.path.join(pdf_samples, "test_hidden_sejda.pdf")
    with open(expected_path, "rb+") as f:
        obj = PdfWrapper(sejda_template)
        obj.widgets["buyer_name"].hidden = True
        obj.widgets["purchase_option"].hidden = True
        obj.widgets["at_future_date"].hidden = True

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


def test_remove_fields_update_widgets(template_stream):
    obj = PdfWrapper(template_stream)
    obj.remove_fields(["test", "test_2", "check_2"])

    assert "test" not in obj.widgets
    assert "test_2" not in obj.widgets
    assert "check_2" not in obj.widgets


def test_remove_fields_no_keys_specified(template_stream):
    assert (
        PdfWrapper(template_stream).remove_fields([]).widgets.keys()
        == PdfWrapper(template_stream).widgets.keys()
    )


def test_merge(template_stream):
    pdf_list = PdfArray()
    for i in range(20):
        pdf_list.append(
            PdfWrapper(template_stream).fill(
                {
                    "test": f"test_1_{i}",
                    "check": True,
                    "test_2": f"test_2_{i}",
                    "check_2": False,
                    "test_3": f"test_3_{i}",
                    "check_3": True,
                }
            )
        )

    result = pdf_list.merge()
    assert len(result.pages) == 60

    for page, fields in get_widgets_by_page(result.read()).items():
        for field in fields:
            key = field[T]
            if key.startswith("test-"):
                assert field[V] == f"test_1_{int(page / 3)}"
            elif key.startswith("test_2-"):
                assert field[V] == f"test_2_{int(page / 3)}"
            elif key.startswith("test_3-"):
                assert field[V] == f"test_3_{int(page / 3 - 0.5)}"


def test_merge_empty_and_one_item(template_stream, sample_font_stream, data_dict):
    result = PdfArray().merge()
    assert isinstance(result, PdfWrapper)
    assert result.read() == b""

    empty = PdfWrapper()
    result = PdfArray([empty]).merge()
    assert result is not empty
    assert result.read() == b""

    source = (
        PdfWrapper(template_stream, need_appearances=True)
        .register_font("new_font", sample_font_stream)
        .fill(data_dict)
    )
    for pdfs in ([source], [PdfWrapper(), source, PdfWrapper()]):
        result = PdfArray(pdfs).merge()
        assert result is not source
        assert getattr(result, "need_appearances")
        assert result.fonts == source.fonts
        assert result.read() == source.read()
        assert PdfArray([result]).merge().read() == source.read()
        assert result.data == source.data
        assert PdfWrapper(result.read()).data == PdfWrapper(source.read()).data
        assert len(result.pages) == len(source.pages)

        result.fill({"test": "changed"})
        assert source.data["test"] == data_dict["test"]

    source.update_widget_key("test_2", "renamed")
    result = PdfArray([source]).merge()
    result.commit_widget_key_updates()
    assert "renamed" in result.widgets
    assert "test_2" in source.widgets


@pytest.mark.parametrize("version", ["1.7", "2.0"])
@pytest.mark.parametrize("padded", [False, True])
def test_merge_copy_preserves_version(template_stream, version, padded):
    source = PdfWrapper(template_stream).change_version(version)
    source.widgets["test"].font_size = 18
    result = PdfArray([source, PdfWrapper()] if padded else [source]).merge()

    assert result.version == source.version == version
    assert result.read().startswith(f"%PDF-{version}".encode())
    assert result.read() == source.read()


def test_merge_copy_preserves_widget_settings(pdf_samples, image_samples, tmp_path):
    template = os.path.join(
        pdf_samples, "signature", "sample_template_with_signature_overlap.pdf"
    )
    image = os.path.join(image_samples, "small_icon.png")
    expected = PdfWrapper(template)
    expected.widgets["signature"].preserve_aspect_ratio = False
    expected = expected.fill({"signature": image}).read()

    source = PdfWrapper(template)
    source.widgets["signature"].preserve_aspect_ratio = False
    for pdfs in ([source], [source, PdfWrapper()]):
        result = PdfArray(pdfs).merge()
        assert result.widgets["signature"] is not source.widgets["signature"]
        assert result.widgets["signature"].preserve_aspect_ratio is False
        assert result.fill({"signature": image}).read() == expected
    assert "signature" in source.widgets

    script = tmp_path / "script.js"
    script.write_text('app.alert("hello");')
    with open(script) as f:
        source.widgets["signature"].on_hovered_over_javascript = f
        result = PdfArray([source]).merge()
    assert result.widgets["signature"].on_hovered_over_javascript is f


def test_annotate(template_stream, pdf_samples, request):
    expected_path = os.path.join(pdf_samples, "test_annotate.pdf")
    with open(expected_path, "rb+") as f:
        obj = PdfWrapper(template_stream).annotate(
            [
                Annotations.TextAnnotation(
                    1, 100, 100, contents="this is an annotation"
                ),
                Annotations.TextAnnotation(
                    1,
                    200,
                    100,
                    contents="this is a second annotation",
                    title="Annotation 2",
                    icon=Annotations.TextAnnotation.comment_icon,
                ),
                Annotations.TextAnnotation(
                    1,
                    100,
                    200,
                    contents="this is a third annotation",
                    icon=Annotations.TextAnnotation.help_icon,
                ),
                Annotations.TextAnnotation(
                    1,
                    200,
                    200,
                    contents="this is a forth annotation",
                    icon=Annotations.TextAnnotation.key_icon,
                ),
                Annotations.TextAnnotation(
                    2,
                    100,
                    300,
                    contents="this is a fifth annotation",
                    icon=Annotations.TextAnnotation.insert_icon,
                ),
            ]
        )

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


def test_annotate_no_annotations(pdf_samples, request):
    expected_path = os.path.join(pdf_samples, "test_annotate_no_annotations.pdf")
    with open(expected_path, "rb+") as f:
        obj = PdfWrapper(os.path.join(pdf_samples, "dummy.pdf")).annotate(
            [
                Annotations.TextAnnotation(
                    1, 100, 100, contents="this is an annotation"
                ),
                Annotations.TextAnnotation(
                    1,
                    200,
                    100,
                    contents="this is a second annotation",
                    title="Annotation 2",
                    icon=Annotations.TextAnnotation.comment_icon,
                ),
                Annotations.TextAnnotation(
                    1,
                    100,
                    200,
                    contents="this is a third annotation",
                    icon=Annotations.TextAnnotation.help_icon,
                ),
                Annotations.TextAnnotation(
                    1,
                    200,
                    200,
                    contents="this is a forth annotation",
                    icon=Annotations.TextAnnotation.key_icon,
                ),
                Annotations.TextAnnotation(
                    1,
                    100,
                    300,
                    contents="this is a fifth annotation",
                    icon=Annotations.TextAnnotation.insert_icon,
                ),
            ]
        )

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


def test_rubber_stamp_annotation(template_stream, pdf_samples, request):
    expected_path = os.path.join(pdf_samples, "test_rubber_stamp_annotation.pdf")
    with open(expected_path, "rb+") as f:
        obj = PdfWrapper(template_stream).annotate(
            [
                Annotations.RubberStampAnnotation(
                    1,
                    0,
                    400,
                    width=50,
                    height=50,
                    name=Annotations.RubberStampAnnotation.approved,
                ),
                Annotations.RubberStampAnnotation(
                    1,
                    100,
                    400,
                    width=50,
                    height=50,
                    name=Annotations.RubberStampAnnotation.experimental,
                ),
                Annotations.RubberStampAnnotation(
                    1,
                    200,
                    400,
                    width=50,
                    height=50,
                    name=Annotations.RubberStampAnnotation.not_approved,
                ),
                Annotations.RubberStampAnnotation(
                    1,
                    300,
                    400,
                    width=50,
                    height=50,
                    name=Annotations.RubberStampAnnotation.as_is,
                ),
                Annotations.RubberStampAnnotation(
                    1,
                    400,
                    400,
                    width=50,
                    height=50,
                    name=Annotations.RubberStampAnnotation.expired,
                ),
                Annotations.RubberStampAnnotation(
                    1,
                    0,
                    500,
                    width=50,
                    height=50,
                    name=Annotations.RubberStampAnnotation.not_for_public_release,
                ),
                Annotations.RubberStampAnnotation(
                    1,
                    100,
                    500,
                    width=50,
                    height=50,
                    name=Annotations.RubberStampAnnotation.confidential,
                ),
                Annotations.RubberStampAnnotation(
                    1,
                    200,
                    500,
                    width=50,
                    height=50,
                    name=Annotations.RubberStampAnnotation.final,
                ),
                Annotations.RubberStampAnnotation(
                    1,
                    300,
                    500,
                    width=50,
                    height=50,
                    name=Annotations.RubberStampAnnotation.sold,
                ),
                Annotations.RubberStampAnnotation(
                    1,
                    400,
                    500,
                    width=50,
                    height=50,
                    name=Annotations.RubberStampAnnotation.departmental,
                ),
                Annotations.RubberStampAnnotation(
                    1,
                    0,
                    600,
                    width=50,
                    height=50,
                    name=Annotations.RubberStampAnnotation.for_comment,
                ),
                Annotations.RubberStampAnnotation(
                    1,
                    100,
                    600,
                    width=50,
                    height=50,
                    name=Annotations.RubberStampAnnotation.top_secret,
                ),
                Annotations.RubberStampAnnotation(
                    1,
                    200,
                    600,
                    width=50,
                    height=50,
                    name=Annotations.RubberStampAnnotation.draft,
                ),
                Annotations.RubberStampAnnotation(
                    1,
                    300,
                    600,
                    width=50,
                    height=50,
                    name=Annotations.RubberStampAnnotation.for_public_release,
                ),
            ]
        )

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


def get_link_targets(stream):
    result = []
    with Pdf.open(BytesIO(stream)) as pdf:
        page_numbers = {page.obj.objgen: i + 1 for i, page in enumerate(pdf.pages)}
        for i, page in enumerate(pdf.pages):
            for annot in page.get("/Annots", []):
                if annot.get("/Subtype") != Name.Link:
                    continue
                dest = annot.Dest if "/Dest" in annot else annot.A.get("/D")
                if dest is None:
                    result.append((i + 1, str(annot.A.URI), []))
                else:
                    target = page_numbers.get(getattr(dest[0], "objgen", None))
                    result.append((i + 1, target, [str(each) for each in dest[1:]]))
    return result


def test_link_page_destinations(template_stream):
    with Pdf.open(BytesIO(template_stream)) as pdf:
        # Links from another tool: a GoTo action and a link to its own page.
        pdf.pages[0].Annots.append(
            pdf.make_indirect(
                Dictionary(
                    Type=Name.Annot,
                    Subtype=Name.Link,
                    Rect=[0, 0, 10, 10],
                    BS=Dictionary(W=1, D=[3]),
                    A=Dictionary(
                        S=Name.GoTo, D=[pdf.pages[2].obj, Name.XYZ, 0, 500, 0]
                    ),
                )
            )
        )
        pdf.pages[1].Annots.append(
            pdf.make_indirect(
                Dictionary(
                    Type=Name.Annot,
                    Subtype=Name.Link,
                    Rect=[0, 0, 10, 10],
                    Dest=[pdf.pages[1].obj, Name.Fit],
                )
            )
        )
        stream = BytesIO()
        pdf.save(stream)

    linked = PdfWrapper(stream.getvalue()).annotate(
        [
            Annotations.LinkAnnotation(1, 70, 705, 95, 20, page=2),
            Annotations.LinkAnnotation(1, 70, 600, 95, 20, uri="https://example.com/"),
        ]
    )
    targets = [
        (1, 3, ["/XYZ", "0", "500", "0"]),
        (1, 2, ["/Fit"]),
        (1, "https://example.com/", []),
        (2, 2, ["/Fit"]),
    ]
    shifted = [
        (page + 3, target + 3 if isinstance(target, int) else target, view)
        for page, target, view in targets
    ]
    other = PdfWrapper(template_stream)
    merged = other + linked

    assert get_link_targets(linked.read()) == targets
    assert get_link_targets(merged.read()) == shifted
    assert get_link_targets((linked + other).read()) == targets
    assert get_link_targets(PdfArray([other, linked, other]).merge().read()) == shifted
    assert get_link_targets(PdfWrapper(merged.read()).pages[3].read()) == [
        (1, "https://example.com/", [])
    ]
    assert get_link_targets(linked.pages[1].read()) == [(1, 1, ["/Fit"])]
    with Pdf.open(BytesIO(merged.read())) as pdf:
        assert [
            list(annot.BS.D)
            for page in pdf.pages
            for annot in page.get("/Annots", [])
            if "/BS" in annot and "/D" in annot.BS
        ] == [[3]]

    for result in (
        PdfWrapper(linked.read()).draw([RawElements.RawText("drawn", 1, 100, 100)]),
        PdfWrapper(linked.read()).generate_coordinate_grid(),
    ):
        assert get_link_targets(result.read()) == targets
        assert get_link_targets(PdfWrapper(result.read()).read()) == targets


def test_invalid_link_page(template_stream):
    form = PdfWrapper(template_stream)
    stream = form.read()
    for page_number, page in ((1, 0), (1, 4), (9, 4)):
        with pytest.raises(
            ValueError, match=rf"Link page {page} must satisfy 1 <= page <= 3\."
        ):
            form.annotate(
                [
                    Annotations.TextAnnotation(1, 100, 100, contents="not added"),
                    Annotations.LinkAnnotation(page_number, 70, 705, 95, 20, page=page),
                ]
            )

        assert form.read() == stream


def test_rebuild_acroform_fields():
    pdf = PdfWrapper(BlankPage() * 2)

    pdf.bulk_create_fields(
        [Fields.TextField("foo", 1, 100, 100), Fields.TextField("bar", 2, 100, 200)]
    )

    reader = PdfReader(BytesIO(pdf.read()))

    assert get_widget_key(reader.root_object[AcroForm][FieldsConst][0], False) == "foo"
    assert get_widget_key(reader.root_object[AcroForm][FieldsConst][1], False) == "bar"


def test_rebuild_acroform_fields_ignores_note_title():
    form = PdfWrapper(BlankPage()).annotate(
        [
            Annotations.TextAnnotation(
                1, 100, 100, title="signature", contents="keep note"
            )
        ]
    )
    stream = form.read()

    result = egress.rebuild_acroform_fields(stream, {"signature"}, False)

    assert result == stream
    reader = PdfReader(BytesIO(result))
    assert not reader.get_fields()
    assert reader.pages[0]["/Annots"][0].get_object()["/Contents"] == "keep note"


@pytest.mark.parametrize("field_name", ["test", "check", "radio_1"])
def test_scalar_geometry(template_stream, template_with_radiobutton_stream, field_name):
    template = (
        template_with_radiobutton_stream if field_name == "radio_1" else template_stream
    )
    attributes = {"x": 123, "y": 0, "width": 80, "height": 40}
    form = PdfWrapper(template)
    float_form = PdfWrapper(template)
    expected = {name: getattr(form.widgets[field_name], name) for name in attributes}
    updates = attributes.copy()
    if field_name != "test":
        updates["size"] = 30

    for attribute, value in updates.items():
        setattr(form.widgets[field_name], attribute, value)
        setattr(float_form.widgets[field_name], attribute, float(value))
        for name in ("width", "height") if attribute == "size" else (attribute,):
            original = expected[name]
            expected[name] = (
                [value] * len(original) if isinstance(original, list) else value
            )

        stream = form.read()
        assert stream == float_form.read()
        reopened = PdfWrapper(stream)
        for name, expected_value in expected.items():
            assert getattr(reopened.widgets[field_name], name) == pytest.approx(
                expected_value
            )


def test_invalid_scalar_geometry(template_stream):
    for attribute in ("x", "y", "width", "height", "size"):
        for value in ("123", True, [123]):
            form = PdfWrapper(template_stream)
            setattr(form.widgets["check"], attribute, value)

            with pytest.raises(
                TypeError, match="Geometry values must be integers or floats"
            ):
                form.read()


@pytest.mark.parametrize(
    ("filename", "name", "spanning_pages"),
    [
        ("sample_template_with_radio_button.pdf", "radio_1", True),
        ("sample_template_sejda.pdf", "purchase_option", False),
    ],
)
def test_radio_group_selection(pdf_samples, filename, name, spanning_pages):
    with Pdf.open(os.path.join(pdf_samples, filename)) as pdf:
        group = next(field for field in pdf.Root.AcroForm.Fields if name == field.T)
        children = list(group.Kids)
        if spanning_pages:
            # Reverse page traversal order without changing /Kids or /Opt order.
            moved = children.pop(0)
            pdf.pages[0].Annots = [
                annot for annot in pdf.pages[0].Annots if annot.objgen != moved.objgen
            ]
            pdf.pages[1].Annots.append(moved)
            moved.P = pdf.pages[1].obj
            children.append(moved)
        states = [
            next(key for key in child.AP.N if key != "/Off") for child in children
        ]
        exports = [str(value) for value in group.get("/Opt", [])]
        # Start with an existing selection, independently of PdfWrapper.fill.
        group.V = Name(states[0])
        for index, child in enumerate(children):
            child.AS = Name(states[0] if index == 0 else "/Off")
        stream = BytesIO()
        pdf.save(stream)

    form = PdfWrapper(stream.getvalue())
    assert form.widgets[name].value == 0
    for reopen in (False, True):
        for index in (1, 0):
            form.fill({name: index})
            result = form.read()
            with Pdf.open(BytesIO(result)) as pdf:
                group = next(
                    field for field in pdf.Root.AcroForm.Fields if name == field.T
                )
                assert states[index] == group.V
                assert [str(child.AS) for child in group.Kids] == [
                    states[index] if states[index] in child.AP.N else "/Off"
                    for child in group.Kids
                ]
                assert [str(value) for value in group.get("/Opt", [])] == exports
            reopened = PdfWrapper(result)
            assert reopened.widgets[name].value == index
            if reopen:
                form = reopened


def test_choice_indices(sample_template_with_dropdown):
    for field_name, count in (("dropdown_1", 4), ("radio_1", 3)):
        for index in (0, count - 1):
            form = PdfWrapper(sample_template_with_dropdown)
            widget = form.widgets[field_name]
            validate({field_name: index}, form.schema)
            with patch.object(
                widget,
                "validate_choice_index",
                wraps=widget.validate_choice_index,
            ) as validation:
                form.fill({field_name: index})
                assert validation.call_count == 1
                validation.reset_mock()
                widget.value = index
                assert validation.call_count == 1

            assert form.widgets[field_name] is widget
            assert widget.value == index
            annotations = [
                reference.get_object()
                for page in PdfReader(BytesIO(form.read())).pages
                for reference in page.get("/Annots", [])
                if get_widget_key(reference.get_object(), False) == field_name
            ]
            assert annotations
            if field_name == "dropdown_1":
                choices = form.widgets[field_name].choices
                assert choices is not None
                assert annotations[0]["/V"] == choices[index]
                assert annotations[0]["/I"] == [index]
            else:
                assert len(annotations) == count
                selected = annotations[index]
                assert selected["/AS"] != "/Off"
                assert selected["/Parent"]["/V"] == selected["/AS"]
                assert all(
                    annotation["/AS"] == "/Off"
                    for i, annotation in enumerate(annotations)
                    if i != index
                )
                assert PdfWrapper(form.read()).widgets[field_name].value == index

    form = PdfWrapper(sample_template_with_dropdown)
    widget = form.widgets["dropdown_1"]
    widget.choices = []
    widget.value = None
    validate({"dropdown_1": "new option"}, form.schema)
    form.fill({"dropdown_1": "new option"})
    assert widget.choices == ["new option"]
    assert widget.value == 0


@pytest.mark.parametrize(("field_name", "count"), [("dropdown_1", 4), ("radio_1", 3)])
@pytest.mark.parametrize("empty", [False, True])
def test_invalid_choice_indices(
    sample_template_with_dropdown, field_name, count, empty
):
    option_count = 0 if empty else count
    form = PdfWrapper(sample_template_with_dropdown).fill({field_name: count - 1})
    widget = form.widgets[field_name]
    if empty:
        if field_name == "dropdown_1":
            widget.choices = []
        else:
            widget.number_of_options = 0
        widget.value = None
    stream = form.read()
    original_state = deepcopy(
        {key: value.__dict__ for key, value in form.widgets.items()}
    )
    for index in (-999, -1, option_count, option_count + 999):
        with pytest.raises(ValidationError):
            validate({field_name: index}, form.schema)
        with pytest.raises(ValueError, match="Choice index"):
            widget.value = index
        with pytest.raises(ValueError, match="Choice index"):
            form.fill(
                {
                    "test_1": "must not change",
                    "dropdown_1": "must not append",
                    field_name: index,
                },
                readonly=True,
            )

        assert {
            key: value.__dict__ for key, value in form.widgets.items()
        } == original_state
        assert form.read() == stream


@pytest.mark.parametrize(("field_name", "count"), [("dropdown_1", 4), ("radio_1", 3)])
@pytest.mark.parametrize("option_count", [1, 0])
def test_stale_choice_indices(
    sample_template_with_dropdown, field_name, count, option_count
):
    form = PdfWrapper(sample_template_with_dropdown).fill(
        {field_name: count - 1, "test_1": "original"}
    )
    widget = form.widgets[field_name]
    if field_name == "dropdown_1":
        choices = widget.choices
        assert choices is not None
        widget.choices = choices[:option_count]
    else:
        widget.number_of_options = option_count
    form.widgets["test_1"].x = 123
    stream = getattr(form, "_stream")
    original_state = deepcopy(
        {key: value.__dict__ for key, value in form.widgets.items()}
    )

    with pytest.raises(ValidationError):
        validate({field_name: widget.value}, form.schema)
    with pytest.raises(ValueError, match="Choice index"):
        form.fill({"test_1": "must not change"}, readonly=True)

    assert {
        key: value.__dict__ for key, value in form.widgets.items()
    } == original_state
    assert getattr(form, "_stream") == stream
    form.fill({field_name: 0 if option_count else None})
    assert widget.value == (0 if option_count else None)
