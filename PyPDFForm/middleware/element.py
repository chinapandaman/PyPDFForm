# -*- coding: utf-8 -*-

from typing import Union

from .exceptions import (InvalidFontColorError, InvalidFontSizeError,
                         InvalidTextOffsetError, InvalidWrapLengthError, InvalidElementValueError)


class Element(object):
    """A class to represent an element of a PDF form."""

    def __init__(
        self,
        element_name: str,
        element_type: str,
        element_value: Union[str, bool] = None,
    ) -> None:
        """Constructs all attributes for the Element object."""

        self._name = element_name
        self._type = element_type
        self.value = element_value

        if element_type == "text":
            self.font_size = None
            self.font_color = None
            self.text_x_offset = None
            self.text_y_offset = None
            self.text_wrap_length = None

    @property
    def name(self) -> str:
        """Name of the element."""

        return self._name

    @property
    def type(self) -> str:
        """Type of the element."""

        return self._type

    def validate_value(self):
        if self._type == "text":
            if self.value is not None and not isinstance(self.value, str):
                raise InvalidElementValueError

        if self._type == "checkbox":
            if self.value is not None and not isinstance(self.value, bool):
                raise InvalidElementValueError

    def validate_text_attributes(self) -> None:
        """Validates text element's attributes."""

        if self._type == "text":
            if self.font_size and not (
                isinstance(self.font_size, float) or isinstance(self.font_size, int)
            ):
                raise InvalidFontSizeError

            if self.font_color and not (
                isinstance(self.font_color, tuple) and len(self.font_color) == 3
            ):
                raise InvalidFontColorError

            if isinstance(self.font_color, tuple):
                for each in self.font_color:
                    if not (isinstance(each, float) or isinstance(each, int)):
                        raise InvalidFontColorError

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
