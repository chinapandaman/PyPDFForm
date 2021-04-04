# -*- coding: utf-8 -*-

import os

import pytest


@pytest.fixture
def pdf_directory():
    return os.path.join(
        os.path.dirname(__file__), "..", "..", "..", "pdf_samples", "scenario"
    )


@pytest.fixture
def image_directory():
    return os.path.join(
        os.path.dirname(__file__), "..", "..", "..", "image_samples", "scenario"
    )


@pytest.fixture
def font_directory():
    return os.path.join(
        os.path.dirname(__file__), "..", "..", "..", "font_samples", "scenario"
    )


@pytest.fixture
def sample_job_application(pdf_directory):
    return os.path.join(pdf_directory, "sample_job_application.pdf")


@pytest.fixture
def sample_signature(image_directory):
    return os.path.join(image_directory, "sample_signature.jpg")


@pytest.fixture
def tinos_regular(font_directory):
    return os.path.join(font_directory, "Tinos-Regular.ttf")


@pytest.fixture
def tinos_bold(font_directory):
    return os.path.join(font_directory, "Tinos-Bold.ttf")


@pytest.fixture
def tinos_italic(font_directory):
    return os.path.join(font_directory, "Tinos-Italic.ttf")


@pytest.fixture
def tinos_bold_italic(font_directory):
    return os.path.join(font_directory, "Tinos-BoldItalic.ttf")
