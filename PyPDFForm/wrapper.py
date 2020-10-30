# -*- coding: utf-8 -*-

from PyPDFForm.pdf import _PyPDFForm


class PyPDFForm(object):
    def __init__(self):
        self.stream = ""

    def __add__(self, other):
        self_obj = _PyPDFForm()
        self_obj.stream = self.stream

        other_obj = _PyPDFForm()
        other_obj.stream = other.stream

        new_obj = self.__class__()

        new_obj.stream = (self_obj + other_obj).stream

        return new_obj

    def fill(
        self,
        template_stream,
        data,
        simple_mode=True,
        font_size=12,
        text_wrap_length=100,
    ):
        self.stream = (
            _PyPDFForm()
            .fill(template_stream, data, simple_mode, font_size, text_wrap_length)
            .stream
        )

        return self

    def draw_image(self, page_number, image_stream, x, y, width, height, rotation=0):
        obj = _PyPDFForm()
        obj.stream = self.stream

        self.stream = obj.draw_image(
            page_number, image_stream, x, y, width, height, rotation
        ).stream

        return self
