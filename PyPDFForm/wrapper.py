# -*- coding: utf-8 -*-

from typing import Union

from PyPDFForm.pdf import _PyPDFForm


class PyPDFForm(object):
    def __init__(self, template: bytes = b"", simple_mode: bool = True) -> None:
        self.stream = template
        self.simple_mode = simple_mode

    def __add__(self, other: "PyPDFForm") -> "PyPDFForm":
        self_obj = _PyPDFForm()
        self_obj.stream = self.stream

        other_obj = _PyPDFForm()
        other_obj.stream = other.stream

        new_obj = self.__class__()

        new_obj.stream = (self_obj + other_obj).stream

        return new_obj

    def fill(
        self,
        data: dict,
        font_size: Union[float, int] = 12,
        text_x_offset: Union[float, int] = 0,
        text_y_offset: Union[float, int] = 0,
        text_wrap_length: int = 100,
    ) -> "PyPDFForm":
        self.stream = (
            _PyPDFForm()
            .fill(
                self.stream,
                data,
                self.simple_mode,
                font_size,
                text_x_offset,
                text_y_offset,
                text_wrap_length,
            )
            .stream
        )

        return self

    def draw_image(
        self,
        image: bytes,
        page_number: int,
        x: Union[float, int],
        y: Union[float, int],
        width: Union[float, int],
        height: Union[float, int],
        rotation: Union[float, int] = 0,
    ) -> "PyPDFForm":
        obj = _PyPDFForm()
        obj.stream = self.stream

        self.stream = obj.draw_image(
            image, page_number, x, y, width, height, rotation
        ).stream

        return self
