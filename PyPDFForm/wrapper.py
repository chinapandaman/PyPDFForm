# -*- coding: utf-8 -*-

from __future__ import annotations

from functools import cached_property
from typing import BinaryIO, Dict, List, Tuple, Union

from .adapter import fp_or_f_obj_or_stream_to_stream
from .constants import (DEFAULT_FONT, DEFAULT_FONT_COLOR, DEFAULT_FONT_SIZE,
                        VERSION_IDENTIFIER_PREFIX, VERSION_IDENTIFIERS)
from .coordinate import generate_coordinate_grid
from .filler import simple_fill
from .font import (get_all_available_fonts, register_font,
                   register_font_acroform)
from .hooks import trigger_widget_hooks
from .image import rotate_image
from .middleware.signature import Signature
from .middleware.text import Text
from .template import build_widgets, update_widget_keys
from .utils import (generate_unique_suffix, get_page_streams, merge_two_pdfs,
                    remove_all_widgets)
from .watermark import (copy_watermark_widgets, create_watermarks_and_draw,
                        merge_watermarks_with_pdf)
from .widgets.checkbox import CheckBoxWidget
from .widgets.dropdown import DropdownWidget
from .widgets.image import ImageWidget
from .widgets.radio import RadioWidget
from .widgets.signature import SignatureWidget
from .widgets.text import TextWidget


class PdfWrapper:
    USER_PARAMS = [
        ("global_font", None),
        ("global_font_size", None),
        ("global_font_color", None),
        ("use_full_widget_name", False),
    ]

    def __init__(
        self,
        template: Union[bytes, str, BinaryIO] = b"",
        **kwargs,
    ) -> None:
        super().__init__()
        self._stream = fp_or_f_obj_or_stream_to_stream(template)
        self.widgets = {}
        self._available_fonts = {}
        self._font_register_events = []
        self._keys_to_update = []

        for attr, default in self.USER_PARAMS:
            setattr(self, attr, kwargs.get(attr, default))

        self._init_helper()

    def _init_helper(self, key_to_refresh: str = None) -> None:
        refresh_not_needed = {}
        new_widgets = (
            build_widgets(
                self.read(),
                getattr(self, "use_full_widget_name"),
            )
            if self.read()
            else {}
        )
        for k, v in self.widgets.items():
            if k in new_widgets:
                new_widgets[k] = v
                refresh_not_needed[k] = True
        self.widgets = new_widgets

        if self.read():
            self._available_fonts.update(**get_all_available_fonts(self.read()))

        for key, value in self.widgets.items():
            if (key_to_refresh and key == key_to_refresh) or (
                key_to_refresh is None
                and isinstance(value, Text)
                and not refresh_not_needed.get(key)
            ):
                value.font = getattr(self, "global_font")
                value.font_size = getattr(self, "global_font_size")
                value.font_color = getattr(self, "global_font_color")

    def read(self) -> bytes:
        if any(widget.hooks_to_trigger for widget in self.widgets.values()):
            for widget in self.widgets.values():
                if (
                    isinstance(widget, Text)
                    and widget.font not in self._available_fonts.values()
                ):
                    widget.font = self._available_fonts.get(widget.font)

            self._stream = trigger_widget_hooks(
                self._stream,
                self.widgets,
                getattr(self, "use_full_widget_name"),
            )

        return self._stream

    @property
    def sample_data(self) -> dict:
        return {key: value.sample_value for key, value in self.widgets.items()}

    @property
    def version(self) -> Union[str, None]:
        for each in VERSION_IDENTIFIERS:
            if self.read().startswith(each):
                return each.replace(VERSION_IDENTIFIER_PREFIX, b"").decode()

        return None

    @cached_property
    def pages(self) -> List[PdfWrapper]:
        return [
            self.__class__(
                copy_watermark_widgets(each, self.read(), None, i),
                **{param: getattr(self, param) for param, _ in self.USER_PARAMS},
            )
            for i, each in enumerate(get_page_streams(remove_all_widgets(self.read())))
        ]

    def change_version(self, version: str) -> PdfWrapper:
        self._stream = self.read().replace(
            VERSION_IDENTIFIER_PREFIX + bytes(self.version, "utf-8"),
            VERSION_IDENTIFIER_PREFIX + bytes(version, "utf-8"),
            1,
        )

        return self

    def __add__(self, other: PdfWrapper) -> PdfWrapper:
        if not self.read():
            return other

        if not other.read():
            return self

        unique_suffix = generate_unique_suffix()
        for k in self.widgets:
            if k in other.widgets:
                other.update_widget_key(k, f"{k}-{unique_suffix}", defer=True)

        other.commit_widget_key_updates()

        return self.__class__(merge_two_pdfs(self.read(), other.read()))

    def generate_coordinate_grid(
        self, color: Tuple[float, float, float] = (1, 0, 0), margin: float = 100
    ) -> PdfWrapper:
        stream_with_widgets = self.read()
        self._stream = copy_watermark_widgets(
            generate_coordinate_grid(
                remove_all_widgets(self.read()),
                color,
                margin,
            ),
            stream_with_widgets,
            None,
            None,
        )
        self._reregister_font()

        return self

    def fill(
        self,
        data: Dict[str, Union[str, bool, int]],
        **kwargs,
    ) -> PdfWrapper:
        for key, value in data.items():
            if key in self.widgets:
                self.widgets[key].value = value

        filled_stream, image_drawn_stream = simple_fill(
            self.read(),
            self.widgets,
            use_full_widget_name=getattr(self, "use_full_widget_name"),
            flatten=kwargs.get("flatten", False),
            adobe_mode=kwargs.get("adobe_mode", False),
        )

        if image_drawn_stream is not None:
            keys_to_copy = [
                k for k, v in self.widgets.items() if not isinstance(v, Signature)
            ]
            filled_stream = copy_watermark_widgets(
                remove_all_widgets(image_drawn_stream),
                filled_stream,
                keys_to_copy,
                None,
            )
        self._stream = filled_stream
        if image_drawn_stream is not None:
            self._reregister_font()

        return self

    def create_widget(
        self,
        widget_type: str,
        name: str,
        page_number: int,
        x: Union[float, List[float]],
        y: Union[float, List[float]],
        **kwargs,
    ) -> PdfWrapper:
        _class = None
        if widget_type == "text":
            _class = TextWidget
        if widget_type == "checkbox":
            _class = CheckBoxWidget
        if widget_type == "dropdown":
            _class = DropdownWidget
        if widget_type == "radio":
            _class = RadioWidget
        if widget_type == "signature":
            _class = SignatureWidget
        if widget_type == "image":
            _class = ImageWidget
        if _class is None:
            return self

        obj = _class(name=name, page_number=page_number, x=x, y=y, **kwargs)
        watermarks = obj.watermarks(self.read())

        self._stream = copy_watermark_widgets(self.read(), watermarks, [name], None)
        hook_params = obj.hook_params

        key_to_refresh = ""
        if widget_type in ("text", "dropdown"):
            key_to_refresh = name

        self._init_helper(key_to_refresh)
        for k, v in hook_params:
            self.widgets[name].__setattr__(k, v)

        return self

    def update_widget_key(
        self, old_key: str, new_key: str, index: int = 0, defer: bool = False
    ) -> PdfWrapper:
        if getattr(self, "use_full_widget_name"):
            raise NotImplementedError

        if defer:
            self._keys_to_update.append((old_key, new_key, index))
            return self

        self._stream = update_widget_keys(
            self.read(), self.widgets, [old_key], [new_key], [index]
        )
        self._init_helper()

        return self

    def commit_widget_key_updates(self) -> PdfWrapper:
        if getattr(self, "use_full_widget_name"):
            raise NotImplementedError

        old_keys = [each[0] for each in self._keys_to_update]
        new_keys = [each[1] for each in self._keys_to_update]
        indices = [each[2] for each in self._keys_to_update]

        self._stream = update_widget_keys(
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
        new_widget = Text("new")
        new_widget.value = text
        new_widget.font = kwargs.get("font", DEFAULT_FONT)
        new_widget.font_size = kwargs.get("font_size", DEFAULT_FONT_SIZE)
        new_widget.font_color = kwargs.get("font_color", DEFAULT_FONT_COLOR)

        watermarks = create_watermarks_and_draw(
            self.read(),
            page_number,
            "text",
            [
                {
                    "widget": new_widget,
                    "x": x,
                    "y": y,
                }
            ],
        )

        stream_with_widgets = self.read()
        self._stream = merge_watermarks_with_pdf(self.read(), watermarks)
        self._stream = copy_watermark_widgets(
            remove_all_widgets(self.read()), stream_with_widgets, None, None
        )
        self._reregister_font()

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
        image = fp_or_f_obj_or_stream_to_stream(image)
        image = rotate_image(image, rotation)
        watermarks = create_watermarks_and_draw(
            self.read(),
            page_number,
            "image",
            [{"stream": image, "x": x, "y": y, "width": width, "height": height}],
        )

        stream_with_widgets = self.read()
        self._stream = merge_watermarks_with_pdf(self.read(), watermarks)
        self._stream = copy_watermark_widgets(
            remove_all_widgets(self.read()), stream_with_widgets, None, None
        )
        self._reregister_font()

        return self

    @property
    def schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                key: value.schema_definition for key, value in self.widgets.items()
            },
        }

    def register_font(
        self, font_name: str, ttf_file: Union[bytes, str, BinaryIO]
    ) -> PdfWrapper:
        ttf_file = fp_or_f_obj_or_stream_to_stream(ttf_file)

        if register_font(font_name, ttf_file) if ttf_file is not None else False:
            self._stream, new_font_name = register_font_acroform(self.read(), ttf_file)
            self._available_fonts[font_name] = new_font_name
            self._font_register_events.append((font_name, ttf_file))

        return self

    def _reregister_font(self) -> PdfWrapper:
        font_register_events_len = len(self._font_register_events)
        for i in range(font_register_events_len):
            event = self._font_register_events[i]
            self.register_font(event[0], event[1])
        self._font_register_events = self._font_register_events[
            font_register_events_len:
        ]

        return self
