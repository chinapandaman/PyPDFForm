# -*- coding: utf-8 -*-

from PyPDFForm.exceptions import MergeError
from PyPDFForm.pdf import _PyPDFForm


class PyPDFForm(object):
    def __init__(self, template: bytes = b"", simple_mode: bool = True) -> None:
        self.stream = template
        self.simple_mode = simple_mode

    def __add__(self, other: "PyPDFForm") -> "PyPDFForm":
        if any(
            [
                (self is not None) and (type(self) != PyPDFForm),
                (other is not None) and (type(other) != PyPDFForm),
            ]
        ):
            raise MergeError

        self_obj = _PyPDFForm()
        if self:
            self_obj.stream = self.stream

        other_obj = _PyPDFForm()

        if other:
            other_obj.stream = other.stream

        new_obj = self.__class__()

        new_obj.stream = (self_obj + other_obj).stream

        return new_obj

    def fill(
        self,
        data: dict,
        font_size: float = 12,
        text_wrap_length: int = 100,
    ) -> "PyPDFForm":
        self.stream = (
            _PyPDFForm()
            .fill(self.stream, data, self.simple_mode, font_size, text_wrap_length)
            .stream
        )

        return self

    def draw_image(
        self,
        image: bytes,
        page_number: int,
        x: float,
        y: float,
        width: float,
        height: float,
        rotation: float = 0,
    ) -> "PyPDFForm":
        obj = _PyPDFForm()
        obj.stream = self.stream

        self.stream = obj.draw_image(
            image, page_number, x, y, width, height, rotation
        ).stream

        return self
