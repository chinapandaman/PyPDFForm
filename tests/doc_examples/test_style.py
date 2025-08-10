# -*- coding: utf-8 -*-

import os

from PyPDFForm import PdfWrapper, Text


def test_change_text_font(static_pdfs, sample_font_stream, pdf_samples, request):
    expected_path = os.path.join(pdf_samples, "docs", "test_change_text_font.pdf")

    form = PdfWrapper(os.path.join(static_pdfs, "sample_template.pdf"))
    form.register_font("new_font_name", sample_font_stream)

    # change globally by iterating each text field
    for field in form.widgets.values():
        if isinstance(field, Text):
            field.font = "new_font_name"

    # or change at each field's widget level
    form.widgets["test"].font = "new_font_name"

    form.fill(
        {
            "test": "test_1",
            "check": True,
            "test_2": "test_2",
            "check_2": False,
            "test_3": "test_3",
            "check_3": True,
        },
    )

    request.config.results["expected_path"] = expected_path
    request.config.results["stream"] = form.read()

    with open(expected_path, "rb+") as f:
        expected = f.read()

        assert len(form.read()) == len(expected)
        assert form.read() == expected


def test_change_text_font_size(static_pdfs, pdf_samples, request):
    expected_path = os.path.join(pdf_samples, "docs", "test_change_text_font_size.pdf")

    form = PdfWrapper(os.path.join(static_pdfs, "sample_template.pdf"))

    # change globally by iterating each text field
    for field in form.widgets.values():
        if isinstance(field, Text):
            field.font_size = 20

    # or change at each field's widget level
    form.widgets["test"].font_size = 30.5

    form.fill(
        {
            "test": "test_1",
            "check": True,
            "test_2": "test_2",
            "check_2": False,
            "test_3": "test_3",
            "check_3": True,
        },
    )

    request.config.results["expected_path"] = expected_path
    request.config.results["stream"] = form.read()

    with open(expected_path, "rb+") as f:
        expected = f.read()

        assert len(form.read()) == len(expected)
        assert form.read() == expected


def test_change_text_font_color(static_pdfs, pdf_samples, request):
    expected_path = os.path.join(pdf_samples, "docs", "test_change_text_font_color.pdf")

    form = PdfWrapper(os.path.join(static_pdfs, "sample_template.pdf"))

    # change globally by iterating each text field
    for field in form.widgets.values():
        if isinstance(field, Text):
            field.font_color = (1, 0, 0)

    # or change at each field's widget level
    form.widgets["test"].font_color = (0.2, 0, 0.5)

    form.fill(
        {
            "test": "test_1",
            "check": True,
            "test_2": "test_2",
            "check_2": False,
            "test_3": "test_3",
            "check_3": True,
        },
    )

    request.config.results["expected_path"] = expected_path
    request.config.results["stream"] = form.read()

    with open(expected_path, "rb+") as f:
        expected = f.read()

        assert len(form.read()) == len(expected)
        assert form.read() == expected


def test_change_text_alignment(static_pdfs, pdf_samples, request):
    expected_path = os.path.join(pdf_samples, "docs", "test_change_text_alignment.pdf")

    form = PdfWrapper(os.path.join(static_pdfs, "sample_template.pdf"))

    # change globally by iterating each text field
    for field in form.widgets.values():
        if isinstance(field, Text):
            field.alignment = 1  # center

    # or change at each field's widget level
    form.widgets["test"].alignment = 2  # right

    form.fill(
        {
            "test": "test_1",
            "check": True,
            "test_2": "test_2",
            "check_2": False,
            "test_3": "test_3",
            "check_3": True,
        },
    )

    request.config.results["expected_path"] = expected_path
    request.config.results["stream"] = form.read()

    with open(expected_path, "rb+") as f:
        expected = f.read()

        assert len(form.read()) == len(expected)
        assert form.read() == expected


def test_change_text_max_length(static_pdfs, pdf_samples, request):
    expected_path = os.path.join(pdf_samples, "docs", "test_change_text_max_length.pdf")

    form = PdfWrapper(os.path.join(static_pdfs, "sample_template.pdf"))

    # change globally by iterating each text field
    for field in form.widgets.values():
        if isinstance(field, Text):
            field.max_length = 4

    # or change at each field's widget level
    form.widgets["test"].max_length = 2

    form.fill(
        {
            "test": "test_1",
            "check": True,
            "test_2": "test_2",
            "check_2": False,
            "test_3": "test_3",
            "check_3": True,
        },
    )

    request.config.results["expected_path"] = expected_path
    request.config.results["stream"] = form.read()

    with open(expected_path, "rb+") as f:
        expected = f.read()

        assert len(form.read()) == len(expected)
        assert form.read() == expected


def test_change_text_comb(static_pdfs, pdf_samples, request):
    expected_path = os.path.join(pdf_samples, "docs", "test_change_text_comb.pdf")

    form = PdfWrapper(os.path.join(static_pdfs, "sample_template.pdf"))

    # change globally by iterating each text field
    for field in form.widgets.values():
        if isinstance(field, Text):
            field.max_length = 4
            field.comb = True

    # or change at each field's widget level
    form.widgets["test"].max_length = 2
    form.widgets["test"].comb = True

    form.fill(
        {
            "test": "test_1",
            "check": True,
            "test_2": "test_2",
            "check_2": False,
            "test_3": "test_3",
            "check_3": True,
        },
    )

    request.config.results["expected_path"] = expected_path
    request.config.results["stream"] = form.read()

    with open(expected_path, "rb+") as f:
        expected = f.read()

        assert len(form.read()) == len(expected)
        assert form.read() == expected


def test_change_text_multiline(static_pdfs, pdf_samples, request):
    expected_path = os.path.join(pdf_samples, "docs", "test_change_text_multiline.pdf")

    form = PdfWrapper(os.path.join(static_pdfs, "sample_template.pdf"))

    form.widgets["test"].multiline = True

    form.fill(
        {
            "test": "test_1\ntest_1",
            "check": True,
            "test_2": "test_2\ntest_2",
            "check_2": False,
            "test_3": "test_3\ntest_3",
            "check_3": True,
        },
    )

    request.config.results["expected_path"] = expected_path
    request.config.results["stream"] = form.read()

    with open(expected_path, "rb+") as f:
        expected = f.read()

        assert len(form.read()) == len(expected)
        assert form.read() == expected


def test_change_check_size(static_pdfs, pdf_samples, request):
    expected_path = os.path.join(pdf_samples, "docs", "test_change_check_size.pdf")

    form = PdfWrapper(os.path.join(static_pdfs, "sample_template.pdf"))

    form.widgets["check"].size = 50
    form.widgets["check_2"].size = 40
    form.widgets["check_3"].size = 60

    form.fill(
        {
            "check": True,
            "check_2": True,
            "check_3": True,
        },
    )

    request.config.results["expected_path"] = expected_path
    request.config.results["stream"] = form.read()

    with open(expected_path, "rb+") as f:
        expected = f.read()

        assert len(form.read()) == len(expected)
        assert form.read() == expected


def test_change_dropdown_choices(static_pdfs, pdf_samples, request):
    expected_path = os.path.join(
        pdf_samples, "docs", "test_change_dropdown_choices.pdf"
    )

    form = PdfWrapper(os.path.join(static_pdfs, "sample_template_with_dropdown.pdf"))

    form.widgets["dropdown_1"].choices = ["", "apple", "banana", "cherry", "dates"]

    request.config.results["expected_path"] = expected_path
    request.config.results["stream"] = form.read()

    with open(expected_path, "rb+") as f:
        expected = f.read()

        assert len(form.read()) == len(expected)
        assert form.read() == expected


def test_change_dropdown_choices_with_export_values(static_pdfs, pdf_samples, request):
    expected_path = os.path.join(
        pdf_samples, "docs", "test_change_dropdown_choices_with_export_values.pdf"
    )

    form = PdfWrapper(os.path.join(static_pdfs, "sample_template_with_dropdown.pdf"))

    form.widgets["dropdown_1"].choices = [
        ("", "blank_export_value"),
        ("apple", "apple_export_value"),
        ("banana", "banana_export_value"),
        ("cherry", "cherry_export_value"),
        ("dates", "dates_export_value"),
    ]

    request.config.results["expected_path"] = expected_path
    request.config.results["stream"] = form.read()

    with open(expected_path, "rb+") as f:
        expected = f.read()

        assert len(form.read()) == len(expected)
        assert form.read() == expected


def test_change_dropdown_font(static_pdfs, pdf_samples, sample_font_stream, request):
    expected_path = os.path.join(pdf_samples, "docs", "test_change_dropdown_font.pdf")

    form = PdfWrapper(os.path.join(static_pdfs, "sample_template_with_dropdown.pdf"))

    form.register_font("new_font_name", sample_font_stream)

    form.widgets["dropdown_1"].font = "new_font_name"

    request.config.results["expected_path"] = expected_path
    request.config.results["stream"] = form.read()

    with open(expected_path, "rb+") as f:
        expected = f.read()

        assert len(form.read()) == len(expected)
        assert form.read() == expected


def test_change_field_editability(static_pdfs, pdf_samples, request):
    expected_path = os.path.join(
        pdf_samples, "docs", "test_change_field_editability.pdf"
    )

    form = PdfWrapper(os.path.join(static_pdfs, "sample_template_with_dropdown.pdf"))

    form.fill(
        {
            "test_1": "test_1",
            "test_2": "test_2",
            "test_3": "test_3",
            "check_1": True,
            "check_2": True,
            "check_3": True,
            "radio_1": 1,
            "dropdown_1": 0,
        },
        flatten=True,
    )
    form.widgets["test_2"].readonly = False  # text
    form.widgets["check_3"].readonly = False  # checkbox
    form.widgets["radio_1"].readonly = False  # radio button group
    form.widgets["dropdown_1"].readonly = False  # dropdown

    request.config.results["expected_path"] = expected_path
    request.config.results["stream"] = form.read()

    with open(expected_path, "rb+") as f:
        expected = f.read()

        assert len(form.read()) == len(expected)
        assert form.read() == expected
