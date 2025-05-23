# -*- coding: utf-8 -*-

import os

from PyPDFForm import PdfWrapper
from PyPDFForm.middleware.base import Widget
from PyPDFForm.middleware.text import Text


def test_base_schema_definition():
    assert Widget("foo").schema_definition == {}


def test_fill(template_stream, pdf_samples, data_dict, request):
    expected_path = os.path.join(pdf_samples, "test_fill.pdf")
    with open(expected_path, "rb+") as f:
        obj = PdfWrapper(template_stream).fill(
            data_dict,
        )

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()
        assert len(obj.read()) == len(obj.read())
        assert obj.read() == obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


def test_fill_flatten(template_stream, pdf_samples, data_dict, request):
    expected_path = os.path.join(pdf_samples, "test_fill_flatten.pdf")
    with open(expected_path, "rb+") as f:
        obj = PdfWrapper(template_stream).fill(data_dict, flatten=True)

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()
        assert len(obj.read()) == len(obj.read())
        assert obj.read() == obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


def test_fill_adobe_mode(template_stream, pdf_samples, data_dict, request):
    expected_path = os.path.join(pdf_samples, "test_fill_adobe_mode.pdf")
    with open(expected_path, "rb+") as f:
        obj = PdfWrapper(template_stream).fill(data_dict, adobe_mode=True)

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()
        assert len(obj.read()) == len(obj.read())
        assert obj.read() == obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


def test_register_bad_fonts():
    assert not PdfWrapper().register_font("foo", b"foo").read()
    assert not PdfWrapper().register_font("foo", "foo").read()


def test_register_global_font_fill(
    template_stream, pdf_samples, samle_font_stream, data_dict, request
):
    expected_path = os.path.join(pdf_samples, "test_register_global_font_fill.pdf")
    with open(
        expected_path,
        "rb+",
    ) as f:
        obj = PdfWrapper(template_stream).register_font(
            "new_font",
            samle_font_stream,
        )
        for v in obj.widgets.values():
            if isinstance(v, Text):
                v.font = "new_font"
        obj.fill(
            data_dict,
        )

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


def test_register_global_font_fill_flatten(
    template_stream, pdf_samples, samle_font_stream, data_dict, request
):
    expected_path = os.path.join(
        pdf_samples, "test_register_global_font_fill_flatten.pdf"
    )
    with open(
        expected_path,
        "rb+",
    ) as f:
        obj = PdfWrapper(template_stream).register_font(
            "new_font",
            samle_font_stream,
        )
        for v in obj.widgets.values():
            if isinstance(v, Text):
                v.font = "new_font"
        obj.fill(
            data_dict,
            flatten=True,
        )

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


def test_register_global_font_fill_adobe_mode(
    template_stream, pdf_samples, samle_font_stream, data_dict, request
):
    expected_path = os.path.join(
        pdf_samples, "test_register_global_font_fill_adobe_mode.pdf"
    )
    with open(
        expected_path,
        "rb+",
    ) as f:
        obj = PdfWrapper(template_stream).register_font(
            "new_font",
            samle_font_stream,
        )
        for v in obj.widgets.values():
            if isinstance(v, Text):
                v.font = "new_font"
        obj.fill(
            data_dict,
            adobe_mode=True,
        )

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected
