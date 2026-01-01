# -*- coding: utf-8 -*-

import os

import pytest

from PyPDFForm import PdfWrapper, RawElements


def test_draw_text_on_one_page(template_stream, pdf_samples, request):
    expected_path = os.path.join(pdf_samples, "test_draw_text_on_one_page.pdf")
    with open(expected_path, "rb+") as f:
        obj = PdfWrapper(template_stream).draw(
            [
                RawElements.RawText(
                    "drawn_text",
                    1,
                    300,
                    225,
                    font_size=20,
                    font_color=(1, 0, 0),
                )
            ]
        )

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


def test_draw_multiline_text_on_one_page(template_stream, pdf_samples, request):
    expected_path = os.path.join(
        pdf_samples, "test_draw_multiline_text_on_one_page.pdf"
    )
    with open(expected_path, "rb+") as f:
        obj = PdfWrapper(template_stream).draw(
            [
                RawElements.RawText(
                    "drawn_text\ndrawn_text\ndrawn_text",
                    1,
                    300,
                    225,
                    font_size=20,
                    font_color=(1, 0, 0),
                )
            ]
        )

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


def test_draw_text_on_radio_template(
    template_with_radiobutton_stream, pdf_samples, request
):
    expected_path = os.path.join(pdf_samples, "test_draw_text_on_radio_template.pdf")
    with open(expected_path, "rb+") as f:
        obj = PdfWrapper(template_with_radiobutton_stream).draw(
            [
                RawElements.RawText(
                    "drawn_text",
                    1,
                    300,
                    225,
                    font_size=20,
                    font_color=(1, 0, 0),
                )
            ]
        )

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


def test_draw_text_on_sejda_template(sejda_template, pdf_samples, request):
    expected_path = os.path.join(pdf_samples, "test_draw_text_on_sejda_template.pdf")
    with open(expected_path, "rb+") as f:
        obj = PdfWrapper(sejda_template).draw(
            [
                RawElements.RawText(
                    "drawn_text",
                    1,
                    300,
                    225,
                    font_size=20,
                    font_color=(1, 0, 0),
                )
            ]
        )

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


def test_draw_image_on_one_page(template_stream, image_samples, pdf_samples, request):
    expected_path = os.path.join(pdf_samples, "test_draw_image_on_one_page.pdf")
    with open(expected_path, "rb+") as f:
        with open(os.path.join(image_samples, "sample_image.jpg"), "rb+") as _f:
            obj = PdfWrapper(template_stream).draw(
                [
                    RawElements.RawImage(
                        _f,
                        2,
                        100,
                        100,
                        400,
                        225,
                    )
                ]
            )

        expected = f.read()

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()
        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


def test_draw_image_on_radio_template(
    template_with_radiobutton_stream, image_samples, pdf_samples, request
):
    expected_path = os.path.join(pdf_samples, "test_draw_image_on_radio_template.pdf")
    with open(expected_path, "rb+") as f:
        with open(os.path.join(image_samples, "sample_image.jpg"), "rb+") as _f:
            obj = PdfWrapper(template_with_radiobutton_stream).draw(
                [
                    RawElements.RawImage(
                        _f,
                        2,
                        100,
                        100,
                        400,
                        225,
                    )
                ]
            )

        expected = f.read()

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


def test_draw_image_on_sejda_template(
    sejda_template, image_samples, pdf_samples, request
):
    expected_path = os.path.join(pdf_samples, "test_draw_image_on_sejda_template.pdf")
    with open(expected_path, "rb+") as f:
        with open(os.path.join(image_samples, "sample_image.jpg"), "rb+") as _f:
            obj = PdfWrapper(sejda_template).draw(
                [
                    RawElements.RawImage(
                        _f,
                        2,
                        100,
                        100,
                        400,
                        225,
                    )
                ]
            )

        expected = f.read()

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


@pytest.mark.posix_only
def test_draw_png_image_on_one_page(
    template_stream, image_samples, pdf_samples, request
):
    expected_path = os.path.join(pdf_samples, "test_draw_png_image_on_one_page.pdf")
    with open(expected_path, "rb+") as f:
        obj = PdfWrapper(template_stream).draw(
            [
                RawElements.RawImage(
                    os.path.join(image_samples, "sample_png_image.png"),
                    2,
                    100,
                    100,
                    400,
                    225,
                )
            ]
        )

        expected = f.read()

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()
        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


@pytest.mark.posix_only
def test_draw_transparent_png_image_on_one_page(
    template_stream, image_samples, pdf_samples, request
):
    expected_path = os.path.join(
        pdf_samples, "test_draw_transparent_png_image_on_one_page.pdf"
    )
    with open(expected_path, "rb+") as f:
        obj = PdfWrapper(template_stream).draw(
            [
                RawElements.RawImage(
                    os.path.join(image_samples, "sample_transparent_png.png"),
                    1,
                    100,
                    100,
                    400,
                    225,
                )
            ]
        )

        expected = f.read()

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()
        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


def test_draw_text_and_image(template_stream, image_samples, pdf_samples, request):
    expected_path = os.path.join(pdf_samples, "test_draw_text_and_image.pdf")
    with open(expected_path, "rb+") as f:
        with open(os.path.join(image_samples, "sample_image.jpg"), "rb+") as _f:
            obj = PdfWrapper(template_stream).draw(
                [
                    RawElements.RawText(
                        "drawn_text", 1, 300, 225, font_size=20, font_color=(1, 0, 0)
                    ),
                    RawElements.RawImage(_f, 2, 100, 100, 400, 225, rotation=180),
                ]
            )

        expected = f.read()

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()
        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


def test_draw_line(template_stream, pdf_samples, request):
    expected_path = os.path.join(pdf_samples, "test_draw_line.pdf")
    with open(expected_path, "rb+") as f:
        obj = PdfWrapper(template_stream).draw(
            [RawElements.RawLine(1, 100, 100, 200, 200, (1, 0, 0))]
        )

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


def test_draw_rect(template_stream, pdf_samples, request):
    expected_path = os.path.join(pdf_samples, "test_draw_rect.pdf")
    with open(expected_path, "rb+") as f:
        obj = PdfWrapper(template_stream).draw(
            [
                RawElements.RawRectangle(
                    page_number=1,
                    x=100,
                    y=100,
                    width=200,
                    height=100,
                    color=(0, 1, 0),
                    fill_color=(1, 0, 0),
                )
            ]
        )

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected
