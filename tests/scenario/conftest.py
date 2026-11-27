# -*- coding: utf-8 -*-

import os

import pytest


@pytest.fixture
def pdf_directory():
    return os.path.join(
        os.path.dirname(__file__), "..", "..", "pdf_samples", "input", "scenario"
    )


@pytest.fixture
def issue_pdf_directory(pdf_directory):
    return os.path.join(pdf_directory, "issues")


@pytest.fixture
def tool_pdf_directory(pdf_directory):
    return os.path.join(pdf_directory, "tools")


@pytest.fixture
def existed_pdf_directory(pdf_directory):
    return os.path.join(pdf_directory, "existed")


@pytest.fixture
def multi_language_pdf_samples():
    return os.path.join(
        os.path.dirname(__file__), "..", "..", "pdf_samples", "input", "multi_language"
    )


@pytest.fixture
def zh_cn(multi_language_pdf_samples):
    return os.path.join(multi_language_pdf_samples, "zh_cn")


@pytest.fixture
def ko(multi_language_pdf_samples):
    return os.path.join(multi_language_pdf_samples, "ko")
