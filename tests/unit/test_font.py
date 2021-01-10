# -*- coding: utf-8 -*-

import pytest
import os
from PyPDFForm.core.font import Font as FontCore


@pytest.fixture
def font_samples():
    return os.path.join(os.path.dirname(__file__), "..", "..", "font_samples")


def test_register_font_and_is_registered(font_samples):
    assert not FontCore().is_registered("LiberationSerif")

    with open(os.path.join(font_samples, "LiberationSerif-Regular.ttf"), "rb+") as f:
        FontCore().register_font("LiberationSerif", f.read())

        assert FontCore().is_registered("LiberationSerif")
