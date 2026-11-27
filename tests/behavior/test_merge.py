# -*- coding: utf-8 -*-

import os

import pytest

from PyPDFForm import PdfArray, PdfWrapper
from PyPDFForm.lib.constants import DA, UNIQUE_SUFFIX_LENGTH, T, V
from PyPDFForm.lib.template import get_widgets_by_page


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
