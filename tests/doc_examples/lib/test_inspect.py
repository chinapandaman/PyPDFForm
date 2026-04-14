# -*- coding: utf-8 -*-

import os

from PyPDFForm import PdfWrapper


def test_schema(static_pdfs):
    pdf_form_schema = PdfWrapper(
        os.path.join(static_pdfs, "sample_template.pdf")
    ).schema

    assert pdf_form_schema == {
        "type": "object",
        "properties": {
            "test": {"type": "string"},
            "check": {"type": "boolean"},
            "test_2": {"type": "string"},
            "check_2": {"type": "boolean"},
            "test_3": {"type": "string"},
            "check_3": {"type": "boolean"},
        },
    }


def test_widgets(static_pdfs):
    pdf_widgets =repr(PdfWrapper(
        os.path.join(static_pdfs, "sample_template.pdf")
    ).widgets)

    assert pdf_widgets ==  "{'test': Text(name='test', value=None, readonly=False, required=False, hidden=False, page_number=1, x=73.3365, y=662.692, width=232.4235, height=21.067999999999984, comb=False, multiline=False), 'check': Checkbox(name='check', value=None, readonly=False, required=False, hidden=False, page_number=1, x=358.874, y=664.717, width=18.47999999999996, height=18.480000000000018), 'test_2': Text(name='test_2', value=None, readonly=False, required=False, hidden=False, page_number=2, x=71.4095, y=671.626, width=232.42350000000005, height=21.067999999999984, comb=False, multiline=False), 'check_2': Checkbox(name='check_2', value=None, readonly=False, required=False, hidden=False, page_number=2, x=349.637, y=673.954, width=18.478999999999985, height=18.480000000000018), 'test_3': Text(name='test_3', value=None, readonly=False, required=False, hidden=False, page_number=3, x=70.5919, y=665.349, width=232.42309999999998, height=21.067999999999984, comb=False, multiline=False), 'check_3': Checkbox(name='check_3', value=None, readonly=False, required=False, hidden=False, page_number=3, x=349.305, y=667.344, width=18.480000000000018, height=18.479999999999905)}"


def test_data(static_pdfs):
    assert PdfWrapper(os.path.join(static_pdfs, "sample_template_filled.pdf")).data == {
        "check": True,
        "check_2": True,
        "check_3": True,
        "test": "test",
        "test_2": "test2",
        "test_3": "test3",
    }


def test_sample_data(static_pdfs):
    assert PdfWrapper(os.path.join(static_pdfs, "sample_template.pdf")).sample_data == {
        "check": True,
        "check_2": True,
        "check_3": True,
        "test": "test",
        "test_2": "test_2",
        "test_3": "test_3",
    }
