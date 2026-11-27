# -*- coding: utf-8 -*-


from PyPDFForm import PdfWrapper


def test_on_open_script(template_stream):
    pdf = PdfWrapper(template_stream, need_appearances=True)
    pdf.on_open_javascript = 'this.getField("test").value = "opened";'

    assert pdf.on_open_javascript == 'this.getField("test").value = "opened";'


def test_on_open_script_title_coexist(template_stream):
    pdf = PdfWrapper(template_stream, title="My PDF")
    pdf.on_open_javascript = 'this.getField("test").value = "opened";'

    assert pdf.title == "My PDF"
    assert pdf.on_open_javascript == 'this.getField("test").value = "opened";'
