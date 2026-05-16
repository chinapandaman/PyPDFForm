# -*- coding: utf-8 -*-

import os

from PyPDFForm import PdfWrapper
from PyPDFForm.lib.middleware.checkbox import Checkbox
from PyPDFForm.lib.middleware.text import Text


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


def test_sejda_values(pdf_samples, sejda_data):
    obj = PdfWrapper(os.path.join(pdf_samples, "test_fill_sejda.pdf"))

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

    assert obj.widgets["dropdown_1"].value is None


def test_sejda_dropdown_values(pdf_samples):
    obj = PdfWrapper(
        os.path.join(pdf_samples, "dropdown", "test_dropdown_alignment_sejda.pdf")
    )

    assert obj.widgets["dropdown_left"].value is None
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


def test_field_readonly(pdf_samples):
    obj = PdfWrapper(os.path.join(pdf_samples, "test_fill_flatten_then_unflatten.pdf"))

    for k, v in obj.widgets.items():
        if k in ["test_2", "check_3"]:
            assert not v.readonly
        else:
            assert v.readonly


def test_field_readonly_sejda(pdf_samples):
    obj = PdfWrapper(os.path.join(pdf_samples, "test_fill_sejda_flatten.pdf"))

    for v in obj.widgets.values():
        assert v.readonly


def test_field_required(pdf_samples):
    obj = PdfWrapper(
        os.path.join(pdf_samples, "widget", "test_create_required_fields.pdf")
    )

    for v in obj.widgets.values():
        assert v.required


def test_field_required_sejda(pdf_samples):
    obj = PdfWrapper(
        os.path.join(
            pdf_samples,
            "test_widget_attr_trigger",
            "test_set_text_field_required_sejda.pdf",
        )
    )

    assert obj.widgets["buyer_address"].required
    for k, v in obj.widgets.items():
        if k != "buyer_address":
            assert not v.required


def test_field_hidden(pdf_samples):
    obj = PdfWrapper(os.path.join(pdf_samples, "test_hidden_text_check.pdf"))

    assert obj.widgets["test"].hidden
    assert obj.widgets["check_2"].hidden
    for k, v in obj.widgets.items():
        if k not in ["test", "check_2"]:
            assert not v.hidden


def test_field_hidden_sejda(pdf_samples):
    obj = PdfWrapper(os.path.join(pdf_samples, "test_hidden_sejda.pdf"))

    assert obj.widgets["buyer_name"].hidden
    assert obj.widgets["purchase_option"].hidden
    assert obj.widgets["at_future_date"].hidden
    for k, v in obj.widgets.items():
        if k not in ["buyer_name", "purchase_option", "at_future_date"]:
            assert not v.hidden


def test_text_field_alignment_sejda(pdf_samples):
    obj = PdfWrapper(
        os.path.join(
            pdf_samples,
            "test_widget_attr_trigger",
            "test_set_text_field_alignment_sejda.pdf",
        )
    )

    assert obj.widgets["buyer_name"].alignment == 2


def test_text_field_comb(max_length_expected_directory):
    obj = PdfWrapper(
        os.path.join(
            max_length_expected_directory,
            "test_fill_comb_text_field_all_chars.pdf",
        )
    )

    assert obj.widgets["LastName"].comb


def test_widget_repr_text(template_stream):
    obj = PdfWrapper(template_stream)
    widget = obj.widgets["test"]
    result = repr(widget)

    assert result.startswith("Text(")
    assert "comb=False" in result
    assert "height=" in result
    assert "hidden=False" in result
    assert "multiline=False" in result
    assert "name='test'" in result
    assert "page_number=1" in result
    assert "readonly=False" in result
    assert "required=False" in result
    assert "value=None" in result
    assert "width=" in result
    assert "x=" in result
    assert "y=" in result

    # None-valued optional attributes should be omitted
    assert "font=" not in result
    assert "font_size=" not in result
    # internal attrs should be omitted
    assert "SET_ATTR_TRIGGER_HOOK_MAP" not in result
    assert "attr_set_tracker" not in result
    assert "hooks_to_trigger" not in result


def test_widget_repr_checkbox(template_stream):
    obj = PdfWrapper(template_stream)
    widget = obj.widgets["check"]
    result = repr(widget)

    assert result.startswith("Checkbox(")
    assert "name='check'" in result
    assert "value=None" in result
    assert "SET_ATTR_TRIGGER_HOOK_MAP" not in result


def test_widget_repr_includes_non_none_attrs():
    widget = Text("my_field")
    widget.font_size = 12.0
    widget.readonly = True
    result = repr(widget)

    assert "font_size=12.0" in result
    assert "readonly=True" in result
    assert "font=" not in result


def test_widget_repr_checkbox_includes_size():
    widget = Checkbox("my_check")
    widget.size = 20.0
    result = repr(widget)

    assert result.startswith("Checkbox(")
    assert "width=20.0" in result
    assert "height=20.0" in result


def test_widget_repr_value_shown_when_set():
    widget = Text("field_name", value="hello")
    result = repr(widget)

    assert "name='field_name'" in result
    assert "value='hello'" in result


def test_widget_repr_all_fields_in_widgets(template_stream):
    obj = PdfWrapper(template_stream)
    for name, widget in obj.widgets.items():
        result = repr(widget)
        assert f"name={name!r}" in result
        assert "value=" in result


def test_text_field_comb_sejda(pdf_samples):
    obj = PdfWrapper(
        os.path.join(
            pdf_samples,
            "test_widget_attr_trigger",
            "test_set_text_field_comb_sejda.pdf",
        )
    )

    assert obj.widgets["buyer_name"].comb
