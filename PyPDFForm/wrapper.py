# -*- coding: utf-8 -*-

from typing import Union

from .pdf import _PyPDFForm


class PyPDFForm(object):
    """A class to represent a PDF form."""

    def __init__(self, template: bytes = b"", simple_mode: bool = True) -> None:
        """Constructs all attributes for the PyPDFForm object."""

        self.stream = template
        self.simple_mode = simple_mode
        self.fill = self._simple_fill if simple_mode else self._fill

        if not simple_mode:
            self.annotations = _PyPDFForm().build_annotations(template).annotations

    def __add__(self, other: "PyPDFForm") -> "PyPDFForm":
        """Overloaded addition operator to perform merging PDFs."""

        self_obj = _PyPDFForm()
        self_obj.stream = self.stream

        other_obj = _PyPDFForm()
        other_obj.stream = other.stream

        new_obj = self.__class__()

        new_obj.stream = (self_obj + other_obj).stream

        return new_obj

    def _simple_fill(self, data: dict, editable: bool = False) -> "PyPDFForm":
        """Fill a PDF form in simple mode."""

        self.stream = (
            _PyPDFForm()
            .fill(self.stream, data, self.simple_mode, 12, 0, 0, 100, editable)
            .stream
        )

        return self

    def _fill(
        self,
        data: dict,
        font_size: Union[float, int] = 12,
        text_x_offset: Union[float, int] = 0,
        text_y_offset: Union[float, int] = 0,
        text_wrap_length: int = 100,
    ) -> "PyPDFForm":
        """Fill a PDF form with customized parameters."""

        obj = _PyPDFForm()
        obj.annotations = self.annotations
        obj = obj.fill(
            self.stream,
            data,
            self.simple_mode,
            font_size,
            text_x_offset,
            text_y_offset,
            text_wrap_length,
            False,
        )

        self.stream = obj.stream
        self.annotations = obj.annotations

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
        """Draw an image on a PDF form."""

        obj = _PyPDFForm()
        obj.stream = self.stream

        self.stream = obj.draw_image(
            image, page_number, x, y, width, height, rotation
        ).stream

        return self
