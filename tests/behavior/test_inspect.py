# -*- coding: utf-8 -*-

import os

import pytest
from jsonschema import ValidationError, validate

from PyPDFForm import PdfWrapper
from PyPDFForm.lib.middleware.base import Widget


def test_base_schema_definition():
    assert Widget("foo").schema_definition == {}


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


def test_text_check_values(pdf_samples, data_dict):
    obj = PdfWrapper(os.path.join(pdf_samples, "test_fill.pdf"))

    for k, v in data_dict.items():
        if v is False:
            assert obj.widgets[k].value is None
        else:
            assert obj.widgets[k].value == v


def test_radio_values(pdf_samples):
    data_dict = {
        "radio_1": 0,
        "radio_2": 1,
        "radio_3": 2,
    }
    obj = PdfWrapper(os.path.join(pdf_samples, "test_fill_radiobutton.pdf"))

    for k, v in data_dict.items():
        assert obj.widgets[k].value == v


def test_sejda_values(expected_pdfs, sejda_data):
    obj = PdfWrapper(
        os.path.join(expected_pdfs, "snapshots", "test_fill", "test_fill_sejda.pdf")
    )

    for k, v in sejda_data.items():
        if v is False:
            assert obj.widgets[k].value is None
        else:
            assert obj.widgets[k].value == v


def test_dropdown_values(pdf_samples):
    obj = PdfWrapper(os.path.join(pdf_samples, "dropdown", "test_dropdown_two.pdf"))

    assert obj.widgets["dropdown_1"].value == 1


def test_dropdown_default_values(pdf_samples):
    obj = PdfWrapper(os.path.join(pdf_samples, "dropdown", "test_dropdown_one.pdf"))

    assert obj.widgets["dropdown_1"].value == 0


def test_sejda_dropdown_values(expected_pdfs):
    obj = PdfWrapper(
        os.path.join(
            expected_pdfs, "snapshots", "test_fill", "test_dropdown_alignment_sejda.pdf"
        )
    )

    assert obj.widgets["dropdown_left"].value == 0
    assert obj.widgets["dropdown_center"].value == 1
    assert obj.widgets["dropdown_right"].value == 2


def test_addition_operator_3_times_values(template_stream, data_dict):
    result = PdfWrapper()

    for _ in range(3):
        result += PdfWrapper(template_stream).fill(data_dict)

    obj = PdfWrapper(result.read())

    for k, v in obj.widgets.items():
        if k.split("-")[0] in data_dict:
            assert (v.value or False) == data_dict[k.split("-")[0]]


def test_field_readonly(expected_pdfs):
    obj = PdfWrapper(
        os.path.join(
            expected_pdfs,
            "snapshots",
            "test_fill",
            "test_fill_readonly_then_editable.pdf",
        )
    )

    for k, v in obj.widgets.items():
        if k in ["test_2", "check_3"]:
            assert not v.readonly
        else:
            assert v.readonly


def test_field_readonly_sejda(expected_pdfs):
    obj = PdfWrapper(
        os.path.join(
            expected_pdfs, "snapshots", "test_fill", "test_fill_sejda_readonly.pdf"
        )
    )

    for v in obj.widgets.values():
        assert v.readonly


def test_field_required(expected_pdfs):
    obj = PdfWrapper(
        os.path.join(
            expected_pdfs,
            "snapshots",
            "test_prepare",
            "test_create_required_fields.pdf",
        )
    )

    for v in obj.widgets.values():
        assert v.required


def test_field_required_sejda(expected_pdfs):
    obj = PdfWrapper(
        os.path.join(
            expected_pdfs,
            "snapshots",
            "test_style",
            "test_set_text_field_required_sejda.pdf",
        )
    )

    assert obj.widgets["buyer_address"].required
    for k, v in obj.widgets.items():
        if k != "buyer_address":
            assert not v.required


def test_field_hidden(expected_pdfs):
    obj = PdfWrapper(
        os.path.join(
            expected_pdfs, "snapshots", "test_style", "test_hidden_text_check.pdf"
        )
    )

    assert obj.widgets["test"].hidden
    assert obj.widgets["check_2"].hidden
    for k, v in obj.widgets.items():
        if k not in ["test", "check_2"]:
            assert not v.hidden


def test_field_hidden_sejda(expected_pdfs):
    obj = PdfWrapper(
        os.path.join(expected_pdfs, "snapshots", "test_style", "test_hidden_sejda.pdf")
    )

    assert obj.widgets["buyer_name"].hidden
    assert obj.widgets["purchase_option"].hidden
    assert obj.widgets["at_future_date"].hidden
    for k, v in obj.widgets.items():
        if k not in ["buyer_name", "purchase_option", "at_future_date"]:
            assert not v.hidden


def test_text_field_alignment_sejda(expected_pdfs):
    obj = PdfWrapper(
        os.path.join(
            expected_pdfs,
            "snapshots",
            "test_style",
            "test_set_text_field_alignment_sejda.pdf",
        )
    )

    assert obj.widgets["buyer_name"].alignment == 2


def test_text_field_comb(expected_pdfs):
    obj = PdfWrapper(
        os.path.join(
            expected_pdfs,
            "snapshots",
            "test_fill",
            "test_fill_comb_text_field_all_chars.pdf",
        )
    )

    assert obj.widgets["LastName"].comb


def test_text_field_comb_sejda(expected_pdfs):
    obj = PdfWrapper(
        os.path.join(
            expected_pdfs,
            "snapshots",
            "test_style",
            "test_set_text_field_comb_sejda.pdf",
        )
    )

    assert obj.widgets["buyer_name"].comb
