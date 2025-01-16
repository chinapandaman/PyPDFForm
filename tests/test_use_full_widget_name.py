# -*- coding: utf-8 -*-

import pytest

from PyPDFForm import PdfWrapper


def test_init(sample_template_with_full_key):
    obj = PdfWrapper(sample_template_with_full_key, use_full_widget_name=True)
    assert "Gain de 2 classes.0" in obj.widgets
    assert obj.widgets["Gain de 2 classes.0"] is obj.widgets["0"]


def test_sample_data(sample_template_with_full_key):
    obj = PdfWrapper(sample_template_with_full_key, use_full_widget_name=True)
    assert "Gain de 2 classes.0" in obj.sample_data
    assert obj.sample_data["Gain de 2 classes.0"] == obj.sample_data["0"]


def test_fill(sample_template_with_full_key):
    obj_1 = PdfWrapper(sample_template_with_full_key, use_full_widget_name=True)
    obj_2 = PdfWrapper(sample_template_with_full_key, use_full_widget_name=True)

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
    assert (
        obj.schema["properties"]["Gain de 2 classes.0"] == obj.schema["properties"]["0"]
    )
