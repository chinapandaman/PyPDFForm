# -*- coding: utf-8 -*-
"""Contains v2 user API for PyPDFForm."""

from typing import BinaryIO, Dict, Union

from ..core import filler
from ..core.font import Font as FontCore
from ..core.image import Image as ImageCore
from ..core.template import Template as TemplateCore
from ..core.utils import Utils as UtilsCore
from ..core.watermark import Watermark as WatermarkCore
from .adapter import FileAdapter
from .constants import Text as TextConstants
from .element import Element as ElementMiddleware
from .element import ElementType
from .template import Template as TemplateMiddleware


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

        if self.read():
            self.elements = TemplateMiddleware().set_character_x_paddings(
                self.stream, self.elements
            )

        self.stream = TemplateCore().remove_all_elements(
            filler.fill_v2(self.stream, self.elements)
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

        result = {
            "type": "object",
            "properties": {
                key: value.schema_definition for key, value in self.elements.items()
            },
        }

        return result

    @classmethod
    def register_font(
        cls, font_name: str, ttf_file: Union[bytes, str, BinaryIO]
    ) -> bool:
        """Registers a font from a ttf file."""

        ttf_file = FileAdapter().fp_or_f_obj_or_stream_to_stream(ttf_file)

        return FontCore().register_font(font_name, ttf_file)
