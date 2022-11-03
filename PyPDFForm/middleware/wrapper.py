# -*- coding: utf-8 -*-
"""Contains user API for PyPDFForm."""

from typing import BinaryIO, Dict, Tuple, Union

from ..core.filler import Filler as FillerCore
from ..core.font import Font as FontCore
from ..core.image import Image as ImageCore
from ..core.template import Template as TemplateCore
from ..core.utils import Utils as UtilsCore
from ..core.watermark import Watermark as WatermarkCore
from .adapter import FileAdapter
from .constants import Text as TextConstants
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
        global_font: str = TextConstants().global_font,
        global_font_size: Union[float, int] = TextConstants().global_font_size,
        global_font_color: Tuple[
            Union[float, int], Union[float, int], Union[float, int]
        ] = TextConstants().global_font_color,
        global_text_x_offset: Union[float, int] = TextConstants().global_text_x_offset,
        global_text_y_offset: Union[float, int] = TextConstants().global_text_y_offset,
        global_text_wrap_length: int = TextConstants().global_text_wrap_length,
        sejda: bool = False,
    ) -> None:
        """Constructs all attributes for the PyPDFForm object."""

        template = FileAdapter().fp_or_f_obj_or_stream_to_stream(template)
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
            TemplateCore().assign_uuid(self.stream) if not self.sejda else self.stream
        )
        pdf_two = (
            TemplateCore().assign_uuid(other.stream)
            if not other.sejda
            else other.stream
        )

        new_obj = self.__class__()
        new_obj.stream = UtilsCore().merge_two_pdfs(pdf_one, pdf_two)

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

        _fill_result = FillerCore().fill(self.stream, self.elements, self.sejda)
        if self.sejda:
            _fill_result = TemplateCore().remove_all_elements(_fill_result)

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

        self.stream = FillerCore().simple_fill(self.stream, data, editable)

        return self

    def draw_text(
        self,
        text: str,
        page_number: int,
        x: Union[float, int],
        y: Union[float, int],
        font: str = TextConstants().global_font,
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

        watermarks = WatermarkCore().create_watermarks_and_draw(
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

        self.stream = WatermarkCore().merge_watermarks_with_pdf(self.stream, watermarks)

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

        image = FileAdapter().fp_or_f_obj_or_stream_to_stream(image)
        if image is None:
            raise InvalidImageError

        if not isinstance(rotation, (float, int)):
            raise InvalidImageRotationAngleError

        if not ImageCore().is_image(image):
            raise InvalidImageError

        image = ImageCore().any_image_to_jpg(image)
        image = ImageCore().rotate_image(image, rotation)

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

        watermarks = WatermarkCore().create_watermarks_and_draw(
            self.stream, page_number, "image", [[image, x, y, width, height]]
        )

        self.stream = WatermarkCore().merge_watermarks_with_pdf(self.stream, watermarks)

        return self

    def read(self) -> bytes:
        """Reads the file stream of a PDF form."""

        return self.stream

    @classmethod
    def register_font(
        cls, font_name: str, ttf_file: Union[bytes, str, BinaryIO]
    ) -> bool:
        """Registers a font from a ttf file."""

        ttf_file = FileAdapter().fp_or_f_obj_or_stream_to_stream(ttf_file)

        if any(
            [
                not font_name,
                not isinstance(font_name, str),
                not ttf_file,
                not isinstance(ttf_file, bytes),
            ]
        ):
            raise InvalidTTFFontError

        if not FontCore().register_font(font_name, ttf_file):
            raise InvalidTTFFontError

        return True


class WrapperV2:
    """A class to represent a PDF form."""

    def __init__(
        self,
        template: Union[bytes, str, BinaryIO] = b"",
        **kwargs,
    ) -> None:
        """Constructs all attributes for the PyPDFForm object."""

        self.stream = FileAdapter().fp_or_f_obj_or_stream_to_stream(template)
        self.elements = (
            TemplateMiddleware().build_elements_v2(self.stream) if self.stream else {}
        )

        for each in self.elements.values():
            if each.type == ElementType.text:
                each.font = kwargs.get("global_font", TextConstants().global_font)
                if each.max_length is None:
                    each.font_size = kwargs.get(
                        "global_font_size", TextConstants().global_font_size
                    )
                each.font_color = kwargs.get(
                    "global_font_color", TextConstants().global_font_color
                )
                each.text_x_offset = kwargs.get(
                    "global_text_x_offset", TextConstants().global_text_x_offset
                )
                each.text_y_offset = kwargs.get(
                    "global_text_y_offset", TextConstants().global_text_y_offset
                )
                each.text_wrap_length = kwargs.get(
                    "global_text_wrap_length", TextConstants().global_text_wrap_length
                )

    def read(self) -> bytes:
        """Reads the file stream of a PDF form."""

        return self.stream

    def __add__(self, other: "WrapperV2") -> "WrapperV2":
        """Overloaded addition operator to perform merging PDFs."""

        if not self.stream:
            return other

        if not other.stream:
            return self

        new_obj = self.__class__()
        new_obj.stream = UtilsCore().merge_two_pdfs(self.stream, other.stream)

        return new_obj

    def fill(
        self,
        data: Dict[str, Union[str, bool, int]],
    ) -> "WrapperV2":
        """Fill a PDF form."""

        for key, value in data.items():
            if key in self.elements:
                self.elements[key].value = value

        self.stream = TemplateCore().remove_all_elements(
            FillerCore().fill_v2(self.stream, self.elements)
        )

        return self

    def draw_text(
        self,
        text: str,
        page_number: int,
        x: Union[float, int],
        y: Union[float, int],
        **kwargs,
    ) -> "WrapperV2":
        """Draws a text on a PDF form."""

        new_element = ElementMiddleware("new", ElementType.text)
        new_element.value = text
        new_element.font = kwargs.get("font", TextConstants().global_font)
        new_element.font_size = kwargs.get(
            "font_size", TextConstants().global_font_size
        )
        new_element.font_color = kwargs.get(
            "font_color", TextConstants().global_font_color
        )
        new_element.text_x_offset = kwargs.get(
            "text_x_offset", TextConstants().global_text_x_offset
        )
        new_element.text_y_offset = kwargs.get(
            "text_y_offset", TextConstants().global_text_y_offset
        )
        new_element.text_wrap_length = kwargs.get(
            "text_wrap_length", TextConstants().global_text_wrap_length
        )

        watermarks = WatermarkCore().create_watermarks_and_draw(
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

        self.stream = WatermarkCore().merge_watermarks_with_pdf(self.stream, watermarks)

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
    ) -> "WrapperV2":
        """Draws an image on a PDF form."""

        image = FileAdapter().fp_or_f_obj_or_stream_to_stream(image)
        image = ImageCore().any_image_to_jpg(image)
        image = ImageCore().rotate_image(image, rotation)
        watermarks = WatermarkCore().create_watermarks_and_draw(
            self.stream, page_number, "image", [[image, x, y, width, height]]
        )

        self.stream = WatermarkCore().merge_watermarks_with_pdf(self.stream, watermarks)

        return self

    def generate_schema(self) -> dict:
        """Generates a json schema for the PDF form template."""

        result = dict()
        result["type"] = "object"
        result["properties"] = {
            key: value.schema_definition for key, value in self.elements.items()
        }

        return result

    @classmethod
    def register_font(
        cls, font_name: str, ttf_file: Union[bytes, str, BinaryIO]
    ) -> bool:
        """Registers a font from a ttf file."""

        ttf_file = FileAdapter().fp_or_f_obj_or_stream_to_stream(ttf_file)

        return FontCore().register_font(font_name, ttf_file)
