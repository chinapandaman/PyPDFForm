# -*- coding: utf-8 -*-

import os

import pytest
from PyPDFForm import PyPDFForm


@pytest.fixture
def pdf_samples():
    return os.path.join(os.path.dirname(__file__), "..", "..", "pdf_samples")


@pytest.fixture
def template_stream(pdf_samples):
    with open(os.path.join(pdf_samples, "sample_template.pdf"), "rb+") as f:
        return f.read()


@pytest.fixture
def comparing_size():
    return 32767


def test_fill_simple_mode(template_stream, pdf_samples, comparing_size):
    with open(os.path.join(pdf_samples, "sample_filled_simple_mode.pdf"), "rb+") as f:
        obj = PyPDFForm(template_stream).fill(
            {
                "test": "test_1",
                "check": True,
                "test_2": "test_2",
                "check_2": False,
                "test_3": "test_3",
                "check_3": True,
            },
        )

        expected = f.read()

        assert len(obj.stream) == len(expected)
        assert obj.stream[:comparing_size] == expected[:comparing_size]


def test_fill_font_20(template_stream, pdf_samples, comparing_size):
    with open(os.path.join(pdf_samples, "sample_filled_font_20.pdf"), "rb+") as f:
        data_dict = {
            "test": "test_1",
            "check": True,
            "test_2": "test_2",
            "check_2": False,
            "test_3": "test_3",
            "check_3": True,
        }

        obj = PyPDFForm(template_stream, simple_mode=False).fill(
            data_dict, font_size=20,
        )

        expected = f.read()

        assert len(obj.stream) == len(expected)
        assert obj.stream[:comparing_size] == expected[:comparing_size]

        for k, v in obj.annotations.items():
            assert k in data_dict
            assert v.name in data_dict
            assert v.value == data_dict[k]

            if v.type == "text":
                assert v.font_size == 20
                assert v.text_x_offset == 0
                assert v.text_y_offset == 0
                assert v.text_wrap_length == 100


def test_fill_text_wrap_2(template_stream, pdf_samples, comparing_size):
    with open(os.path.join(pdf_samples, "sample_filled_text_wrap_2.pdf"), "rb+") as f:
        data_dict = {
            "test": "test_1",
            "check": True,
            "test_2": "test_2",
            "check_2": False,
            "test_3": "test_3",
            "check_3": True,
        }

        obj = PyPDFForm(template_stream, simple_mode=False).fill(
            data_dict, text_wrap_length=2,
        )

        expected = f.read()

        assert len(obj.stream) == len(expected)
        assert obj.stream[:comparing_size] == expected[:comparing_size]

        for k, v in obj.annotations.items():
            assert k in data_dict
            assert v.name in data_dict
            assert v.value == data_dict[k]

            if v.type == "text":
                assert v.font_size == 12
                assert v.text_x_offset == 0
                assert v.text_y_offset == 0
                assert v.text_wrap_length == 2


def test_fill_offset_100(template_stream, pdf_samples, comparing_size):
    with open(os.path.join(pdf_samples, "sample_filled_offset_100.pdf"), "rb+") as f:
        data_dict = {
            "test": "test_1",
            "check": True,
            "test_2": "test_2",
            "check_2": False,
            "test_3": "test_3",
            "check_3": True,
        }

        obj = PyPDFForm(template_stream, simple_mode=False).fill(
            data_dict, text_x_offset=100, text_y_offset=-100,
        )

        expected = f.read()

        assert len(obj.stream) == len(expected)
        assert obj.stream[:comparing_size] == expected[:comparing_size]

        for k, v in obj.annotations.items():
            assert k in data_dict
            assert v.name in data_dict
            assert v.value == data_dict[k]

            if v.type == "text":
                assert v.font_size == 12
                assert v.text_x_offset == 100
                assert v.text_y_offset == -100
                assert v.text_wrap_length == 100


def test_fill_editable(template_stream, pdf_samples, comparing_size):
    with open(os.path.join(pdf_samples, "sample_filled_editable.pdf"), "rb+") as f:
        obj = PyPDFForm(template_stream, simple_mode=True).fill(
            {
                "test": "test_1",
                "check": True,
                "test_2": "test_2",
                "check_2": False,
                "test_3": "test_3",
                "check_3": True,
            },
            editable=True,
        )

        expected = f.read()

        assert len(obj.stream) == len(expected)
        assert obj.stream[:comparing_size] == expected[:comparing_size]


def test_fill_with_customized_annotations(template_stream, pdf_samples, comparing_size):
    with open(
        os.path.join(pdf_samples, "sample_filled_customized_annotations.pdf"), "rb+"
    ) as f:
        data_dict = {
            "test": "test_1",
            "check": True,
            "test_2": "test_2",
            "check_2": False,
            "test_3": "test_3",
            "check_3": True,
        }

        obj = PyPDFForm(template_stream, simple_mode=False)

        obj.annotations["test"].font_size = 20
        obj.annotations["test_2"].text_x_offset = 50
        obj.annotations["test_2"].text_y_offset = -50
        obj.annotations["test_2"].text_wrap_length = 1
        obj.annotations["test_3"].text_wrap_length = 2

        obj.fill(data_dict)

        expected = f.read()

        assert len(obj.stream) == len(expected)
        assert obj.stream[:comparing_size] == expected[:comparing_size]

        for k, v in obj.annotations.items():
            assert k in data_dict
            assert v.name in data_dict
            assert v.value == data_dict[k]

        assert obj.annotations["test"].font_size == 20
        assert obj.annotations["test"].text_x_offset == 0
        assert obj.annotations["test"].text_y_offset == 0
        assert obj.annotations["test"].text_wrap_length == 100

        assert obj.annotations["test_2"].font_size == 12
        assert obj.annotations["test_2"].text_x_offset == 50
        assert obj.annotations["test_2"].text_y_offset == -50
        assert obj.annotations["test_2"].text_wrap_length == 1

        assert obj.annotations["test_3"].font_size == 12
        assert obj.annotations["test_3"].text_x_offset == 0
        assert obj.annotations["test_3"].text_y_offset == 0
        assert obj.annotations["test_3"].text_wrap_length == 2
