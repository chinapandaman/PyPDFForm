# -*- coding: utf-8 -*-
# ruff: noqa: SIM115

import os

from PyPDFForm import PdfWrapper, RawElements


def test_draw_text(static_pdfs, pdf_samples, request):
    expected_path = os.path.join(pdf_samples, "docs", "test_draw_text.pdf")

    texts = [
        RawElements.RawText(
            text="random text",
            page_number=1,
            x=300,
            y=225,
            font="Helvetica",  # optional
            font_size=12,  # optional
            font_color=(1, 0, 0),  # optional
        ),
        RawElements.RawText(
            text="random text on page 2",
            page_number=2,
            x=300,
            y=225,
            font="Helvetica",  # optional
            font_size=12,  # optional
            font_color=(1, 0, 0),  # optional
        ),
    ]

    pdf = PdfWrapper(os.path.join(static_pdfs, "sample_template.pdf")).draw(texts)

    request.config.results["expected_path"] = expected_path
    request.config.results["stream"] = pdf.read()

    with open(expected_path, "rb+") as f:
        expected = f.read()

        assert len(pdf.read()) == len(expected)
        assert pdf.read() == expected


def test_draw_image(static_pdfs, image_samples, pdf_samples, request):
    expected_path = os.path.join(pdf_samples, "docs", "test_draw_image.pdf")

    images = [
        RawElements.RawImage(
            image=os.path.join(image_samples, "sample_image.jpg"),
            page_number=1,
            x=100,
            y=100,
            width=400,
            height=225,
            rotation=0,  # optional
        ),
        RawElements.RawImage(
            image=os.path.join(image_samples, "sample_image.jpg"),
            page_number=2,
            x=100,
            y=100,
            width=400,
            height=225,
            rotation=180,  # optional
        ),
    ]

    pdf = PdfWrapper(os.path.join(static_pdfs, "sample_template.pdf")).draw(images)

    request.config.results["expected_path"] = expected_path
    request.config.results["stream"] = pdf.read()

    with open(expected_path, "rb+") as f:
        expected = f.read()

        assert len(pdf.read()) == len(expected)
        assert pdf.read() == expected

    images = [
        RawElements.RawImage(
            image=open(
                os.path.join(image_samples, "sample_image.jpg"), "rb+"
            ),  # in practice, use a context manager
            page_number=1,
            x=100,
            y=100,
            width=400,
            height=225,
            rotation=0,  # optional
        ),
        RawElements.RawImage(
            image=open(
                os.path.join(image_samples, "sample_image.jpg"), "rb+"
            ),  # in practice, use a context manager
            page_number=2,
            x=100,
            y=100,
            width=400,
            height=225,
            rotation=180,  # optional
        ),
    ]

    pdf2 = PdfWrapper(os.path.join(static_pdfs, "sample_template.pdf")).draw(images)

    assert pdf2.read() == pdf.read()

    images = [
        RawElements.RawImage(
            image=open(
                os.path.join(image_samples, "sample_image.jpg"), "rb+"
            ).read(),  # in practice, use a context manager
            page_number=1,
            x=100,
            y=100,
            width=400,
            height=225,
            rotation=0,  # optional
        ),
        RawElements.RawImage(
            image=open(
                os.path.join(image_samples, "sample_image.jpg"), "rb+"
            ).read(),  # in practice, use a context manager
            page_number=2,
            x=100,
            y=100,
            width=400,
            height=225,
            rotation=180,  # optional
        ),
    ]

    pdf3 = PdfWrapper(os.path.join(static_pdfs, "sample_template.pdf")).draw(images)

    assert pdf3.read() == pdf.read()


def test_draw_line(static_pdfs, pdf_samples, request):
    expected_path = os.path.join(pdf_samples, "docs", "test_draw_line.pdf")

    lines = [
        RawElements.RawLine(
            page_number=1,
            src_x=100,
            src_y=100,
            dest_x=100,
            dest_y=200,
        ),
        RawElements.RawLine(
            page_number=1,
            src_x=100,
            src_y=100,
            dest_x=200,
            dest_y=100,
            color=(0, 0, 1),  # optional
        ),
    ]

    pdf = PdfWrapper(os.path.join(static_pdfs, "sample_template.pdf")).draw(lines)

    request.config.results["expected_path"] = expected_path
    request.config.results["stream"] = pdf.read()

    with open(expected_path, "rb+") as f:
        expected = f.read()

        assert len(pdf.read()) == len(expected)
        assert pdf.read() == expected


def test_draw_rect(static_pdfs, pdf_samples, request):
    expected_path = os.path.join(pdf_samples, "docs", "test_draw_rect.pdf")

    rectangles = [
        RawElements.RawRectangle(
            page_number=1,
            x=100,
            y=100,
            width=200,
            height=100,
        ),
        RawElements.RawRectangle(
            page_number=1,
            x=400,
            y=100,
            width=100,
            height=200,
            color=(0, 0, 1),  # optional
            fill_color=(0, 1, 0),  # optional
        ),
    ]

    pdf = PdfWrapper(os.path.join(static_pdfs, "sample_template.pdf")).draw(rectangles)

    request.config.results["expected_path"] = expected_path
    request.config.results["stream"] = pdf.read()

    with open(expected_path, "rb+") as f:
        expected = f.read()

        assert len(pdf.read()) == len(expected)
        assert pdf.read() == expected


def test_draw_circle(static_pdfs, pdf_samples, request):
    expected_path = os.path.join(pdf_samples, "docs", "test_draw_circle.pdf")

    circles = [
        RawElements.RawCircle(
            page_number=1,
            center_x=100,
            center_y=100,
            radius=50,
        ),
        RawElements.RawCircle(
            page_number=1,
            center_x=250,
            center_y=100,
            radius=100,
            color=(1, 0, 0),  # optional
            fill_color=(0, 1, 0),  # optional
        ),
    ]

    pdf = PdfWrapper(os.path.join(static_pdfs, "sample_template.pdf")).draw(circles)

    request.config.results["expected_path"] = expected_path
    request.config.results["stream"] = pdf.read()

    with open(expected_path, "rb+") as f:
        expected = f.read()

        assert len(pdf.read()) == len(expected)
        assert pdf.read() == expected


def test_draw_ellipse(static_pdfs, pdf_samples, request):
    expected_path = os.path.join(pdf_samples, "docs", "test_draw_ellipse.pdf")

    ellipses = [
        RawElements.RawEllipse(
            page_number=1,
            x1=100,
            y1=100,
            x2=250,
            y2=200,
        ),
        RawElements.RawEllipse(
            page_number=1,
            x1=300,
            y1=100,
            x2=500,
            y2=250,
            color=(1, 0, 0),  # optional
            fill_color=(0, 1, 0),  # optional
        ),
    ]

    pdf = PdfWrapper(os.path.join(static_pdfs, "sample_template.pdf")).draw(ellipses)

    request.config.results["expected_path"] = expected_path
    request.config.results["stream"] = pdf.read()

    with open(expected_path, "rb+") as f:
        expected = f.read()

        assert len(pdf.read()) == len(expected)
        assert pdf.read() == expected
