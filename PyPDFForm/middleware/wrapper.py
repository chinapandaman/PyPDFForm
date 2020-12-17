# -*- coding: utf-8 -*-

from typing import Tuple, Union

from ..core.filler import Filler as FillerCore
from ..core.image import Image as ImageCore
from ..core.watermark import Watermark as WatermarkCore
from .constants import Text as TextConstants
from .element import Element as ElementMiddleware
from .element import ElementType
from .exceptions.input import (InvalidCoordinateError,
                               InvalidEditableParameterError,
                               InvalidFormDataError,
                               InvalidImageDimensionError, InvalidImageError,
                               InvalidImageRotationAngleError,
                               InvalidModeError, InvalidPageNumberError,
                               InvalidTextError)
from .template import Template as TemplateMiddleware


class PyPDFForm(object):
    """A class to represent a PDF form."""

    def __init__(self,
                 template: bytes = b"",
                 simple_mode: bool = True,
                 global_font_size: Union[float, int] = TextConstants().global_font_size,
                 global_font_color: Tuple[
                     Union[float, int], Union[float, int], Union[float, int]
                 ] = TextConstants().global_font_color,
                 global_text_x_offset: Union[float, int] = TextConstants().global_text_x_offset,
                 global_text_y_offset: Union[float, int] = TextConstants().global_text_y_offset,
                 global_text_wrap_length: int = TextConstants().global_text_wrap_length,
                 ) -> None:
        """Constructs all attributes for the PyPDFForm object."""

        TemplateMiddleware().validate_template(template)
        if not isinstance(simple_mode, bool):
            raise InvalidModeError

        self.stream = template
        self.simple_mode = simple_mode
        self.fill = self._simple_fill if simple_mode else self._fill

        if not simple_mode:
            self.elements = {}
            if template:
                TemplateMiddleware().validate_stream(template)
                self.elements = TemplateMiddleware().build_elements(template)

            for each in self.elements.values():
                if each.type == ElementType.text:
                    each.font_size = global_font_size
                    each.font_color = global_font_color
                    each.text_x_offset = global_text_x_offset
                    each.text_y_offset = global_text_y_offset
                    each.text_wrap_length = global_text_wrap_length
                each.validate_constants()
                each.validate_value()
                each.validate_text_attributes()

    def _fill(
        self,
        data: dict,
    ) -> "PyPDFForm":
        """Fill a PDF form with customized parameters."""

        TemplateMiddleware().validate_stream(self.stream)

        if not isinstance(data, dict):
            raise InvalidFormDataError

        for k, v in data.items():
            if k in self.elements:
                self.elements[k].value = v
                self.elements[k].validate_constants()
                self.elements[k].validate_value()
                self.elements[k].validate_text_attributes()

        self.stream = FillerCore().fill(
            self.stream, self.elements
        )

        return self

    def _simple_fill(self, data: dict, editable: bool = False) -> "PyPDFForm":
        """Fills a PDF form in simple mode."""

        TemplateMiddleware().validate_stream(self.stream)

        if not isinstance(data, dict):
            raise InvalidFormDataError

        if not (isinstance(editable, bool)):
            raise InvalidEditableParameterError

        self.stream = FillerCore().simple_fill(
            self.stream, data, editable
        )

        return self

    def draw_text(
        self,
        text: str,
        page_number: int,
        x: Union[float, int],
        y: Union[float, int],
        font_size: Union[float, int] = TextConstants().global_font_size,
        font_color: Tuple[
            Union[float, int], Union[float, int], Union[float, int]
        ] = TextConstants().global_font_color,
        text_x_offset: Union[float, int] = TextConstants().global_text_x_offset,
        text_y_offset: Union[float, int] = TextConstants().global_text_y_offset,
        text_wrap_length: int = TextConstants().global_text_wrap_length,
    ) -> "PyPDFForm":
        """Draws a text on a PDF form."""

        TemplateMiddleware().validate_stream(self.stream)

        if not isinstance(text, str):
            raise InvalidTextError

        if not isinstance(page_number, int):
            raise InvalidPageNumberError

        if not (isinstance(x, float) or isinstance(x, int)):
            raise InvalidCoordinateError

        if not (isinstance(y, float) or isinstance(y, int)):
            raise InvalidCoordinateError

        new_element = ElementMiddleware("new", ElementType.text)
        new_element.value = text
        new_element.font_size = font_size
        new_element.font_color = font_color
        new_element.text_x_offset = text_x_offset
        new_element.text_y_offset = text_y_offset
        new_element.text_wrap_length = text_wrap_length
        new_element.validate_constants()
        new_element.validate_value()
        new_element.validate_text_attributes()

        watermarks = WatermarkCore().create_watermarks_and_draw(
            self.stream,
            page_number,
            "text",
            [
                [
                    new_element,
                    x,
                    y,
                    TextConstants().global_font,
                ]
            ],
        )

        self.stream = WatermarkCore().merge_watermarks_with_pdf(self.stream, watermarks)

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
        """Draws an image on a PDF form."""

        TemplateMiddleware().validate_stream(self.stream)

        if not (isinstance(rotation, float) or isinstance(rotation, int)):
            raise InvalidImageRotationAngleError

        try:
            image = ImageCore().rotate_image(image, rotation)
        except Exception:
            raise InvalidImageError

        if not isinstance(page_number, int):
            raise InvalidPageNumberError

        if not (isinstance(x, float) or isinstance(x, int)):
            raise InvalidCoordinateError

        if not (isinstance(y, float) or isinstance(y, int)):
            raise InvalidCoordinateError

        if not (isinstance(width, float) or isinstance(width, int)):
            raise InvalidImageDimensionError

        if not (isinstance(height, float) or isinstance(height, int)):
            raise InvalidImageDimensionError

        watermarks = WatermarkCore().create_watermarks_and_draw(
            self.stream, page_number, "image", [[image, x, y, width, height]]
        )

        self.stream = WatermarkCore().merge_watermarks_with_pdf(self.stream, watermarks)

        return self
