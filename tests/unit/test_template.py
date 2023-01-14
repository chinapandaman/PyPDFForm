# -*- coding: utf-8 -*-

import os
import uuid

import pdfrw
import pytest

from PyPDFForm.core import constants, template
from PyPDFForm.middleware import template as template_middleware
from PyPDFForm.middleware.element import ElementType
from PyPDFForm.middleware.exceptions.template import InvalidTemplateError


@pytest.fixture
def pdf_samples():
    return os.path.join(os.path.dirname(__file__), "..", "..", "pdf_samples")


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
        template_middleware.validate_template(*bad_inputs)
        assert False
    except InvalidTemplateError:
        assert True


def test_validate_template_stream(template_stream):
    try:
        template_middleware.validate_stream(b"")
        assert False
    except InvalidTemplateError:
        assert True

    template_middleware.validate_stream(template_stream)
    assert True


def test_remove_all_elements(template_stream):
    result = template.remove_all_elements(template_stream)
    assert not template.iterate_elements(result)


def test_iterate_elements_and_get_element_key(
    template_with_radiobutton_stream, data_dict
):
    for each in template.iterate_elements(template_with_radiobutton_stream):
        data_dict[template.get_element_key(each)] = True

    for k in data_dict.keys():
        assert data_dict[k]


def test_iterate_elements_and_get_element_key_v2(
    template_with_radiobutton_stream, data_dict
):
    assert template.get_element_key_v2(pdfrw.PdfDict()) is None
    for each in template.iterate_elements(template_with_radiobutton_stream):
        data_dict[template.get_element_key_v2(each)] = True

    for k in data_dict.keys():
        assert data_dict[k]


def test_iterate_elements_and_get_element_key_sejda(sejda_template, sejda_data):
    data_dict = {key: False for key in sejda_data.keys()}
    for each in template.iterate_elements(sejda_template, sejda=True):
        data_dict[template.get_element_key(each, sejda=True)] = True

    for k in data_dict.keys():
        assert data_dict[k]


def test_iterate_elements_and_get_element_key_v2_sejda(sejda_template, sejda_data):
    data_dict = {key: False for key in sejda_data.keys()}
    for each in template.iterate_elements(sejda_template, sejda=True):
        data_dict[template.get_element_key_v2(each)] = True

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

    for page, elements in template.get_elements_by_page(
        sejda_template, sejda=True
    ).items():
        for each in elements:
            expected[page][template.get_element_key(each, sejda=True)] = True

    for page, elements in expected.items():
        for k in elements.keys():
            assert expected[page][k]


def test_get_elements_by_page_sejda_v2(sejda_template):
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

    for page, elements in template.get_elements_by_page_v2(sejda_template).items():
        for each in elements:
            expected[page][template.get_element_key(each, sejda=True)] = True

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

    for page, elements in template.get_elements_by_page(
        template_with_radiobutton_stream
    ).items():
        for each in elements:
            expected[page][template.get_element_key(each)] = True

    for page, elements in expected.items():
        for k in elements.keys():
            assert expected[page][k]


def test_get_elements_by_page_v2(template_with_radiobutton_stream):
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

    for page, elements in template.get_elements_by_page_v2(
        template_with_radiobutton_stream
    ).items():
        for each in elements:
            expected[page][template.get_element_key(each)] = True

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

    for each in template.iterate_elements(sejda_template, sejda=True):
        assert type_mapping[
            template.get_element_key(each, sejda=True)
        ] == template.get_element_type(each, sejda=True)

    read_template_stream = pdfrw.PdfReader(fdata=sejda_template)

    for each in template.iterate_elements(read_template_stream):
        assert type_mapping[
            template.get_element_key(each, sejda=True)
        ] == template.get_element_type(each, sejda=True)


def test_get_element_type_v2_sejda(sejda_template):
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

    for each in template.iterate_elements(sejda_template, sejda=True):
        assert type_mapping[
            template.get_element_key_v2(each)
        ] == template.get_element_type_v2(each)

    read_template_stream = pdfrw.PdfReader(fdata=sejda_template)

    for each in template.iterate_elements(read_template_stream):
        assert type_mapping[
            template.get_element_key_v2(each)
        ] == template.get_element_type_v2(each)


def test_get_element_type(template_stream):
    type_mapping = {
        "test": ElementType.text,
        "check": ElementType.checkbox,
        "test_2": ElementType.text,
        "check_2": ElementType.checkbox,
        "test_3": ElementType.text,
        "check_3": ElementType.checkbox,
    }

    for each in template.iterate_elements(template_stream):
        assert type_mapping[
            template.get_element_key(each)
        ] == template.get_element_type(each)

    read_template_stream = pdfrw.PdfReader(fdata=template_stream)

    for each in template.iterate_elements(read_template_stream):
        assert type_mapping[
            template.get_element_key(each)
        ] == template.get_element_type(each)


def test_get_element_type_v2(template_stream):
    assert template.get_element_type_v2(pdfrw.PdfDict()) is None

    type_mapping = {
        "test": ElementType.text,
        "check": ElementType.checkbox,
        "test_2": ElementType.text,
        "check_2": ElementType.checkbox,
        "test_3": ElementType.text,
        "check_3": ElementType.checkbox,
    }

    for each in template.iterate_elements(template_stream):
        assert type_mapping[
            template.get_element_key_v2(each)
        ] == template.get_element_type_v2(each)

    read_template_stream = pdfrw.PdfReader(fdata=template_stream)

    for each in template.iterate_elements(read_template_stream):
        assert type_mapping[
            template.get_element_key_v2(each)
        ] == template.get_element_type_v2(each)


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

    for each in template.iterate_elements(template_with_radiobutton_stream):
        assert type_mapping[
            template.get_element_key(each)
        ] == template.get_element_type(each)

    read_template_stream = pdfrw.PdfReader(fdata=template_with_radiobutton_stream)

    for each in template.iterate_elements(read_template_stream):
        assert type_mapping[
            template.get_element_key(each)
        ] == template.get_element_type(each)


def test_get_element_type_v2_radiobutton(template_with_radiobutton_stream):
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

    for each in template.iterate_elements(template_with_radiobutton_stream):
        assert type_mapping[
            template.get_element_key_v2(each)
        ] == template.get_element_type_v2(each)

    read_template_stream = pdfrw.PdfReader(fdata=template_with_radiobutton_stream)

    for each in template.iterate_elements(read_template_stream):
        assert type_mapping[
            template.get_element_key_v2(each)
        ] == template.get_element_type_v2(each)


def test_build_elements(template_with_radiobutton_stream, data_dict):
    for k, v in template_middleware.build_elements(
        template_with_radiobutton_stream
    ).items():
        if k in data_dict and k == v.name:
            data_dict[k] = True

    for k in data_dict.keys():
        assert data_dict[k]


def test_build_elements_v2(template_with_radiobutton_stream, data_dict):
    for k, v in template_middleware.build_elements_v2(
        template_with_radiobutton_stream
    ).items():
        if k in data_dict and k == v.name:
            data_dict[k] = True

    for k in data_dict.keys():
        assert data_dict[k]


def test_build_elements_sejda(sejda_template, sejda_data):
    data_dict = {key: False for key in sejda_data.keys()}

    for k, v in template_middleware.build_elements(sejda_template, sejda=True).items():
        if k in data_dict and k == v.name:
            data_dict[k] = True

    for k in data_dict.keys():
        assert data_dict[k]


def test_build_elements_v2_sejda(sejda_template, sejda_data):
    data_dict = {key: False for key in sejda_data.keys()}

    for k, v in template_middleware.build_elements_v2(sejda_template).items():
        if k in data_dict and k == v.name:
            data_dict[k] = True

    for k in data_dict.keys():
        assert data_dict[k]


def test_build_elements_v2_with_comb_text_field(
    sample_template_with_max_length_text_field, sample_template_with_comb_text_field
):
    result = template_middleware.build_elements_v2(
        sample_template_with_max_length_text_field
    )
    assert result["LastName"].max_length == 8
    assert result["LastName"].comb is None

    result = template_middleware.build_elements_v2(sample_template_with_comb_text_field)
    assert result["LastName"].max_length == 7
    assert result["LastName"].comb is True


def test_get_draw_checkbox_radio_coordinates(sejda_template):
    for element in template.iterate_elements(sejda_template):
        assert template.get_draw_checkbox_radio_coordinates(element) == (
            (
                float(element[constants.ANNOTATION_RECTANGLE_KEY][0])
                + float(element[constants.ANNOTATION_RECTANGLE_KEY][2])
            )
            / 2
            - 5,
            (
                float(element[constants.ANNOTATION_RECTANGLE_KEY][1])
                + float(element[constants.ANNOTATION_RECTANGLE_KEY][3])
            )
            / 2
            - 4,
        )


def test_assign_uuid(template_with_radiobutton_stream, data_dict):
    for element in template.iterate_elements(
        template.assign_uuid(template_with_radiobutton_stream)
    ):
        key = template.get_element_key(element)
        assert constants.SEPARATOR in key

        key, _uuid = key.split(constants.SEPARATOR)

        assert len(_uuid) == len(uuid.uuid4().hex)
        data_dict[key] = True

    for k in data_dict.keys():
        assert data_dict[k]


def test_traverse_pattern(template_with_radiobutton_stream):
    _data_dict = {
        "test": "text",
        "check": "check",
        "radio_1": "radio",
        "test_2": "text",
        "check_2": "check",
        "radio_2": "radio",
        "test_3": "text",
        "check_3": "check",
        "radio_3": "radio",
    }

    type_to_pattern = {
        "text": {constants.ANNOTATION_FIELD_KEY: True},
        "check": {constants.ANNOTATION_FIELD_KEY: True},
        "radio": {constants.PARENT_KEY: {constants.ANNOTATION_FIELD_KEY: True}},
    }

    for each in template.iterate_elements(template_with_radiobutton_stream):
        key = template.get_element_key(each)
        pattern = type_to_pattern[_data_dict[key]]
        assert template.traverse_pattern(pattern, each)[1:-1] == key


def test_traverse_pattern_sejda(sejda_template):
    pattern = {constants.PARENT_KEY: {constants.ANNOTATION_FIELD_KEY: True}}

    for each in template.iterate_elements(sejda_template):
        key = template.get_element_key(each)
        assert template.traverse_pattern(pattern, each)[1:-1] == key


def test_find_pattern_match(template_with_radiobutton_stream):
    _data_dict = {
        "test": "text",
        "check": "check",
        "radio_1": "radio",
        "test_2": "text",
        "check_2": "check",
        "radio_2": "radio",
        "test_3": "text",
        "check_3": "check",
        "radio_3": "radio",
    }

    type_to_pattern = {
        "text": ({constants.ELEMENT_TYPE_KEY: constants.TEXT_FIELD_IDENTIFIER},),
        "check": ({constants.ELEMENT_TYPE_KEY: constants.SELECTABLE_IDENTIFIER},),
        "radio": (
            {
                constants.PARENT_KEY: {
                    constants.ELEMENT_TYPE_KEY: constants.SELECTABLE_IDENTIFIER
                }
            },
        ),
    }

    for each in template.iterate_elements(template_with_radiobutton_stream):
        key = template.get_element_key(each)
        patterns = type_to_pattern[_data_dict[key]]
        check = True
        for pattern in patterns:
            check = check and template.find_pattern_match(pattern, each)
        assert check


def test_find_pattern_match_sejda(sejda_template, sejda_data):
    _data_dict = {}
    for key, value in sejda_data.items():
        _type = None
        if isinstance(value, str):
            _type = "text"
        if isinstance(value, int):
            _type = "radio"
        if isinstance(value, bool):
            _type = "check"
        _data_dict[key] = _type

    type_to_pattern = {
        "text": (
            {
                constants.PARENT_KEY: {
                    constants.ELEMENT_TYPE_KEY: constants.TEXT_FIELD_IDENTIFIER
                }
            },
        ),
        "check": (
            {
                constants.PARENT_KEY: {
                    constants.ELEMENT_TYPE_KEY: constants.SELECTABLE_IDENTIFIER
                }
            },
            {
                constants.PARENT_KEY: {
                    constants.SUBTYPE_KEY: constants.WIDGET_SUBTYPE_KEY
                }
            },
        ),
        "radio": (
            {
                constants.PARENT_KEY: {
                    constants.ELEMENT_TYPE_KEY: constants.SELECTABLE_IDENTIFIER
                }
            },
        ),
    }

    for each in template.iterate_elements(sejda_template):
        key = template.get_element_key(each, sejda=True)
        patterns = type_to_pattern[_data_dict[key]]
        check = True
        for pattern in patterns:
            check = check and template.find_pattern_match(pattern, each)
        assert check


def test_get_text_field_max_length(sample_template_with_max_length_text_field):
    for _page, elements in template.get_elements_by_page_v2(
        sample_template_with_max_length_text_field
    ).items():
        for element in elements:
            assert template.get_text_field_max_length(element) is (
                8 if template.get_element_key_v2(element) == "LastName" else None
            )


def test_is_text_field_comb(sample_template_with_comb_text_field):
    for _page, elements in template.get_elements_by_page_v2(
        sample_template_with_comb_text_field
    ).items():
        for element in elements:
            assert template.get_text_field_max_length(element) is (
                7 if template.get_element_key_v2(element) == "LastName" else None
            )
            if template.get_element_key_v2(element) == "LastName":
                assert template.is_text_field_comb(element) is True
