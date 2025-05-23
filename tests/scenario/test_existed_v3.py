# -*- coding: utf-8 -*-

import os

from PyPDFForm import PdfWrapper


def test_illinois_gun_bill_of_sale(existed_pdf_directory, request):
    obj = PdfWrapper(
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
        existed_pdf_directory, "test_illinois_gun_bill_of_sale.pdf"
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
    obj = PdfWrapper(os.path.join(existed_pdf_directory, "DS82.pdf")).fill(
        {
            "LastName": "Smith",
        }
    )

    expected_path = os.path.join(
        existed_pdf_directory,
        "test_ds82.pdf",
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
