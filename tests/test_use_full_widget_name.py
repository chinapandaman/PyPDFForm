# -*- coding: utf-8 -*-

import pytest

from PyPDFForm import BlankPage, Fields, PdfWrapper


@pytest.fixture
def full_name_forms():
    return [
        PdfWrapper(BlankPage(), use_full_widget_name=True)
        .bulk_create_fields([Fields.TextField(name, 1, 100, 100)])
        .fill({name: f"{name} value"})
        for name in ("left", "right")
    ]


def test_init(sample_template_with_full_key):
    obj = PdfWrapper(sample_template_with_full_key, use_full_widget_name=True)
    assert "Gain de 2 classes.0" in obj.widgets
    assert "0" not in obj.widgets


def test_sample_data(sample_template_with_full_key):
    obj = PdfWrapper(sample_template_with_full_key, use_full_widget_name=True)
    assert "Gain de 2 classes.0" in obj.sample_data
    assert "0" not in obj.sample_data


def test_fill(sample_template_with_full_key):
    obj_1 = PdfWrapper(sample_template_with_full_key, use_full_widget_name=True)
    obj_2 = PdfWrapper(sample_template_with_full_key)

    assert (
        obj_1.fill({"Gain de 2 classes.0": True}).read()
        == obj_2.fill({"0": True}).read()
    )


def test_update_widget_key(sample_template_with_full_key):
    obj = PdfWrapper(sample_template_with_full_key, use_full_widget_name=True)

    with pytest.raises(NotImplementedError):
        obj.update_widget_key("0", "foo")


def test_commit_widget_key_updates(sample_template_with_full_key):
    obj = PdfWrapper(sample_template_with_full_key, use_full_widget_name=True)

    with pytest.raises(NotImplementedError):
        obj.commit_widget_key_updates()


def test_schema(sample_template_with_full_key):
    obj = PdfWrapper(sample_template_with_full_key, use_full_widget_name=True)
    assert "Gain de 2 classes.0" in obj.schema["properties"]
    assert "0" not in obj.schema


def test_remove_fields(sample_template_with_full_key):
    obj = PdfWrapper(sample_template_with_full_key, use_full_widget_name=True)
    obj.remove_fields(["Gain de 2 classes.0"])

    assert "Gain de 2 classes.0" not in obj.widgets
    assert "0" not in obj.widgets


def test_merge(full_name_forms):
    left, right = full_name_forms
    originals = [form.read() for form in full_name_forms]

    merged = left + right

    expected = {"left": "left value", "right": "right value"}
    assert merged.use_full_widget_name
    assert merged.data == expected
    reopened = PdfWrapper(merged.read(), use_full_widget_name=True)
    assert reopened.data == expected
    assert len(reopened.pages) == 2
    assert [form.read() for form in full_name_forms] == originals


def test_merge_collision(full_name_forms):
    left = full_name_forms[0]
    right = PdfWrapper(left.read(), use_full_widget_name=True)
    originals = (left.read(), right.read())

    with pytest.raises(NotImplementedError):
        _ = left + right

    assert (left.read(), right.read()) == originals
    assert left.data == right.data == {"left": "left value"}


def test_page_slice(template_stream):
    source = PdfWrapper(template_stream, use_full_widget_name=True).fill(
        {"test": "first", "test_2": "second", "test_3": "third"}
    )
    original = source.read()

    result = source.pages[1:]

    expected = {
        "test_2": "second",
        "check_2": None,
        "test_3": "third",
        "check_3": None,
    }
    assert result.use_full_widget_name
    assert result.data == expected
    reopened = PdfWrapper(result.read(), use_full_widget_name=True)
    assert reopened.data == expected
    assert len(reopened.pages) == 2
    assert reopened.widgets["test_2"].page_number == 1
    assert reopened.widgets["test_3"].page_number == 2
    assert source.read() == original
