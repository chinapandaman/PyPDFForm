# -*- coding: utf-8 -*-

import os

from PyPDFForm import PdfWrapper


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
