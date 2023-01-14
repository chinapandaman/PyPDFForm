# -*- coding: utf-8 -*-

import os

import pytest

from PyPDFForm.core import font


@pytest.fixture
def font_samples():
    return os.path.join(os.path.dirname(__file__), "..", "..", "font_samples")


def test_register_bad_font():
    assert not font.register_font("foo", b"bar")


def test_not_registered():
    assert not font.is_registered("LiberationSerif")


def test_register_font_and_is_registered(font_samples):
    with open(os.path.join(font_samples, "LiberationSerif-Regular.ttf"), "rb+") as f:
        font.register_font("LiberationSerif", f.read())

        assert font.is_registered("LiberationSerif")
