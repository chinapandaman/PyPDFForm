# -*- coding: utf-8 -*-
"""Contains user API for PyPDFForm."""

from __future__ import annotations

from typing import BinaryIO, Dict, List, Union

from .core.constants import DEFAULT_FONT, DEFAULT_FONT_COLOR, DEFAULT_FONT_SIZE
from .core.filler import fill
from .core.font import register_font, update_text_field_attributes
from .core.image import any_image_to_jpg, rotate_image
from .core.utils import (get_page_streams, merge_two_pdfs,
                         preview_widget_to_draw, remove_all_widgets)
from .core.watermark import (create_watermarks_and_draw,
                             merge_watermarks_with_pdf)
from .middleware.adapter import fp_or_f_obj_or_stream_to_stream
from .middleware.constants import (DEPRECATION_NOTICE, VERSION_IDENTIFIER_PREFIX,
                                   VERSION_IDENTIFIERS)
from .middleware.dropdown import Dropdown
from .middleware.template import (build_widgets, dropdown_to_text,
                                  set_character_x_paddings)
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
        self.widgets = build_widgets(self.stream) if self.stream else {}

        for each in self.widgets.values():
            if isinstance(each, Text):
                each.font = kwargs.get("global_font")
                each.font_size = kwargs.get("global_font_size")
                each.font_color = kwargs.get("global_font_color")

    def read(self) -> bytes:
        """Reads the file stream of a PDF form."""

        return self.stream

    @property
    def elements(self) -> None:
        """Deprecated elements attribute."""

        raise DeprecationWarning(
            DEPRECATION_NOTICE.format(
                "Wrapper.elements",
                "Wrapper.widgets"
            )
        )

    @property
    def sample_data(self) -> dict:
        """Returns a valid sample data that can be filled into the PDF form."""

        return {key: value.sample_value for key, value in self.widgets.items()}

    @property
    def version(self) -> Union[str, None]:
        """Gets the version of the PDF."""

        for each in VERSION_IDENTIFIERS:
            if self.stream.startswith(each):
                return each.replace(VERSION_IDENTIFIER_PREFIX, b"").decode()

        return None

    @property
    def pages(self) -> List[Wrapper]:
        """Returns a list of wrapper objects where each is a page of the PDF form."""

        return [self.__class__(each) for each in get_page_streams(self.stream)]

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
        """Inspects all supported widgets' names for the PDF form."""

        return fill(
            self.stream,
            {
                key: preview_widget_to_draw(value)
                for key, value in self.widgets.items()
            },
        )

    def fill(
        self,
        data: Dict[str, Union[str, bool, int]],
    ) -> Wrapper:
        """Fills a PDF form."""

        for key, value in data.items():
            if key in self.widgets:
                self.widgets[key].value = value

        for key, value in self.widgets.items():
            if isinstance(value, Dropdown):
                self.widgets[key] = dropdown_to_text(value)

        update_text_field_attributes(self.stream, self.widgets)
        if self.read():
            self.widgets = set_character_x_paddings(self.stream, self.widgets)

        self.stream = remove_all_widgets(fill(self.stream, self.widgets))

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

        new_widget = Text("new")
        new_widget.value = text
        new_widget.font = kwargs.get("font", DEFAULT_FONT)
        new_widget.font_size = kwargs.get("font_size", DEFAULT_FONT_SIZE)
        new_widget.font_color = kwargs.get("font_color", DEFAULT_FONT_COLOR)

        watermarks = create_watermarks_and_draw(
            self.stream,
            page_number,
            "text",
            [
                [
                    new_widget,
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
                key: value.schema_definition for key, value in self.widgets.items()
            },
        }

        return result

    @classmethod
    def register_font(
        cls, font_name: str, ttf_file: Union[bytes, str, BinaryIO]
    ) -> bool:
        """Registers a font from a ttf file."""

        ttf_file = fp_or_f_obj_or_stream_to_stream(ttf_file)

        return register_font(font_name, ttf_file) if ttf_file is not None else False
