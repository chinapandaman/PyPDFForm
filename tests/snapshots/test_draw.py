# -*- coding: utf-8 -*-

import os

from PyPDFForm import PdfWrapper, RawElements


def test_draw_multiline_text_on_one_page(template_stream, expect_pdf):
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

    expect_pdf(obj.read())


def test_draw_text_on_radio_template(template_with_radiobutton_stream, expect_pdf):
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

    expect_pdf(obj.read())


def test_draw_text_on_sejda_template(sejda_template, expect_pdf):
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

    expect_pdf(obj.read())


def test_draw_image_on_radio_template(
    template_with_radiobutton_stream, image_samples, expect_pdf
):
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

    expect_pdf(obj.read())


def test_draw_image_on_sejda_template(sejda_template, image_samples, expect_pdf):
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

    expect_pdf(obj.read())


def test_draw_png_image_on_one_page(template_stream, image_samples, expect_pdf):
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

    expect_pdf(obj.read())


def test_draw_transparent_png_image_on_one_page(
    template_stream, image_samples, expect_pdf
):
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

    expect_pdf(obj.read())


def test_draw_text_and_image(template_stream, image_samples, expect_pdf):
    with open(os.path.join(image_samples, "sample_image.jpg"), "rb+") as _f:
        obj = PdfWrapper(template_stream).draw(
            [
                RawElements.RawText(
                    "drawn_text", 1, 300, 225, font_size=20, font_color=(1, 0, 0)
                ),
                RawElements.RawImage(_f, 2, 100, 100, 400, 225, rotation=180),
            ]
        )

    expect_pdf(obj.read())
