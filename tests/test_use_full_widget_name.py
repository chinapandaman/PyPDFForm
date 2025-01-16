# -*- coding: utf-8 -*-

from PyPDFForm import PdfWrapper


def test_init(sample_template_with_full_key):
    obj = PdfWrapper(sample_template_with_full_key, use_full_widget_name=True)
    assert "Gain de 2 classes.0" in obj.widgets
    assert obj.widgets["Gain de 2 classes.0"] is obj.widgets["0"]
