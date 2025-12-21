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


@pytest.fixture
def it(multi_language_pdf_samples):
    return os.path.join(multi_language_pdf_samples, "it")


@pytest.fixture
def hi(multi_language_pdf_samples):
    return os.path.join(multi_language_pdf_samples, "hi")


@pytest.fixture
def tr(multi_language_pdf_samples):
    return os.path.join(multi_language_pdf_samples, "tr")


@pytest.fixture
def ar(multi_language_pdf_samples):
    return os.path.join(multi_language_pdf_samples, "ar")


@pytest.fixture
def de(multi_language_pdf_samples):
    return os.path.join(multi_language_pdf_samples, "de")


@pytest.fixture
def fr(multi_language_pdf_samples):
    return os.path.join(multi_language_pdf_samples, "fr")


@pytest.fixture
def jv(multi_language_pdf_samples):
    return os.path.join(multi_language_pdf_samples, "jv")


@pytest.fixture
def th(multi_language_pdf_samples):
    return os.path.join(multi_language_pdf_samples, "th")


@pytest.fixture
def he(multi_language_pdf_samples):
    return os.path.join(multi_language_pdf_samples, "he")


@pytest.fixture
def fa(multi_language_pdf_samples):
    return os.path.join(multi_language_pdf_samples, "fa")


@pytest.fixture
def pl(multi_language_pdf_samples):
    return os.path.join(multi_language_pdf_samples, "pl")


@pytest.fixture
def sr(multi_language_pdf_samples):
    return os.path.join(multi_language_pdf_samples, "sr")


@pytest.fixture
def ms(multi_language_pdf_samples):
    return os.path.join(multi_language_pdf_samples, "ms")


@pytest.fixture
def no(multi_language_pdf_samples):
    return os.path.join(multi_language_pdf_samples, "no")


@pytest.fixture
def da(multi_language_pdf_samples):
    return os.path.join(multi_language_pdf_samples, "da")


@pytest.fixture
def fi(multi_language_pdf_samples):
    return os.path.join(multi_language_pdf_samples, "fi")


@pytest.fixture
def el(multi_language_pdf_samples):
    return os.path.join(multi_language_pdf_samples, "el")
