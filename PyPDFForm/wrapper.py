# -*- coding: utf-8 -*-
"""Contains user API for PyPDFForm."""

from __future__ import annotations

from typing import BinaryIO, Dict, Union

from .core import constants as core_constants
from .core import filler, font
from .core import image as image_core
from .core import utils
from .core import watermark as watermark_core
from .middleware import adapter, constants
from .middleware import template as template_middleware
from .middleware.dropdown import Dropdown
from .middleware.text import Text


class Wrapper:
    """A class to represent a PDF form."""

    def __init__(
        self,
        template: Union[bytes, str, BinaryIO] = b"",
        **kwargs,
    ) -> None:
        """Constructs all attributes for the object."""

        self.stream = adapter.fp_or_f_obj_or_stream_to_stream(template)
        self.elements = (
            template_middleware.build_elements(self.stream) if self.stream else {}
        )

        for each in self.elements.values():
            if isinstance(each, Text):
                each.font = kwargs.get("global_font")
                each.font_size = kwargs.get("global_font_size")
                each.font_color = kwargs.get("global_font_color")

    def read(self) -> bytes:
        """Reads the file stream of a PDF form."""

        return self.stream

    @property
    def sample_data(self) -> dict:
        """Returns a valid sample data that can be filled into the PDF form."""

        return {key: value.sample_value for key, value in self.elements.items()}

    @property
    def version(self) -> Union[str, None]:
        """Gets the version of the PDF."""

        for each in constants.VERSION_IDENTIFIERS:
            if self.stream.startswith(each):
                return each.replace(constants.VERSION_IDENTIFIER_PREFIX, b"").decode()

        return None

    def change_version(self, version: str) -> Wrapper:
        """Changes the version of the PDF."""

        self.stream = self.stream.replace(
            constants.VERSION_IDENTIFIER_PREFIX + bytes(self.version, "utf-8"),
            constants.VERSION_IDENTIFIER_PREFIX + bytes(version, "utf-8"),
            1,
        )

        return self

    def __add__(self, other: Wrapper) -> Wrapper:
        """Overloaded addition operator to perform merging PDFs."""

        if not self.stream:
            return other

        if not other.stream:
            return self

        new_obj = self.__class__()
        new_obj.stream = utils.merge_two_pdfs(self.stream, other.stream)

        return new_obj

    @property
    def preview(self) -> bytes:
        """Inspects all supported elements' names for the PDF form."""

        return filler.fill(
            self.stream,
            {
                key: utils.preview_element_to_draw(value)
                for key, value in self.elements.items()
            },
        )

    def fill(
        self,
        data: Dict[str, Union[str, bool, int]],
    ) -> Wrapper:
        """Fills a PDF form."""

        for key, value in data.items():
            if key in self.elements:
                self.elements[key].value = value

        for key, value in self.elements.items():
            if isinstance(value, Dropdown):
                self.elements[key] = template_middleware.dropdown_to_text(value)

        utils.update_text_field_attributes(self.stream, self.elements)
        if self.read():
            self.elements = template_middleware.set_character_x_paddings(
                self.stream, self.elements
            )

        self.stream = utils.remove_all_elements(filler.fill(self.stream, self.elements))

        return self

    def draw_text(
        self,
        text: str,
        page_number: int,
        x: Union[float, int],
        y: Union[float, int],
        **kwargs,
    ) -> Wrapper:
        """Draws a text on a PDF form."""

        new_element = Text("new")
        new_element.value = text
        new_element.font = kwargs.get("font", core_constants.DEFAULT_FONT)
        new_element.font_size = kwargs.get(
            "font_size", core_constants.DEFAULT_FONT_SIZE
        )
        new_element.font_color = kwargs.get(
            "font_color", core_constants.DEFAULT_FONT_COLOR
        )

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
    ) -> Wrapper:
        """Draws an image on a PDF form."""

        image = adapter.fp_or_f_obj_or_stream_to_stream(image)
        image = image_core.any_image_to_jpg(image)
        image = image_core.rotate_image(image, rotation)
        watermarks = watermark_core.create_watermarks_and_draw(
            self.stream, page_number, "image", [[image, x, y, width, height]]
        )

        self.stream = watermark_core.merge_watermarks_with_pdf(self.stream, watermarks)

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

        ttf_file = adapter.fp_or_f_obj_or_stream_to_stream(ttf_file)

        return (
            font.register_font(font_name, ttf_file) if ttf_file is not None else False
        )
