# -*- coding: utf-8 -*-

import os

from PyPDFForm import PdfWrapper


def test_create_text(pdf_samples, sample_font_stream, request):
    expected_path = os.path.join(pdf_samples, "docs", "test_create_text.pdf")

    new_form = (
        PdfWrapper(os.path.join(pdf_samples, "dummy.pdf"))
        .register_font(
            "your_registered_font",
            sample_font_stream,
        )
        .create_widget(
            widget_type="text",
            name="new_text_field",
            page_number=1,
            x=57,
            y=700,
            required=False,  # optional
            tooltip="this is a text field",  # optional
            width=120,  # optional
            height=40,  # optional
            max_length=10,  # optional
            comb=True,  # optional, when set to True, max_length must also be set
            font="your_registered_font",  # optional
            font_size=15,  # optional
            font_color=(0, 1, 0),  # optional
            bg_color=(0, 0, 1, 1),  # optional, (r, g, b, alpha)
            border_color=(1, 0, 0, 1),  # optional, (r, g, b, alpha)
            border_width=5,  # optional
            alignment=2,  # optional, 0=left, 1=center, 2=right
            multiline=False,  # optional
        )
    )

    request.config.results["expected_path"] = expected_path
    request.config.results["stream"] = new_form.read()

    with open(expected_path, "rb+") as f:
        expected = f.read()

        assert len(new_form.read()) == len(expected)
        assert new_form.read() == expected


def test_create_check(pdf_samples, request):
    expected_path = os.path.join(pdf_samples, "docs", "test_create_check.pdf")

    new_form = PdfWrapper(os.path.join(pdf_samples, "dummy.pdf")).create_widget(
        widget_type="checkbox",
        name="new_checkbox",
        page_number=1,
        x=57,
        y=700,
        required=False,  # optional
        tooltip="this is a checkbox",  # optional
        size=50,  # optional
        button_style="cross",  # optional
        tick_color=(0, 1, 0),  # optional
        bg_color=(0, 0, 1, 1),  # optional, (r, g, b, alpha)
        border_color=(1, 0, 0, 1),  # optional, (r, g, b, alpha)
        border_width=5,  # optional
    )

    request.config.results["expected_path"] = expected_path
    request.config.results["stream"] = new_form.read()

    with open(expected_path, "rb+") as f:
        expected = f.read()

        assert len(new_form.read()) == len(expected)
        assert new_form.read() == expected


def test_create_radio(pdf_samples, request):
    expected_path = os.path.join(pdf_samples, "docs", "test_create_radio.pdf")

    new_form = PdfWrapper(os.path.join(pdf_samples, "dummy.pdf")).create_widget(
        widget_type="radio",
        name="new_radio_group",
        page_number=1,
        x=[50, 100, 150],
        y=[50, 100, 150],
        required=False,  # optional
        tooltip="this is a radio group",  # optional
        size=40,  # optional
        button_style="circle",  # optional
        shape="square",  # optional, circle or square
        tick_color=(0, 1, 0),  # optional
        bg_color=(0, 0, 1, 1),  # optional, (r, g, b, alpha)
        border_color=(1, 0, 0, 1),  # optional, (r, g, b, alpha)
        border_width=5,  # optional
    )

    request.config.results["expected_path"] = expected_path
    request.config.results["stream"] = new_form.read()

    with open(expected_path, "rb+") as f:
        expected = f.read()

        assert len(new_form.read()) == len(expected)
        assert new_form.read() == expected


def test_create_dropdown(pdf_samples, sample_font_stream, request):
    expected_path = os.path.join(pdf_samples, "docs", "test_create_dropdown.pdf")

    new_form = (
        PdfWrapper(os.path.join(pdf_samples, "dummy.pdf"))
        .register_font("your_registered_font", sample_font_stream)
        .create_widget(
            widget_type="dropdown",
            name="new_dropdown",
            page_number=1,
            x=57,
            y=700,
            options=[
                "foo",
                "bar",
                "foobar",
            ],
            required=False,  # optional
            tooltip="this is a dropdown",  # optional
            width=120,  # optional
            height=40,  # optional
            font="your_registered_font",  # optional
            font_size=15,  # optional
            font_color=(0, 1, 0),  # optional
            bg_color=(0, 0, 1, 1),  # optional, (r, g, b, alpha)
            border_color=(1, 0, 0, 1),  # optional, (r, g, b, alpha)
            border_width=5,  # optional
        )
    )

    request.config.results["expected_path"] = expected_path
    request.config.results["stream"] = new_form.read()

    with open(expected_path, "rb+") as f:
        expected = f.read()

        assert len(new_form.read()) == len(expected)
        assert new_form.read() == expected


def test_create_dropdown_with_export_values(pdf_samples, request):
    expected_path = os.path.join(
        pdf_samples, "docs", "test_create_dropdown_with_export_values.pdf"
    )

    new_form = PdfWrapper(os.path.join(pdf_samples, "dummy.pdf")).create_widget(
        widget_type="dropdown",
        name="new_dropdown",
        page_number=1,
        x=57,
        y=700,
        options=[
            ("option_1", "option_1_export_value"),
            ("option_2", "option_2_export_value"),
            ("option_3", "option_3_export_value"),
        ],
    )

    request.config.results["expected_path"] = expected_path
    request.config.results["stream"] = new_form.read()

    with open(expected_path, "rb+") as f:
        expected = f.read()

        assert len(new_form.read()) == len(expected)
        assert new_form.read() == expected


def test_create_sig(pdf_samples, request):
    expected_path = os.path.join(pdf_samples, "docs", "test_create_sig.pdf")

    new_form = PdfWrapper(os.path.join(pdf_samples, "dummy.pdf")).create_widget(
        widget_type="signature",
        name="new_signature",
        page_number=1,
        x=100,
        y=100,
        required=False,  # optional
        tooltip="this is a signature",  # optional
        width=410,  # optional
        height=100,  # optional
    )

    request.config.results["expected_path"] = expected_path
    request.config.results["stream"] = new_form.read()

    with open(expected_path, "rb+") as f:
        expected = f.read()

        assert len(new_form.read()) == len(expected)
        assert new_form.read() == expected


def test_create_image(pdf_samples, request):
    expected_path = os.path.join(pdf_samples, "docs", "test_create_image.pdf")

    new_form = PdfWrapper(os.path.join(pdf_samples, "dummy.pdf")).create_widget(
        widget_type="image",
        name="new_image",
        page_number=1,
        x=100,
        y=100,
        required=False,  # optional
        tooltip="this is an image",  # optional
        width=192,  # optional
        height=108,  # optional
    )

    request.config.results["expected_path"] = expected_path
    request.config.results["stream"] = new_form.read()

    with open(expected_path, "rb+") as f:
        expected = f.read()

        assert len(new_form.read()) == len(expected)
        assert new_form.read() == expected


def test_update_key(static_pdfs):
    new_form = PdfWrapper(os.path.join(static_pdfs, "sample_template.pdf"))
    assert "test" in new_form.widgets
    new_form.update_widget_key("test", "test_text")
    assert "test" not in new_form.widgets
    assert "test_text" in new_form.widgets


def test_update_key_index(pdf_samples, static_pdfs, request):
    expected_path = os.path.join(pdf_samples, "docs", "test_update_key_index.pdf")

    new_form = PdfWrapper(os.path.join(static_pdfs, "733.pdf")).update_widget_key(
        "Description[0]", "Description[1]", index=1
    )

    new_form.fill(new_form.sample_data)

    request.config.results["expected_path"] = expected_path
    request.config.results["stream"] = new_form.read()

    with open(expected_path, "rb+") as f:
        expected = f.read()

        assert len(new_form.read()) == len(expected)
        assert new_form.read() == expected


def test_update_key_bulk(pdf_samples, static_pdfs, request):
    expected_path = os.path.join(pdf_samples, "docs", "test_update_key_bulk.pdf")

    new_form = PdfWrapper(os.path.join(static_pdfs, "733.pdf"))
    for i in range(1, 10):
        new_form.update_widget_key(
            "Description[0]", f"Description[{i}]", index=1, defer=True
        )
    new_form.commit_widget_key_updates()

    new_form.fill(new_form.sample_data)

    request.config.results["expected_path"] = expected_path
    request.config.results["stream"] = new_form.read()

    with open(expected_path, "rb+") as f:
        expected = f.read()

        assert len(new_form.read()) == len(expected)
        assert new_form.read() == expected
