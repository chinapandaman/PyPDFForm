# -*- coding: utf-8 -*-

import os

import pytest

from PyPDFForm.core.font import Font as FontCore


@pytest.fixture
def font_samples():
    return os.path.join(os.path.dirname(__file__), "..", "..", "font_samples")


def test_register_bad_font():
    assert not FontCore().register_font("foo", b"bar")


def test_not_registered():
    assert not FontCore().is_registered("LiberationSerif")


def test_register_font_and_is_registered(font_samples):
    with open(os.path.join(font_samples, "LiberationSerif-Regular.ttf"), "rb+") as f:
        FontCore().register_font("LiberationSerif", f.read())

        assert FontCore().is_registered("LiberationSerif")
