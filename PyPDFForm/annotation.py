# -*- coding: utf-8 -*-

from typing import Union

from PyPDFForm import (InvalidFontSizeError, InvalidTextOffsetError,
                       InvalidWrapLengthError)


class Annotation(object):
    """A class to represent an annotation of a PDF form."""

    def __init__(
        self, annot_name: str, annot_type: str, annot_value: Union[str, bool] = None
    ) -> None:
        """Constructs all attributes for the Annotation object."""

        self._name = annot_name
        self._type = annot_type
        self.value = annot_value

        if annot_type == "text":
            self.font_size = None
            self.text_x_offset = None
            self.text_y_offset = None
            self.text_wrap_length = None

    @property
    def name(self) -> str:
        """Name of the annotation."""

        return self._name

    @property
    def type(self) -> str:
        """Type of the annotation."""

        return self._type

    def validate(self) -> None:
        """Validates text annotation's attributes."""

        if self._type == "text":
            if self.font_size and not (
                isinstance(self.font_size, float) or isinstance(self.font_size, int)
            ):
                raise InvalidFontSizeError

            if self.text_x_offset and not (
                isinstance(self.text_x_offset, float)
                or isinstance(self.text_x_offset, int)
            ):
                raise InvalidTextOffsetError

            if self.text_y_offset and not (
                isinstance(self.text_y_offset, float)
                or isinstance(self.text_y_offset, int)
            ):
                raise InvalidTextOffsetError

            if self.text_wrap_length and not isinstance(self.text_wrap_length, int):
                raise InvalidWrapLengthError
