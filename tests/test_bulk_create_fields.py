# -*- coding: utf-8 -*-

import os

import pytest

from PyPDFForm import Fields, PdfWrapper


@pytest.mark.posix_only
def test_bulk_create_fields_stress(template_stream, pdf_samples, request):
    expected_path = os.path.join(
        pdf_samples, "bulk_create_fields", "test_bulk_create_fields_stress.pdf"
    )

    fields = []
    x = 0
    y = 0
    margin = 25
    while x <= 575:
        while y <= 625:
            fields.append(
                Fields.TextField(f"text_{x}_{y}", 1, x, y, width=margin, height=margin)
            )
            fields.append(Fields.CheckBoxField(f"check_{x}_{y}", 2, x, y, size=margin))
            fields.append(
                Fields.DropdownField(
                    f"dropdown_{x}_{y}",
                    3,
                    x,
                    y,
                    width=margin,
                    height=margin,
                    options=["foo", "bar"],
                )
            )
            y += margin
        y = 0
        x += margin

    with open(expected_path, "rb+") as f:
        obj = PdfWrapper(template_stream).bulk_create_fields(fields)

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


@pytest.mark.posix_only
def test_bulk_create_fields_stress_2(template_stream, pdf_samples, request):
    expected_path = os.path.join(
        pdf_samples, "bulk_create_fields", "test_bulk_create_fields_stress_2.pdf"
    )

    fields = []
    x = 0
    y = 0
    margin = 25
    while x <= 575:
        while y <= 625:
            fields.append(
                Fields.TextField(f"text_{x}_{y}", 1, x, y, width=margin, height=margin)
            )
            fields.append(Fields.CheckBoxField(f"check_{x}_{y}", 2, x, y, size=margin))
            fields.append(
                Fields.DropdownField(
                    f"dropdown_{x}_{y}",
                    3,
                    x,
                    y,
                    width=margin,
                    height=margin,
                    options=["foo", "bar"],
                )
            )
            fields.append(
                Fields.RadioGroup(
                    f"radio_{x}_{y}", 4, [x, x + 12.5], [y, y + 12.5], size=12.5
                )
            )
            y += margin
        y = 0
        x += margin

    with open(expected_path, "rb+") as f:
        obj = PdfWrapper(template_stream) + PdfWrapper(
            os.path.join(pdf_samples, "dummy.pdf")
        )
        obj.bulk_create_fields(fields)

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


@pytest.mark.posix_only
def test_bulk_create_fields_stress_3(pdf_samples, request):
    expected_path = os.path.join(
        pdf_samples, "bulk_create_fields", "test_bulk_create_fields_stress_3.pdf"
    )

    fields = []
    x = 0
    y = 0
    margin = 25
    while x <= 575:
        while y <= 625:
            fields.append(
                Fields.TextField(f"text_{x}_{y}", 1, x, y, width=margin, height=margin)
            )
            fields.append(
                Fields.CheckBoxField(f"check_{x}_{y}", 1, x + margin, y, size=margin)
            )
            fields.append(
                Fields.DropdownField(
                    f"dropdown_{x}_{y}",
                    1,
                    x,
                    y + margin,
                    width=margin,
                    height=margin,
                    options=["foo", "bar"],
                )
            )
            fields.append(
                Fields.RadioGroup(
                    f"radio_{x}_{y}",
                    1,
                    [x + margin, x + margin + 12.5],
                    [y + margin, y + margin + 12.5],
                    size=12.5,
                )
            )
            y += 50
        y = 0
        x += 50

    with open(expected_path, "rb+") as f:
        obj = PdfWrapper(os.path.join(pdf_samples, "dummy.pdf")).bulk_create_fields(
            fields
        )

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected
