# -*- coding: utf-8 -*-

import os

from PyPDFForm import PyPDFForm


def test_illinois_gun_bill_of_sale(existed_pdf_directory, request):
    obj = PyPDFForm(
        os.path.join(existed_pdf_directory, "illinois-gun-bill-of-sale.pdf")
    ).fill(
        {
            "Date": "01-01",
            "20": "22",
            "Buyers Name": "John Doe",
            "undefined": "1 N Main St, Chicago, IL 60000",
            "Sellers Name": "Jack Smith",
            "undefined_2": "2 S Main St, Chicago, IL 60000",
            "Make": "AK",
            "TypeModel": "47",
            "Caliber": "7.62-x39mm",
            "Serial Number SN": "111111",
            "Seller accepts cash payment in the amount of": True,
            "The date of this bill of sale": True,
            "At a future date no later than": True,
            "Other": True,
            "undefined_4": "NO REASONS",
            "to": "400",
            "undefined_3": "01-01",
            "20_2": "23",
            "undefined_5": "Food",
            "Buyer is receiving the Firearm as a Gift": True,
            "Seller accepts trade for the Firearm in exchange for": True,
            "Print Name": "John Doe",
            "Print Name_2": "Jack Smith",
            "Date_2": "2021-01-01",
            "Date_3": "2021-01-01",
            "Drivers License Number": "D000-4609-0001",
            "Drivers License Number_2": "S530-4209-0001",
            "State": "IL",
            "State_2": "IL",
        }
    )

    expected_path = os.path.join(
        existed_pdf_directory, "illinois-gun-bill-of-sale_expected.pdf"
    )
    request.config.results["expected_path"] = expected_path
    request.config.results["stream"] = obj.read()
    with open(
        expected_path,
        "rb+",
    ) as f:
        expected = f.read()
        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


def test_ds82(existed_pdf_directory, request):
    obj = PyPDFForm(os.path.join(existed_pdf_directory, "DS82.pdf")).fill(
        {
            "LastName": "Smith",
        }
    )

    expected_path = os.path.join(
        existed_pdf_directory,
        "DS82_expected.pdf",
    )
    request.config.results["expected_path"] = expected_path
    request.config.results["stream"] = obj.read()
    with open(
        expected_path,
        "rb+",
    ) as f:
        expected = f.read()
        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


def test_ds82_all_chars_lowercase(existed_pdf_directory, request):
    obj = PyPDFForm(os.path.join(existed_pdf_directory, "DS82.pdf")).fill(
        {
            "LastName": "x" * 30,
        }
    )

    expected_path = os.path.join(
        existed_pdf_directory,
        "DS82_expected_all_chars_lowercase.pdf",
    )
    request.config.results["expected_path"] = expected_path
    request.config.results["stream"] = obj.read()
    with open(
        expected_path,
        "rb+",
    ) as f:
        expected = f.read()
        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


def test_ds82_all_chars_uppercase(existed_pdf_directory, request):
    obj = PyPDFForm(os.path.join(existed_pdf_directory, "DS82.pdf")).fill(
        {
            "LastName": "X" * 30,
        }
    )

    expected_path = os.path.join(
        existed_pdf_directory,
        "DS82_expected_all_chars_uppercase.pdf",
    )
    request.config.results["expected_path"] = expected_path
    request.config.results["stream"] = obj.read()
    with open(
        expected_path,
        "rb+",
    ) as f:
        expected = f.read()
        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


def test_ds82_mixed_case(existed_pdf_directory, request):
    obj = PyPDFForm(os.path.join(existed_pdf_directory, "DS82.pdf")).fill(
        {
            "LastName": "xX" * 10,
        }
    )

    expected_path = os.path.join(
        existed_pdf_directory,
        "DS82_expected_mixed_case.pdf",
    )
    request.config.results["expected_path"] = expected_path
    request.config.results["stream"] = obj.read()
    with open(
        expected_path,
        "rb+",
    ) as f:
        expected = f.read()
        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


def test_illinois_real_estate_power_of_attorney_form(existed_pdf_directory, request):
    obj = PyPDFForm(
        os.path.join(
            existed_pdf_directory, "illinois-real-estate-power-of-attorney-form.pdf"
        )
    ).fill(
        {
            "undefined": "John Doe",
            "State of": "Chicago",
            "undefined_2": "Illinois",
            "of": "Michael Smith",
            "Illinois as my Attorneyin": "Chicago",
            "with full power and": "Random",
            "is as": "Not Random",
            "Address of Principal": "1 N Central, Chicago, IL 60000",
            "Phone number where Principal can be contacted": "(000)000-0000",
            "Email address of Principal": "msmith@example.com",
            "Text3": "Someone",
            "Dated": "2018-01-01",
            "Text4": "Sometwo",
            "Text5": "Somethree",
            "Text6": "Somefour",
            "Dated 1": "2019-01-01",
            "My commission expires": "NOW",
        }
    )

    expected_path = os.path.join(
        existed_pdf_directory,
        "illinois-real-estate-power-of-attorney-form_expected.pdf",
    )
    request.config.results["expected_path"] = expected_path
    request.config.results["stream"] = obj.read()
    with open(
        expected_path,
        "rb+",
    ) as f:
        expected = f.read()
        assert len(obj.read()) == len(expected)
        assert obj.read() == expected
