# -*- coding: utf-8 -*-

import os


def test_fixture_setup(pdf_directory, sample_job_application):
    assert os.path.isdir(pdf_directory)
    assert os.path.isfile(sample_job_application)

    file_extension = os.path.splitext(sample_job_application)[1]
    assert file_extension == ".pdf"
