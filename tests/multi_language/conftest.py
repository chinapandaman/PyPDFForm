# -*- coding: utf-8 -*-

import os

import pytest


@pytest.fixture
def multi_language_pdf_samples():
    return os.path.join(
        os.path.dirname(__file__), "..", "..", "pdf_samples", "multi_language"
    )


@pytest.fixture
def zh_cn(multi_language_pdf_samples):
    return os.path.join(multi_language_pdf_samples, "zh_cn")


@pytest.fixture
def ko(multi_language_pdf_samples):
    return os.path.join(multi_language_pdf_samples, "ko")


@pytest.fixture
def ja(multi_language_pdf_samples):
    return os.path.join(multi_language_pdf_samples, "ja")


@pytest.fixture
def ru(multi_language_pdf_samples):
    return os.path.join(multi_language_pdf_samples, "ru")


@pytest.fixture
def vi(multi_language_pdf_samples):
    return os.path.join(multi_language_pdf_samples, "vi")


@pytest.fixture
def es(multi_language_pdf_samples):
    return os.path.join(multi_language_pdf_samples, "es")
