# -*- coding: utf-8 -*-

import os

import pytest


@pytest.fixture
def pdf_directory():
    return os.path.join(os.path.dirname(__file__), "..", "..", "..", "pdf_samples", "scenario")


@pytest.fixture
def sample_job_application(pdf_directory):
    return os.path.join(pdf_directory, "sample_job_application.pdf")
