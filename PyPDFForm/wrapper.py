# -*- coding: utf-8 -*-
"""Contains user API for PyPDFForm."""

from __future__ import annotations

from functools import cached_property
from typing import BinaryIO, Dict, List, Tuple, Union

from .adapter import fp_or_f_obj_or_stream_to_stream
from .constants import (DEFAULT_FONT, DEFAULT_FONT_COLOR, DEFAULT_FONT_SIZE,
                        NEW_LINE_SYMBOL, VERSION_IDENTIFIER_PREFIX,
                        VERSION_IDENTIFIERS)
from .coordinate import generate_coordinate_grid
from .filler import fill, simple_fill
from .font import register_font
from .image import rotate_image
from .middleware.dropdown import Dropdown
from .middleware.text import Text
from .template import (build_widgets, dropdown_to_text,
                       set_character_x_paddings, update_text_field_attributes,
                       update_widget_keys)
from .utils import (generate_unique_suffix, get_page_streams, merge_two_pdfs,
                    preview_widget_to_draw, remove_all_widgets)
from .watermark import create_watermarks_and_draw, merge_watermarks_with_pdf
from .widgets.base import handle_non_acro_form_params
from .widgets.checkbox import CheckBoxWidget
from .widgets.dropdown import DropdownWidget
from .widgets.text import TextWidget


class FormWrapper:
    """A simple base wrapper for just filling a PDF form."""

    def __init__(
        self,
        template: Union[bytes, str, BinaryIO] = b"",
    ) -> None:
        """Constructs all attributes for the object."""

        super().__init__()
        self.stream = fp_or_f_obj_or_stream_to_stream(template)

    def read(self) -> bytes:
        """Reads the file stream of a PDF form."""

        return self.stream

    def fill(
        self,
        data: Dict[str, Union[str, bool, int]],
        **kwargs,
    ) -> FormWrapper:
        """Fills a PDF form."""

        widgets = build_widgets(self.stream, False, False) if self.stream else {}

        for key, value in data.items():
            if key in widgets:
                widgets[key].value = value

        self.stream = simple_fill(
            self.read(),
            widgets,
            flatten=kwargs.get("flatten", False),
            adobe_mode=kwargs.get("adobe_mode", False),
        )

        return self


class PdfWrapper(FormWrapper):
    """A class to represent a PDF form."""

    USER_PARAMS = [
        ("global_font", None),
        ("global_font_size", None),
        ("global_font_color", None),
        ("use_full_widget_name", False),
        ("render_widgets", True),
    ]

    def __init__(
        self,
        template: Union[bytes, str, BinaryIO] = b"",
        **kwargs,
    ) -> None:
        """Constructs all attributes for the object."""

        super().__init__(template)
        self.widgets = {}
        self._keys_to_update = []

        for attr, default in self.USER_PARAMS:
            setattr(self, attr, kwargs.get(attr, default))

        self._init_helper()

    def _init_helper(self, key_to_refresh: str = None) -> None:
        """Updates all attributes when the state of the PDF stream changes."""

        refresh_not_needed = {}
        new_widgets = (
            build_widgets(
                self.read(),
                getattr(self, "use_full_widget_name"),
                getattr(self, "render_widgets"),
            )
            if self.read()
            else {}
        )
        for k, v in self.widgets.items():
            if k in new_widgets:
                new_widgets[k] = v
                refresh_not_needed[k] = True
        self.widgets = new_widgets

        for key, value in self.widgets.items():
            if (key_to_refresh and key == key_to_refresh) or (
                key_to_refresh is None
                and isinstance(value, Text)
                and not refresh_not_needed.get(key)
            ):
                value.font = getattr(self, "global_font")
                value.font_size = getattr(self, "global_font_size")
                value.font_color = getattr(self, "global_font_color")

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

    @cached_property
    def pages(self) -> List[PdfWrapper]:
        """Returns a list of pdf wrapper objects where each is a page of the PDF form."""

        return [
            self.__class__(
                each, **{param: getattr(self, param) for param, _ in self.USER_PARAMS}
            )
            for each in get_page_streams(self.stream)
        ]

    def change_version(self, version: str) -> PdfWrapper:
        """Changes the version of the PDF."""

        self.stream = self.stream.replace(
            VERSION_IDENTIFIER_PREFIX + bytes(self.version, "utf-8"),
            VERSION_IDENTIFIER_PREFIX + bytes(version, "utf-8"),
            1,
        )

        return self

    def __add__(self, other: PdfWrapper) -> PdfWrapper:
        """Overloaded addition operator to perform merging PDFs."""

        if not self.stream:
            return other

        if not other.stream:
            return self

        unique_suffix = generate_unique_suffix()
        for k in self.widgets:
            if k in other.widgets:
                other.update_widget_key(k, f"{k}-{unique_suffix}", defer=True)

        other.commit_widget_key_updates()

        return self.__class__(merge_two_pdfs(self.stream, other.stream))

    @property
    def preview(self) -> bytes:
        """Inspects all supported widgets' names for the PDF form."""

        return remove_all_widgets(
            fill(
                self.stream,
                {
                    key: preview_widget_to_draw(value, True)
                    for key, value in self.widgets.items()
                },
            )
        )

    def generate_coordinate_grid(
        self, color: Tuple[float, float, float] = (1, 0, 0), margin: float = 100
    ) -> PdfWrapper:
        """Inspects a coordinate grid of the PDF."""

        self.stream = generate_coordinate_grid(
            remove_all_widgets(
                fill(
                    self.stream,
                    {
                        key: preview_widget_to_draw(value, False)
                        for key, value in self.widgets.items()
                    },
                )
            ),
            color,
            margin,
        )

        return self

    def fill(
        self,
        data: Dict[str, Union[str, bool, int]],
        **kwargs,
    ) -> PdfWrapper:
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

    def create_widget(
        self,
        widget_type: str,
        name: str,
        page_number: int,
        x: float,
        y: float,
        **kwargs,
    ) -> PdfWrapper:
        """Creates a new widget on a PDF form."""

        _class = None
        if widget_type == "text":
            _class = TextWidget
        if widget_type == "checkbox":
            _class = CheckBoxWidget
        if widget_type == "dropdown":
            _class = DropdownWidget
        if _class is None:
            return self

        obj = _class(name=name, page_number=page_number, x=x, y=y, **kwargs)
        watermarks = obj.watermarks(self.read())

        self.stream = merge_watermarks_with_pdf(self.read(), watermarks)
        if obj.non_acro_form_params:
            self.stream = handle_non_acro_form_params(
                self.stream, name, obj.non_acro_form_params
            )

        key_to_refresh = ""
        if widget_type in ("text", "dropdown"):
            key_to_refresh = name

        self._init_helper(key_to_refresh)

        return self

    def update_widget_key(
        self, old_key: str, new_key: str, index: int = 0, defer: bool = False
    ) -> PdfWrapper:
        """Updates the key of an existed widget on a PDF form."""

        if getattr(self, "use_full_widget_name"):
            raise NotImplementedError

        if defer:
            self._keys_to_update.append((old_key, new_key, index))
            return self

        self.stream = update_widget_keys(
            self.read(), self.widgets, [old_key], [new_key], [index]
        )
        self._init_helper()

        return self

    def commit_widget_key_updates(self) -> PdfWrapper:
        """Commits all deferred widget key updates on a PDF form."""

        if getattr(self, "use_full_widget_name"):
            raise NotImplementedError

        old_keys = [each[0] for each in self._keys_to_update]
        new_keys = [each[1] for each in self._keys_to_update]
        indices = [each[2] for each in self._keys_to_update]

        self.stream = update_widget_keys(
            self.read(), self.widgets, old_keys, new_keys, indices
        )
        self._init_helper()
        self._keys_to_update = []

        return self

    def draw_text(
        self,
        text: str,
        page_number: int,
        x: Union[float, int],
        y: Union[float, int],
        **kwargs,
    ) -> PdfWrapper:
        """Draws a text on a PDF form."""

        new_widget = Text("new")
        new_widget.value = text
        new_widget.font = kwargs.get("font", DEFAULT_FONT)
        new_widget.font_size = kwargs.get("font_size", DEFAULT_FONT_SIZE)
        new_widget.font_color = kwargs.get("font_color", DEFAULT_FONT_COLOR)

        if NEW_LINE_SYMBOL in text:
            new_widget.text_lines = text.split(NEW_LINE_SYMBOL)

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
    ) -> PdfWrapper:
        """Draws an image on a PDF form."""

        image = fp_or_f_obj_or_stream_to_stream(image)
        image = rotate_image(image, rotation)
        watermarks = create_watermarks_and_draw(
            self.stream, page_number, "image", [[image, x, y, width, height]]
        )

        self.stream = merge_watermarks_with_pdf(self.stream, watermarks)

        return self

    @property
    def schema(self) -> dict:
        """Generates a json schema for the PDF form template."""

        return {
            "type": "object",
            "properties": {
                key: value.schema_definition for key, value in self.widgets.items()
            },
        }

    @classmethod
    def register_font(
        cls, font_name: str, ttf_file: Union[bytes, str, BinaryIO]
    ) -> bool:
        """Registers a font from a ttf file."""

        ttf_file = fp_or_f_obj_or_stream_to_stream(ttf_file)

        return register_font(font_name, ttf_file) if ttf_file is not None else False
