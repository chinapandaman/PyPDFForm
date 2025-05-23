# -*- coding: utf-8 -*-

import os

from PyPDFForm import PdfWrapper


def test_create_not_supported_type_not_working(template_stream):
    obj = PdfWrapper(template_stream)
    stream = obj.read()
    assert (
        obj.create_widget(
            "foo",
            "foo",
            1,
            100,
            100,
        ).read()
        == stream
    )


def test_create_checkbox_default(template_stream, pdf_samples, request):
    expected_path = os.path.join(pdf_samples, "widget", "test_create_checkbox_default.pdf")
    with open(expected_path, "rb+") as f:
        obj = PdfWrapper(template_stream).create_widget(
            "checkbox",
            "foo",
            1,
            100,
            100,
        )
        assert obj.schema["properties"]["foo"]["type"] == "boolean"

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


def test_create_checkbox_default_filled(template_stream, pdf_samples, request):
    expected_path = os.path.join(
        pdf_samples, "widget", "test_create_checkbox_default_filled.pdf"
    )
    with open(expected_path, "rb+") as f:
        obj = PdfWrapper(template_stream).create_widget(
            "checkbox",
            "foo",
            1,
            100,
            100,
        )
        obj.fill(obj.sample_data)

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


def test_create_checkbox_default_filled_flatten(template_stream, pdf_samples, request):
    expected_path = os.path.join(
        pdf_samples, "widget", "test_create_checkbox_default_filled_flatten.pdf"
    )
    with open(expected_path, "rb+") as f:
        obj = PdfWrapper(template_stream).create_widget(
            "checkbox",
            "foo",
            1,
            100,
            100,
        )
        obj.fill(obj.sample_data, flatten=True)

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


def test_create_checkbox_complex(template_stream, pdf_samples, request):
    expected_path = os.path.join(pdf_samples, "widget", "test_create_checkbox_complex.pdf")
    with open(expected_path, "rb+") as f:
        obj = PdfWrapper(template_stream).create_widget(
            "checkbox",
            "foo",
            1,
            100,
            100,
            size=100,
            button_style="check",
            tick_color=(0, 1, 0),
            bg_color=(0, 0, 1),
            border_color=(1, 0, 0),
            border_width=5,
        )

        assert obj.schema["properties"]["foo"]["type"] == "boolean"

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


def test_create_checkbox_complex_fill(template_stream, pdf_samples, request):
    expected_path = os.path.join(pdf_samples, "widget", "test_create_checkbox_complex_fill.pdf")
    with open(expected_path, "rb+") as f:
        obj = PdfWrapper(template_stream).create_widget(
            "checkbox",
            "foo",
            1,
            100,
            100,
            size=100,
            button_style="check",
            tick_color=(0, 1, 0),
            bg_color=(0, 0, 1),
            border_color=(1, 0, 0),
            border_width=5,
        )
        obj.fill(obj.sample_data)

        assert obj.schema["properties"]["foo"]["type"] == "boolean"

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


def test_create_checkbox_complex_fill_flatten(template_stream, pdf_samples, request):
    expected_path = os.path.join(pdf_samples, "widget", "test_create_checkbox_complex_fill_flatten.pdf")
    with open(expected_path, "rb+") as f:
        obj = PdfWrapper(template_stream).create_widget(
            "checkbox",
            "foo",
            1,
            100,
            100,
            size=100,
            button_style="check",
            tick_color=(0, 1, 0),
            bg_color=(0, 0, 1),
            border_color=(1, 0, 0),
            border_width=5,
        )
        obj.fill(obj.sample_data, flatten=True)

        assert obj.schema["properties"]["foo"]["type"] == "boolean"

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


def test_create_checkbox_check_fill(template_stream, pdf_samples, request):
    expected_path = os.path.join(pdf_samples, "widget", "test_create_checkbox_check_fill.pdf")
    with open(expected_path, "rb+") as f:
        obj = PdfWrapper(template_stream).create_widget(
            "checkbox",
            "foo",
            1,
            100,
            100,
            button_style="check",
        )
        obj.fill(obj.sample_data)

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


def test_create_checkbox_check_fill_flatten(template_stream, pdf_samples, request):
    expected_path = os.path.join(pdf_samples, "widget", "test_create_checkbox_check_fill_flatten.pdf")
    with open(expected_path, "rb+") as f:
        obj = PdfWrapper(template_stream).create_widget(
            "checkbox",
            "foo",
            1,
            100,
            100,
            button_style="check",
        )
        obj.fill(obj.sample_data, flatten=True)

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected
