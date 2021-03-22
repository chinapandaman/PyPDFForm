# -*- coding: utf-8 -*-

import os


def test_fixture_setup(pdf_directory, sample_job_application):
    assert os.path.isdir(pdf_directory)
    assert os.path.isfile(sample_job_application)
