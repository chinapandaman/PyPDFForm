# -*- coding: utf-8 -*-

import os

from PyPDFForm import PdfWrapper
from PyPDFForm.middleware.base import Widget
from PyPDFForm.middleware.text import Text


def test_base_schema_definition():
    assert Widget("foo").schema_definition == {}


def test_fill(template_stream, pdf_samples, data_dict, request):
    expected_path = os.path.join(pdf_samples, "test_fill.pdf")
    with open(expected_path, "rb+") as f:
        obj = PdfWrapper(template_stream).fill(
            data_dict,
        )

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()
        assert len(obj.read()) == len(obj.read())
        assert obj.read() == obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


def test_fill_flatten(template_stream, pdf_samples, data_dict, request):
    expected_path = os.path.join(pdf_samples, "test_fill_flatten.pdf")
    with open(expected_path, "rb+") as f:
        obj = PdfWrapper(template_stream).fill(data_dict, flatten=True)

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()
        assert len(obj.read()) == len(obj.read())
        assert obj.read() == obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


def test_register_bad_fonts():
    assert not PdfWrapper().register_font("foo", b"foo").read()
    assert not PdfWrapper().register_font("foo", "foo").read()


def test_register_global_font_fill(
    template_stream, pdf_samples, samle_font_stream, data_dict, request
):
    expected_path = os.path.join(pdf_samples, "test_register_global_font_fill.pdf")
    with open(
        expected_path,
        "rb+",
    ) as f:
        obj = PdfWrapper(template_stream).register_font(
            "new_font",
            samle_font_stream,
        )
        for v in obj.widgets.values():
            if isinstance(v, Text):
                v.font = "new_font"
        obj.fill(
            data_dict,
        )

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


def test_register_global_font_fill_flatten(
    template_stream, pdf_samples, samle_font_stream, data_dict, request
):
    expected_path = os.path.join(
        pdf_samples, "test_register_global_font_fill_flatten.pdf"
    )
    with open(
        expected_path,
        "rb+",
    ) as f:
        obj = PdfWrapper(template_stream).register_font(
            "new_font",
            samle_font_stream,
        )
        for v in obj.widgets.values():
            if isinstance(v, Text):
                v.font = "new_font"
        obj.fill(
            data_dict,
            flatten=True,
        )

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


def test_fill_font_20(
    template_stream, pdf_samples, data_dict, request
):
    expected_path = os.path.join(pdf_samples, "test_fill_font_20.pdf")
    with open(
        expected_path,
        "rb+",
    ) as f:
        obj = PdfWrapper(template_stream)
        for v in obj.widgets.values():
            if isinstance(v, Text):
                v.font_size = 20
        obj.fill(
            data_dict,
        )

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


def test_fill_font_20_flatten(
    template_stream, pdf_samples, data_dict, request
):
    expected_path = os.path.join(pdf_samples, "test_fill_font_20_flatten.pdf")
    with open(
        expected_path,
        "rb+",
    ) as f:
        obj = PdfWrapper(template_stream)
        for v in obj.widgets.values():
            if isinstance(v, Text):
                v.font_size = 20
        obj.fill(
            data_dict, flatten=True,
        )

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


def test_fill_font_color_red(
    template_stream, pdf_samples, data_dict, request
):
    expected_path = os.path.join(pdf_samples, "test_fill_font_color_red.pdf")
    with open(
        expected_path,
        "rb+",
    ) as f:
        obj = PdfWrapper(template_stream)
        for v in obj.widgets.values():
            if isinstance(v, Text):
                v.font_color = (1, 0, 0)
        obj.fill(
            data_dict,
        )

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


def test_fill_font_color_red_flatten(
    template_stream, pdf_samples, data_dict, request
):
    expected_path = os.path.join(pdf_samples, "test_fill_font_color_red_flatten.pdf")
    with open(
        expected_path,
        "rb+",
    ) as f:
        obj = PdfWrapper(template_stream)
        for v in obj.widgets.values():
            if isinstance(v, Text):
                v.font_color = (1, 0, 0)
        obj.fill(
            data_dict, flatten=True
        )

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


def test_fill_with_customized_widgets(
    template_stream, pdf_samples, samle_font_stream, data_dict, request
):
    expected_path = os.path.join(pdf_samples, "test_fill_with_customized_widgets.pdf")
    with open(
        expected_path,
        "rb+",
    ) as f:
        obj = PdfWrapper(template_stream).register_font(
            "new_font",
            samle_font_stream,
        )
        obj.widgets["test"].font = "new_font"
        obj.widgets["test"].font_size = 20
        obj.widgets["test"].font_color = (1, 0, 0)
        obj.widgets["test_2"].font_color = (0, 1, 0)
        obj.fill(
            data_dict,
        )

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


def test_fill_with_customized_widgets_flatten(
    template_stream, pdf_samples, samle_font_stream, data_dict, request
):
    expected_path = os.path.join(pdf_samples, "test_fill_with_customized_widgets_flatten.pdf")
    with open(
        expected_path,
        "rb+",
    ) as f:
        obj = PdfWrapper(template_stream).register_font(
            "new_font",
            samle_font_stream,
        )
        obj.widgets["test"].font = "new_font"
        obj.widgets["test"].font_size = 20
        obj.widgets["test"].font_color = (1, 0, 0)
        obj.widgets["test_2"].font_color = (0, 1, 0)
        obj.fill(
            data_dict, flatten=True,
        )

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


def test_fill_radiobutton(
    template_with_radiobutton_stream, pdf_samples, request
):
    expected_path = os.path.join(pdf_samples, "test_fill_radiobutton.pdf")
    with open(
        expected_path,
        "rb+",
    ) as f:
        obj = PdfWrapper(template_with_radiobutton_stream).fill(
            {
                "radio_1": 0,
                "radio_2": 1,
                "radio_3": 2,
            },
        )

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


def test_fill_radiobutton_flatten(
    template_with_radiobutton_stream, pdf_samples, request
):
    expected_path = os.path.join(pdf_samples, "test_fill_radiobutton_flatten.pdf")
    with open(
        expected_path,
        "rb+",
    ) as f:
        obj = PdfWrapper(template_with_radiobutton_stream).fill(
            {
                "radio_1": 0,
                "radio_2": 1,
                "radio_3": 2,
            },
            flatten=True,
        )

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


def test_fill_sejda(
    sejda_template, pdf_samples, sejda_data, request
):
    expected_path = os.path.join(pdf_samples, "test_fill_sejda.pdf")
    with open(
        expected_path,
        "rb+",
    ) as f:
        obj = PdfWrapper(sejda_template).fill(
            sejda_data
        )

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


def test_fill_sejda_flatten(
    sejda_template, pdf_samples, sejda_data, request
):
    expected_path = os.path.join(pdf_samples, "test_fill_sejda_flatten.pdf")
    with open(
        expected_path,
        "rb+",
    ) as f:
        obj = PdfWrapper(sejda_template).fill(
            sejda_data, flatten=True,
        )

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


def test_draw_text_on_one_page(template_stream, pdf_samples, request):
    expected_path = os.path.join(pdf_samples, "test_draw_text_on_one_page.pdf")
    with open(expected_path, "rb+") as f:
        obj = PdfWrapper(template_stream).draw_text(
            "drawn_text",
            1,
            300,
            225,
            font_size=20,
            font_color=(1, 0, 0),
        )

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


def test_draw_text_on_radio_template(
    template_with_radiobutton_stream, pdf_samples, request
):
    expected_path = os.path.join(pdf_samples, "test_draw_text_on_radio_template.pdf")
    with open(expected_path, "rb+") as f:
        obj = PdfWrapper(template_with_radiobutton_stream).draw_text(
            "drawn_text",
            1,
            300,
            225,
            font_size=20,
            font_color=(1, 0, 0),
        )

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected


def test_draw_text_on_sejda_template(sejda_template, pdf_samples, request):
    expected_path = os.path.join(pdf_samples, "test_draw_text_on_sejda_template.pdf")
    with open(expected_path, "rb+") as f:
        obj = PdfWrapper(sejda_template).draw_text(
            "drawn_text",
            1,
            300,
            225,
            font_size=20,
            font_color=(1, 0, 0),
        )

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected
