# -*- coding: utf-8 -*-

import os
import uuid

import pdfrw
import pytest

from PyPDFForm.core.constants import Merge as MergeCoreConstants
from PyPDFForm.core.constants import Template as TemplateCoreConstants
from PyPDFForm.core.template import Template as TemplateCore
from PyPDFForm.middleware.element import ElementType
from PyPDFForm.middleware.exceptions.template import InvalidTemplateError
from PyPDFForm.middleware.template import Template as TemplateMiddleware


@pytest.fixture
def pdf_samples():
    return os.path.join(os.path.dirname(__file__), "..", "..", "pdf_samples", "v2")


@pytest.fixture
def template_stream(pdf_samples):
    with open(os.path.join(pdf_samples, "sample_template.pdf"), "rb+") as f:
        return f.read()


@pytest.fixture
def template_with_radiobutton_stream(pdf_samples):
    with open(
        os.path.join(pdf_samples, "sample_template_with_radio_button.pdf"), "rb+"
    ) as f:
        return f.read()


@pytest.fixture
def data_dict():
    return {
        "test": False,
        "check": False,
        "radio_1": False,
        "test_2": False,
        "check_2": False,
        "radio_2": False,
        "test_3": False,
        "check_3": False,
        "radio_3": False,
    }


def test_validate_template():
    bad_inputs = [""]

    try:
        TemplateMiddleware().validate_template(*bad_inputs)
        assert False
    except InvalidTemplateError:
        assert True


def test_validate_template_stream(template_stream):
    try:
        TemplateMiddleware().validate_stream(b"")
        assert False
    except InvalidTemplateError:
        assert True

    TemplateMiddleware().validate_stream(template_stream)
    assert True


def test_iterate_elements_and_get_element_key(
    template_with_radiobutton_stream, data_dict
):
    for each in TemplateCore().iterate_elements(template_with_radiobutton_stream):
        data_dict[TemplateCore().get_element_key(each)] = True

    for k in data_dict.keys():
        assert data_dict[k]


def test_iterate_elements_and_get_element_key_sejda(
    sejda_template, sejda_data
):
    data_dict = {
        key: False
        for key in sejda_data.keys()
    }
    for each in TemplateCore().iterate_elements(sejda_template, sejda=True):
        data_dict[TemplateCore().get_element_key(each, sejda=True)] = True

    for k in data_dict.keys():
        assert data_dict[k]


def test_get_elements_by_page_sejda(sejda_template):
    expected = {
        1: {
            "date": False,
            "year": False,
            "buyer_name": False,
            "buyer_address": False,
            "seller_name": False,
            "seller_address": False,
            "make": False,
            "model": False,
            "caliber": False,
            "serial_number": False,
            "purchase_option": False,
            "date_of_this_bill": False,
            "at_future_date": False,
            "other": False,
            "other_reason": False,
            "future_date": False,
            "future_year": False,
            "exchange_for": False,
        },
        2: {
            "buyer_name_printed": False,
            "seller_name_printed": False,
            "buyer_signed_date": False,
            "seller_signed_date": False,
            "buyer_dl_number": False,
            "seller_dl_number": False,
            "buyer_dl_state": False,
            "seller_dl_state": False,
        },
    }

    for page, elements in (
        TemplateCore().get_elements_by_page(sejda_template, sejda=True).items()
    ):
        for each in elements:
            expected[page][TemplateCore().get_element_key(each, sejda=True)] = True

    for page, elements in expected.items():
        for k in elements.keys():
            assert expected[page][k]


def test_get_elements_by_page(template_with_radiobutton_stream):
    expected = {
        1: {
            "test": False,
            "check": False,
            "radio_1": False,
        },
        2: {
            "test_2": False,
            "check_2": False,
            "radio_2": False,
        },
        3: {
            "test_3": False,
            "check_3": False,
            "radio_3": False,
        },
    }

    for page, elements in (
        TemplateCore().get_elements_by_page(template_with_radiobutton_stream).items()
    ):
        for each in elements:
            expected[page][TemplateCore().get_element_key(each)] = True

    for page, elements in expected.items():
        for k in elements.keys():
            assert expected[page][k]


def test_get_element_type_sejda(sejda_template):
    type_mapping = {
        "date": ElementType.text,
        "year": ElementType.text,
        "buyer_name": ElementType.text,
        "buyer_address": ElementType.text,
        "seller_name": ElementType.text,
        "seller_address": ElementType.text,
        "make": ElementType.text,
        "model": ElementType.text,
        "caliber": ElementType.text,
        "serial_number": ElementType.text,
        "purchase_option": ElementType.radio,
        "date_of_this_bill": ElementType.checkbox,
        "at_future_date": ElementType.checkbox,
        "other": ElementType.checkbox,
        "other_reason": ElementType.text,
        "payment_amount": ElementType.text,
        "future_date": ElementType.text,
        "future_year": ElementType.text,
        "exchange_for": ElementType.text,
        "buyer_name_printed": ElementType.text,
        "seller_name_printed": ElementType.text,
        "buyer_signed_date": ElementType.text,
        "seller_signed_date": ElementType.text,
        "buyer_dl_number": ElementType.text,
        "seller_dl_number": ElementType.text,
        "buyer_dl_state": ElementType.text,
        "seller_dl_state": ElementType.text,
    }

    for each in TemplateCore().iterate_elements(sejda_template, sejda=True):
        assert type_mapping[
            TemplateCore().get_element_key(each, sejda=True)
        ] == TemplateCore().get_element_type(each, sejda=True)

    read_template_stream = pdfrw.PdfReader(fdata=sejda_template)

    for each in TemplateCore().iterate_elements(read_template_stream):
        assert type_mapping[
            TemplateCore().get_element_key(each, sejda=True)
        ] == TemplateCore().get_element_type(each, sejda=True)


def test_get_element_type(template_stream):
    type_mapping = {
        "test": ElementType.text,
        "check": ElementType.checkbox,
        "test_2": ElementType.text,
        "check_2": ElementType.checkbox,
        "test_3": ElementType.text,
        "check_3": ElementType.checkbox,
    }

    for each in TemplateCore().iterate_elements(template_stream):
        assert type_mapping[
            TemplateCore().get_element_key(each)
        ] == TemplateCore().get_element_type(each)

    read_template_stream = pdfrw.PdfReader(fdata=template_stream)

    for each in TemplateCore().iterate_elements(read_template_stream):
        assert type_mapping[
            TemplateCore().get_element_key(each)
        ] == TemplateCore().get_element_type(each)


def test_get_element_type_radiobutton(template_with_radiobutton_stream):
    type_mapping = {
        "test": ElementType.text,
        "check": ElementType.checkbox,
        "test_2": ElementType.text,
        "check_2": ElementType.checkbox,
        "test_3": ElementType.text,
        "check_3": ElementType.checkbox,
        "radio_1": ElementType.radio,
        "radio_2": ElementType.radio,
        "radio_3": ElementType.radio,
    }

    for each in TemplateCore().iterate_elements(template_with_radiobutton_stream):
        assert type_mapping[
            TemplateCore().get_element_key(each)
        ] == TemplateCore().get_element_type(each)

    read_template_stream = pdfrw.PdfReader(fdata=template_with_radiobutton_stream)

    for each in TemplateCore().iterate_elements(read_template_stream):
        assert type_mapping[
            TemplateCore().get_element_key(each)
        ] == TemplateCore().get_element_type(each)


def test_build_elements(template_with_radiobutton_stream, data_dict):
    for k, v in (
        TemplateMiddleware().build_elements(template_with_radiobutton_stream).items()
    ):
        if k in data_dict and k == v.name:
            data_dict[k] = True

    for k in data_dict.keys():
        assert data_dict[k]


def test_build_elements_sejda(sejda_template, sejda_data):
    data_dict = {
        key: False
        for key in sejda_data.keys()
    }

    for k, v in (
        TemplateMiddleware().build_elements(sejda_template, sejda=True).items()
    ):
        if k in data_dict and k == v.name:
            data_dict[k] = True

    for k in data_dict.keys():
        assert data_dict[k]


def test_get_draw_text_coordinates(template_stream):
    for element in TemplateCore().iterate_elements(template_stream):
        assert TemplateCore().get_draw_text_coordinates(element) == (
            float(element[TemplateCoreConstants().annotation_rectangle_key][0]),
            (
                float(element[TemplateCoreConstants().annotation_rectangle_key][1])
                + float(element[TemplateCoreConstants().annotation_rectangle_key][3])
            )
            / 2
            - 2,
        )


def test_get_draw_checkbox_radio_coordinates(sejda_template):
    for element in TemplateCore().iterate_elements(sejda_template):
        assert TemplateCore().get_draw_checkbox_radio_coordinates(element) == (
            (
                    float(element[TemplateCoreConstants().annotation_rectangle_key][0])
                    + float(element[TemplateCoreConstants().annotation_rectangle_key][2])
            )
            / 2
            - 5,
            (
                float(element[TemplateCoreConstants().annotation_rectangle_key][1])
                + float(element[TemplateCoreConstants().annotation_rectangle_key][3])
            )
            / 2
            - 4,
        )


def test_assign_uuid(template_with_radiobutton_stream, data_dict):
    for element in TemplateCore().iterate_elements(
        TemplateCore().assign_uuid(template_with_radiobutton_stream)
    ):
        key = TemplateCore().get_element_key(element)
        assert MergeCoreConstants().separator in key

        key, _uuid = key.split(MergeCoreConstants().separator)

        assert len(_uuid) == len(uuid.uuid4().hex)
        data_dict[key] = True

    for k in data_dict.keys():
        assert data_dict[k]
