# -*- coding: utf-8 -*-

import os

import pytest


def pytest_configure(config):
    config.results = {}


def pytest_addoption(parser):
    parser.addoption("--regenerate", action="store", default="0")


@pytest.fixture(autouse=True)
def generate_new_pdf_samples(request):
    request.config.results = {}
    yield
    if request.config.getoption("--regenerate") == "1":
        if request.config.results:
            with open(request.config.results["expected_path"], "wb+") as f:
                f.write(request.config.results["stream"])


@pytest.fixture
def pdf_samples():
    return os.path.join(os.path.dirname(__file__), "..", "pdf_samples")


@pytest.fixture
def template_stream(pdf_samples):
    with open(os.path.join(pdf_samples, "sample_template.pdf"), "rb+") as f:
        return f.read()


@pytest.fixture
def template_with_radiobutton_stream(pdf_samples):
    with open(
        os.path.join(pdf_samples, "sample_template_with_radio_button.pdf"), "rb+"
    ) as f:
        return f.read()


@pytest.fixture
def image_samples():
    return os.path.join(os.path.dirname(__file__), "..", "image_samples")


@pytest.fixture
def font_samples():
    return os.path.join(os.path.dirname(__file__), "..", "font_samples")


@pytest.fixture
def data_dict():
    return {
        "test": "test_1",
        "check": True,
        "test_2": "test_2",
        "check_2": False,
        "test_3": "test_3",
        "check_3": True,
    }


@pytest.fixture
def sejda_template(pdf_samples):
    with open(os.path.join(pdf_samples, "sample_template_sejda.pdf"), "rb+") as f:
        return f.read()


@pytest.fixture
def sejda_template_complex(pdf_samples):
    with open(
        os.path.join(pdf_samples, "sample_template_sejda_complex.pdf"), "rb+"
    ) as f:
        return f.read()


@pytest.fixture
def sample_template_with_max_length_text_field(pdf_samples):
    with open(
        os.path.join(pdf_samples, "sample_template_with_max_length_text_field.pdf"),
        "rb+",
    ) as f:
        return f.read()


@pytest.fixture
def sample_template_with_comb_text_field(pdf_samples):
    with open(
        os.path.join(pdf_samples, "sample_template_with_comb_text_field.pdf"), "rb+"
    ) as f:
        return f.read()


@pytest.fixture
def sample_template_with_comb_text_field_right_aligned(pdf_samples):
    with open(
        os.path.join(
            pdf_samples, "sample_template_with_comb_text_field_right_aligned.pdf"
        ),
        "rb+",
    ) as f:
        return f.read()


@pytest.fixture
def sample_template_with_right_aligned_text_field(pdf_samples):
    with open(
        os.path.join(pdf_samples, "sample_template_with_right_aligned_text_field.pdf"),
        "rb+",
    ) as f:
        return f.read()


@pytest.fixture
def sample_template_with_paragraph(pdf_samples):
    with open(
        os.path.join(pdf_samples, "sample_template_with_paragraph.pdf"),
        "rb+",
    ) as f:
        return f.read()


@pytest.fixture
def sample_template_with_paragraph_auto_font(pdf_samples):
    with open(
        os.path.join(pdf_samples, "sample_template_with_paragraph_auto_font.pdf"),
        "rb+",
    ) as f:
        return f.read()


@pytest.fixture
def sample_template_with_dropdown(pdf_samples):
    with open(
        os.path.join(pdf_samples, "dropdown", "sample_template_with_dropdown.pdf"),
        "rb+",
    ) as f:
        return f.read()


@pytest.fixture
def dropdown_alignment(pdf_samples):
    with open(
        os.path.join(pdf_samples, "dropdown", "dropdown_alignment.pdf"),
        "rb+",
    ) as f:
        return f.read()


@pytest.fixture
def dropdown_alignment_sejda(pdf_samples):
    with open(
        os.path.join(pdf_samples, "dropdown", "dropdown_alignment_sejda.pdf"),
        "rb+",
    ) as f:
        return f.read()


@pytest.fixture
def sejda_data():
    return {
        "date": "01-01",
        "year": "21",
        "buyer_name": "John Doe",
        "buyer_address": "1 N Main St, Chicago, IL 60000",
        "seller_name": "Jack Smith",
        "seller_address": "2 S Main St, Chicago, IL 60000",
        "make": "AK",
        "model": "47",
        "caliber": "7.62-x39mm",
        "serial_number": "111111",
        "purchase_option": 0,
        "date_of_this_bill": True,
        "at_future_date": True,
        "other": True,
        "other_reason": "NO REASONS",
        "payment_amount": "400",
        "future_date": "01-01",
        "future_year": "22",
        "exchange_for": "Food",
        "buyer_name_printed": "John Doe",
        "seller_name_printed": "Jack Smith",
        "buyer_signed_date": "2021-01-01",
        "seller_signed_date": "2021-01-01",
        "buyer_dl_number": "D000-4609-0001",
        "seller_dl_number": "S530-4209-0001",
        "buyer_dl_state": "IL",
        "seller_dl_state": "IL",
    }


@pytest.fixture
def max_length_expected_directory():
    return os.path.join(
        os.path.dirname(__file__),
        "..",
        "pdf_samples",
        "max_length_text_field_related",
    )
