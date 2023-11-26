# -*- coding: utf-8 -*-
"""Contains user API for PyPDFForm."""

from __future__ import annotations

from typing import BinaryIO, Dict, Union

from .core.constants import DEFAULT_FONT, \
    DEFAULT_FONT_SIZE, DEFAULT_FONT_COLOR
from .core.filler import fill
from .core.font import register_font, update_text_field_attributes
from .core.image import any_image_to_jpg, rotate_image
from .core.utils import merge_two_pdfs, \
    preview_element_to_draw, remove_all_elements
from .core.watermark import create_watermarks_and_draw, \
    merge_watermarks_with_pdf
from .middleware.adapter import fp_or_f_obj_or_stream_to_stream
from .middleware.constants import VERSION_IDENTIFIERS, \
    VERSION_IDENTIFIER_PREFIX
from .middleware.dropdown import Dropdown
from .middleware.template import build_elements, \
    dropdown_to_text, set_character_x_paddings
from .middleware.text import Text


class Wrapper:
    """A class to represent a PDF form."""

    def __init__(
        self,
        template: Union[bytes, str, BinaryIO] = b"",
        **kwargs,
    ) -> None:
        """Constructs all attributes for the object."""

        self.stream = fp_or_f_obj_or_stream_to_stream(template)
        self.elements = (
            build_elements(self.stream) if self.stream else {}
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

        for each in VERSION_IDENTIFIERS:
            if self.stream.startswith(each):
                return each.replace(VERSION_IDENTIFIER_PREFIX, b"").decode()

        return None

    def change_version(self, version: str) -> Wrapper:
        """Changes the version of the PDF."""

        self.stream = self.stream.replace(
            VERSION_IDENTIFIER_PREFIX + bytes(self.version, "utf-8"),
            VERSION_IDENTIFIER_PREFIX + bytes(version, "utf-8"),
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
        new_obj.stream = merge_two_pdfs(self.stream, other.stream)

        return new_obj

    @property
    def preview(self) -> bytes:
        """Inspects all supported elements' names for the PDF form."""

        return fill(
            self.stream,
            {
                key: preview_element_to_draw(value)
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
                self.elements[key] = dropdown_to_text(value)

        update_text_field_attributes(self.stream, self.elements)
        if self.read():
            self.elements = set_character_x_paddings(
                self.stream, self.elements
            )

        self.stream = remove_all_elements(fill(self.stream, self.elements))

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
        new_element.font = kwargs.get("font", DEFAULT_FONT)
        new_element.font_size = kwargs.get(
            "font_size", DEFAULT_FONT_SIZE
        )
        new_element.font_color = kwargs.get(
            "font_color", DEFAULT_FONT_COLOR
        )

        watermarks = create_watermarks_and_draw(
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

        self.stream = merge_watermarks_with_pdf(self.stream, watermarks)

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

        image = fp_or_f_obj_or_stream_to_stream(image)
        image = any_image_to_jpg(image)
        image = rotate_image(image, rotation)
        watermarks = create_watermarks_and_draw(
            self.stream, page_number, "image", [[image, x, y, width, height]]
        )

        self.stream = merge_watermarks_with_pdf(self.stream, watermarks)

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

        ttf_file = fp_or_f_obj_or_stream_to_stream(ttf_file)

        return (
            register_font(font_name, ttf_file) if ttf_file is not None else False
        )
