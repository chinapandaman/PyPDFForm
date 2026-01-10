# -*- coding: utf-8 -*-

import os
from io import BytesIO

from PyPDFForm import PdfWrapper


def test_create_pdf_wrapper(static_pdfs):
    pdf = PdfWrapper(os.path.join(static_pdfs, "sample_template.pdf"))

    assert pdf.read()

    with open(os.path.join(static_pdfs, "sample_template.pdf"), "rb+") as template:
        pdf_2 = PdfWrapper(template)

    with open(os.path.join(static_pdfs, "sample_template.pdf"), "rb+") as template:
        pdf_3 = PdfWrapper(template.read())

    assert pdf.read() == pdf_2.read()
    assert pdf.read() == pdf_3.read()


def test_change_title(static_pdfs):
    pdf = PdfWrapper(os.path.join(static_pdfs, "sample_template.pdf"), title="My PDF")

    assert pdf.title == "My PDF"

    pdf.title = "My PDF"

    assert pdf.title == "My PDF"


def test_create_need_appearances_wrapper(static_pdfs):
    pdf = PdfWrapper(
        os.path.join(static_pdfs, "sample_template.pdf"), need_appearances=True
    )

    assert getattr(pdf, "need_appearances")
    assert (
        pdf.read()
        != PdfWrapper(os.path.join(static_pdfs, "sample_template.pdf")).read()
    )


def test_create_generate_appearance_streams_wrapper(static_pdfs):
    pdf = PdfWrapper(
        os.path.join(static_pdfs, "sample_template.pdf"),
        generate_appearance_streams=True,
    )

    assert getattr(pdf, "generate_appearance_streams")
    assert getattr(pdf, "need_appearances")
    assert (
        pdf.read()
        != PdfWrapper(os.path.join(static_pdfs, "sample_template.pdf")).read()
    )


def test_use_full_widget_name(static_pdfs):
    pdf = PdfWrapper(
        os.path.join(static_pdfs, "sample_template_with_full_key.pdf"),
        use_full_widget_name=True,
    )

    assert getattr(pdf, "use_full_widget_name")
    assert "Gain de 2 classes.0" in pdf.widgets
    assert "0" not in pdf.widgets


def test_write_io(static_pdfs):
    buff = BytesIO()

    pdf = PdfWrapper(os.path.join(static_pdfs, "sample_template.pdf"))
    pdf.write(buff)

    buff.seek(0)

    assert buff.read() == pdf.read()
