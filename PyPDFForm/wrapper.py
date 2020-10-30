# -*- coding: utf-8 -*-

from PyPDFForm.pdf import _PyPDFForm


class PyPDFForm(object):
    def __init__(self, template="", simple_mode=True):
        self.stream = template
        self.simple_mode = simple_mode

    def __add__(self, other):
        self_obj = _PyPDFForm()
        self_obj.stream = self.stream

        other_obj = _PyPDFForm()
        other_obj.stream = other.stream

        new_obj = self.__class__()

        new_obj.stream = (self_obj + other_obj).stream

        return new_obj

    def fill(
        self, data, font_size=12, text_wrap_length=100,
    ):
        self.stream = (
            _PyPDFForm()
            .fill(self.stream, data, self.simple_mode, font_size, text_wrap_length)
            .stream
        )

        return self

    def draw_image(self, image, page_number, x, y, width, height, rotation=0):
        obj = _PyPDFForm()
        obj.stream = self.stream

        self.stream = obj.draw_image(
            page_number, image, x, y, width, height, rotation
        ).stream

        return self
