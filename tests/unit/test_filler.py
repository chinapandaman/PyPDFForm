# -*- coding: utf-8 -*-

import os

import pdfrw
import pytest
from pdfrw.objects.pdfname import BasePdfName

from PyPDFForm.core.constants import Template as TemplateConstants
from PyPDFForm.core.filler import Filler
from PyPDFForm.core.template import Template as TemplateCore
from PyPDFForm.middleware.constants import Text as TextConstants
from PyPDFForm.middleware.element import ElementType
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
        "test": "test_1",
        "check": True,
        "test_2": "test_2",
        "check_2": False,
        "test_3": "test_3",
        "check_3": True,
    }


def test_fill(template_stream, data_dict):
    elements = TemplateMiddleware().build_elements(template_stream)

    for k, v in data_dict.items():
        if k in elements:
            elements[k].value = v

            if elements[k].type == ElementType.text:
                elements[k].font = TextConstants().global_font
                elements[k].font_size = TextConstants().global_font_size
                elements[k].font_color = TextConstants().global_font_color
                elements[k].text_x_offset = TextConstants().global_text_x_offset
                elements[k].text_y_offset = TextConstants().global_text_y_offset
                elements[k].text_wrap_length = TextConstants().global_text_wrap_length
            elements[k].validate_constants()
            elements[k].validate_value()
            elements[k].validate_text_attributes()

    result_stream = Filler().fill(template_stream, elements)

    assert result_stream != template_stream

    for element in TemplateCore().iterate_elements(result_stream):
        key = TemplateCore().get_element_key(element)

        assert element[TemplateConstants().field_editable_key] == pdfrw.PdfObject(1)

        if isinstance(data_dict[key], bool):
            assert element[TemplateConstants().checkbox_field_value_key] == (
                pdfrw.PdfName.Yes if data_dict[key] else pdfrw.PdfName.Off
            )


def test_fill_with_radiobutton(template_with_radiobutton_stream, data_dict):
    elements = TemplateMiddleware().build_elements(template_with_radiobutton_stream)

    data_dict["radio_1"] = 0
    data_dict["radio_2"] = 1
    data_dict["radio_3"] = 2

    radio_button_tracker = {}

    for k, v in data_dict.items():
        if k in elements:
            elements[k].value = v

            if elements[k].type == ElementType.text:
                elements[k].font = TextConstants().global_font
                elements[k].font_size = TextConstants().global_font_size
                elements[k].font_color = TextConstants().global_font_color
                elements[k].text_x_offset = TextConstants().global_text_x_offset
                elements[k].text_y_offset = TextConstants().global_text_y_offset
                elements[k].text_wrap_length = TextConstants().global_text_wrap_length
            elements[k].validate_constants()
            elements[k].validate_value()
            elements[k].validate_text_attributes()

    result_stream = Filler().fill(template_with_radiobutton_stream, elements)

    assert result_stream != template_with_radiobutton_stream

    for element in TemplateCore().iterate_elements(result_stream):
        key = TemplateCore().get_element_key(element)

        if isinstance(data_dict[key], bool) or isinstance(data_dict[key], str):
            assert element[TemplateConstants().field_editable_key] == pdfrw.PdfObject(1)
        else:
            assert element[TemplateConstants().parent_key][
                TemplateConstants().field_editable_key
            ] == pdfrw.PdfObject(1)

        if isinstance(data_dict[key], bool):
            assert element[TemplateConstants().checkbox_field_value_key] == (
                pdfrw.PdfName.Yes if data_dict[key] else pdfrw.PdfName.Off
            )
        elif isinstance(data_dict[key], int):
            if key not in radio_button_tracker:
                radio_button_tracker[key] = 0
            radio_button_tracker[key] += 1

            if data_dict[key] == radio_button_tracker[key] - 1:
                assert element[
                    TemplateConstants().checkbox_field_value_key
                ] == BasePdfName("/" + str(data_dict[key]), False)
            else:
                assert (
                    element[TemplateConstants().checkbox_field_value_key]
                    == pdfrw.PdfName.Off
                )


def test_simple_fill(template_stream, data_dict):
    result_stream = Filler().simple_fill(template_stream, data_dict, False)

    assert result_stream != template_stream

    for element in TemplateCore().iterate_elements(result_stream):
        key = TemplateCore().get_element_key(element)

        if isinstance(data_dict[key], bool):
            assert element[TemplateConstants().checkbox_field_value_key] == (
                pdfrw.PdfName.Yes if data_dict[key] else pdfrw.PdfName.Off
            )
        else:
            assert (
                element[TemplateConstants().text_field_value_key][1:-1]
                == data_dict[key]
            )
        assert element[TemplateConstants().field_editable_key] == pdfrw.PdfObject(1)


def test_simple_fill_with_radiobutton(template_with_radiobutton_stream, data_dict):
    data_dict["radio_1"] = 0
    data_dict["radio_2"] = 1
    data_dict["radio_3"] = 2

    radio_button_tracker = {}

    result_stream = Filler().simple_fill(
        template_with_radiobutton_stream, data_dict, True
    )

    assert result_stream != template_with_radiobutton_stream

    for element in TemplateCore().iterate_elements(result_stream):
        key = TemplateCore().get_element_key(element)

        if isinstance(data_dict[key], bool):
            assert element[TemplateConstants().checkbox_field_value_key] == (
                pdfrw.PdfName.Yes if data_dict[key] else pdfrw.PdfName.Off
            )
        elif isinstance(data_dict[key], int):
            if key not in radio_button_tracker:
                radio_button_tracker[key] = 0
            radio_button_tracker[key] += 1

            if data_dict[key] == radio_button_tracker[key] - 1:
                assert element[
                    TemplateConstants().checkbox_field_value_key
                ] == BasePdfName("/" + str(data_dict[key]), False)
            else:
                assert (
                    element[TemplateConstants().checkbox_field_value_key]
                    == pdfrw.PdfName.Off
                )
        else:
            assert (
                element[TemplateConstants().text_field_value_key][1:-1]
                == data_dict[key]
            )
        assert element[TemplateConstants().field_editable_key] != pdfrw.PdfObject(1)
