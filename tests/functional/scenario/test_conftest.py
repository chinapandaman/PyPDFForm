# -*- coding: utf-8 -*-

import inspect
import os


def test_sample_job_application_fixture_setup(pdf_directory, sample_job_application):
    assert os.path.isdir(pdf_directory)
    assert os.path.isfile(sample_job_application)

    file_extension = os.path.splitext(sample_job_application)[1]
    assert file_extension == ".pdf"


def test_sample_signature_fixture_setup(image_directory, sample_signature):
    assert os.path.isdir(image_directory)
    assert os.path.isfile(sample_signature)
    file_extension = os.path.splitext(sample_signature)[1]
    assert file_extension == ".jpg"


def test_sample_font_fixtures_setup(
    font_directory, tinos_regular, tinos_bold, tinos_italic, tinos_bold_italic
):
    assert os.path.isdir(font_directory)

    fonts = [
        value
        for key, value in locals().items()
        if isinstance(value, str) and key.startswith("tinos")
    ]
    for each in fonts:
        assert os.path.isfile(each)
        file_extension = os.path.splitext(each)[1]
        assert file_extension == ".ttf"
