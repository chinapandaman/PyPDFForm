# -*- coding: utf-8 -*-
"""Contains user API for PyPDFForm."""

from typing import BinaryIO, Dict, Tuple, Union

from ..core import filler
from ..core import font as font_core
from ..core import image as image_core
from ..core import template
from ..core import utils
from ..core import watermark as watermark_core
from . import adapter
from . import constants
from .element import Element as ElementMiddleware
from .element import ElementType
from .exceptions.input import (InvalidCoordinateError,
                               InvalidEditableParameterError,
                               InvalidFormDataError,
                               InvalidImageDimensionError, InvalidImageError,
                               InvalidImageRotationAngleError,
                               InvalidModeError, InvalidPageNumberError,
                               InvalidTextError, InvalidTTFFontError)
from .template import Template as TemplateMiddleware


class PyPDFForm:
    """A class to represent a PDF form."""

    def __init__(
        self,
        template: Union[bytes, str, BinaryIO] = b"",
        simple_mode: bool = True,
        global_font: str = constants.GLOBAL_FONT,
        global_font_size: Union[float, int] = constants.GLOBAL_FONT_SIZE,
        global_font_color: Tuple[
            Union[float, int], Union[float, int], Union[float, int]
        ] = constants.GLOBAL_FONT_COLOR,
        global_text_x_offset: Union[float, int] = constants.GLOBAL_TEXT_X_OFFSET,
        global_text_y_offset: Union[float, int] = constants.GLOBAL_TEXT_Y_OFFSET,
        global_text_wrap_length: int = constants.GLOBAL_TEXT_WRAP_LENGTH,
        sejda: bool = False,
    ) -> None:
        """Constructs all attributes for the PyPDFForm object."""

        template = adapter.fp_or_f_obj_or_stream_to_stream(template)
        TemplateMiddleware().validate_template(template)
        if not isinstance(simple_mode, bool):
            raise InvalidModeError
        if not isinstance(sejda, bool):
            raise InvalidModeError

        self.stream = template
        self.simple_mode = simple_mode
        self.sejda = sejda
        self.fill = self._simple_fill if simple_mode and not sejda else self._fill

        if not simple_mode or sejda:
            self.elements = {}
            if template:
                TemplateMiddleware().validate_stream(template)
                self.elements = TemplateMiddleware().build_elements(template, sejda)

            for each in self.elements.values():
                if each.type == ElementType.text:
                    each.font = global_font
                    each.font_size = global_font_size
                    each.font_color = global_font_color
                    each.text_x_offset = global_text_x_offset
                    each.text_y_offset = global_text_y_offset
                    each.text_wrap_length = global_text_wrap_length
                each.validate_constants()
                each.validate_value()
                each.validate_text_attributes()

    def __add__(self, other: "PyPDFForm") -> "PyPDFForm":
        """Overloaded addition operator to perform merging PDFs."""

        if not self.stream:
            return other

        if not other.stream:
            return self

        TemplateMiddleware().validate_stream(self.stream)
        TemplateMiddleware().validate_stream(other.stream)

        pdf_one = (
            template.assign_uuid(self.stream) if not self.sejda else self.stream
        )
        pdf_two = (
            template.assign_uuid(other.stream)
            if not other.sejda
            else other.stream
        )

        new_obj = self.__class__()
        new_obj.stream = utils.merge_two_pdfs(pdf_one, pdf_two)

        return new_obj

    def _fill(
        self,
        data: Dict[str, Union[str, bool, int]],
    ) -> "PyPDFForm":
        """Fill a PDF form with customized parameters."""

        TemplateMiddleware().validate_stream(self.stream)

        if not isinstance(data, dict):
            raise InvalidFormDataError

        for key, value in data.items():
            if not isinstance(key, str):
                raise InvalidFormDataError
            if not isinstance(value, (str, bool, int)):
                raise InvalidFormDataError

        for key, value in data.items():
            if key in self.elements:
                self.elements[key].value = value
                self.elements[key].validate_constants()
                self.elements[key].validate_value()
                self.elements[key].validate_text_attributes()

        _fill_result = filler.fill(self.stream, self.elements, self.sejda)
        if self.sejda:
            _fill_result = template.remove_all_elements(_fill_result)

        self.stream = _fill_result

        return self

    def _simple_fill(
        self,
        data: Dict[str, Union[str, bool, int]],
        editable: bool = False,
    ) -> "PyPDFForm":
        """Fills a PDF form in simple mode."""

        TemplateMiddleware().validate_stream(self.stream)

        if not isinstance(data, dict):
            raise InvalidFormDataError

        for key, value in data.items():
            if not isinstance(key, str):
                raise InvalidFormDataError
            if not isinstance(value, (str, bool, int)):
                raise InvalidFormDataError

        if not isinstance(editable, bool):
            raise InvalidEditableParameterError

        self.stream = filler.simple_fill(self.stream, data, editable)

        return self

    def draw_text(
        self,
        text: str,
        page_number: int,
        x: Union[float, int],
        y: Union[float, int],
        font: str = constants.GLOBAL_FONT,
        font_size: Union[float, int] = constants.GLOBAL_FONT_SIZE,
        font_color: Tuple[
            Union[float, int], Union[float, int], Union[float, int]
        ] = constants.GLOBAL_FONT_COLOR,
        text_x_offset: Union[float, int] = constants.GLOBAL_TEXT_X_OFFSET,
        text_y_offset: Union[float, int] = constants.GLOBAL_TEXT_Y_OFFSET,
        text_wrap_length: int = constants.GLOBAL_TEXT_WRAP_LENGTH,
    ) -> "PyPDFForm":
        """Draws a text on a PDF form."""

        TemplateMiddleware().validate_stream(self.stream)

        if not isinstance(text, str):
            raise InvalidTextError

        if not isinstance(page_number, int):
            raise InvalidPageNumberError

        if not isinstance(x, (float, int)):
            raise InvalidCoordinateError

        if not isinstance(y, (float, int)):
            raise InvalidCoordinateError

        new_element = ElementMiddleware("new", ElementType.text)
        new_element.value = text
        new_element.font = font
        new_element.font_size = font_size
        new_element.font_color = font_color
        new_element.text_x_offset = text_x_offset
        new_element.text_y_offset = text_y_offset
        new_element.text_wrap_length = text_wrap_length
        new_element.validate_constants()
        new_element.validate_value()
        new_element.validate_text_attributes()

        watermarks = watermark_core.create_watermarks_and_draw(
            self.stream,
            page_number,
            "text",
            [
                [
                    new_element,
                    x,
                    y,
                ]
            ],
        )

        self.stream = watermark_core.merge_watermarks_with_pdf(self.stream, watermarks)

        return self

    def draw_image(
        self,
        image: Union[bytes, str, BinaryIO],
        page_number: int,
        x: Union[float, int],
        y: Union[float, int],
        width: Union[float, int],
        height: Union[float, int],
        rotation: Union[float, int] = 0,
    ) -> "PyPDFForm":
        """Draws an image on a PDF form."""

        TemplateMiddleware().validate_stream(self.stream)

        image = adapter.fp_or_f_obj_or_stream_to_stream(image)
        if image is None:
            raise InvalidImageError

        if not isinstance(rotation, (float, int)):
            raise InvalidImageRotationAngleError

        if not image_core.is_image(image):
            raise InvalidImageError

        image = image_core.any_image_to_jpg(image)
        image = image_core.rotate_image(image, rotation)

        if not isinstance(page_number, int):
            raise InvalidPageNumberError

        if not isinstance(x, (float, int)):
            raise InvalidCoordinateError

        if not isinstance(y, (float, int)):
            raise InvalidCoordinateError

        if not isinstance(width, (float, int)):
            raise InvalidImageDimensionError

        if not isinstance(height, (float, int)):
            raise InvalidImageDimensionError

        watermarks = watermark_core.create_watermarks_and_draw(
            self.stream, page_number, "image", [[image, x, y, width, height]]
        )

        self.stream = watermark_core.merge_watermarks_with_pdf(self.stream, watermarks)

        return self

    def read(self) -> bytes:
        """Reads the file stream of a PDF form."""

        return self.stream

    @classmethod
    def register_font(
        cls, font_name: str, ttf_file: Union[bytes, str, BinaryIO]
    ) -> bool:
        """Registers a font from a ttf file."""

        ttf_file = adapter.fp_or_f_obj_or_stream_to_stream(ttf_file)

        if any(
            [
                not font_name,
                not isinstance(font_name, str),
                not ttf_file,
                not isinstance(ttf_file, bytes),
            ]
        ):
            raise InvalidTTFFontError

        if not font_core.register_font(font_name, ttf_file):
            raise InvalidTTFFontError

        return True
