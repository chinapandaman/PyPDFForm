# -*- coding: utf-8 -*-

import os

import pdfrw
import pytest

from PyPDFForm.core.constants import Template as TemplateConstants
from PyPDFForm.core.filler import Filler
from PyPDFForm.core.template import Template as TemplateCore
from PyPDFForm.middleware.constants import Text as TextConstants
from PyPDFForm.middleware.template import Template as TemplateMiddleware


@pytest.fixture
def pdf_samples():
    return os.path.join(os.path.dirname(__file__), "..", "..", "pdf_samples", "v2")


@pytest.fixture
def template_stream(pdf_samples):
    with open(os.path.join(pdf_samples, "sample_template.pdf"), "rb+") as f:
        return f.read()


@pytest.fixture
def template_with_image_stream(pdf_samples):
    with open(os.path.join(pdf_samples, "sample_template_with_image_field.pdf"), "rb+") as f:
        return f.read()


@pytest.fixture
def image_stream(pdf_samples):
    with open(os.path.join(pdf_samples, "sample_image.jpg"), "rb+") as f:
        return f.read()


@pytest.fixture
def image_stream_2(pdf_samples):
    with open(os.path.join(pdf_samples, "sample_image_2.jpg"), "rb+") as f:
        return f.read()


@pytest.fixture
def image_stream_3(pdf_samples):
    with open(os.path.join(pdf_samples, "sample_image_3.jpg"), "rb+") as f:
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


def test_simple_fill_with_image(template_with_image_stream, data_dict, image_stream, image_stream_2, image_stream_3):
    comparing_stream = Filler().simple_fill(template_with_image_stream, data_dict, True)

    data_dict["image_1"] = image_stream
    data_dict["image_2"] = image_stream_2
    data_dict["image_3"] = image_stream_3

    result_stream = Filler().simple_fill(template_with_image_stream, data_dict, True)

    assert result_stream != template_with_image_stream
    assert result_stream != comparing_stream

    for element in TemplateCore().iterate_elements(result_stream):
        key = TemplateCore().get_element_key(element)

        if isinstance(data_dict[key], bool):
            assert element[TemplateConstants().checkbox_field_value_key] == (
                pdfrw.PdfName.Yes if data_dict[key] else pdfrw.PdfName.Off
            )
        elif isinstance(data_dict[key], bytes):
            assert element[TemplateConstants().field_editable_key] == pdfrw.PdfObject(1)
            continue
        else:
            assert (
                element[TemplateConstants().text_field_value_key][1:-1]
                == data_dict[key]
            )
        assert element[TemplateConstants().field_editable_key] != pdfrw.PdfObject(1)
