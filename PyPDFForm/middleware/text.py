# -*- coding: utf-8 -*-

from typing import Any

from .base import Widget


class Text(Widget):
    SET_ATTR_TRIGGER_HOOK_MAP = {
        "font": "update_text_field_font",
        "font_size": "update_text_field_font_size",
        "font_color": "update_text_field_font_color",
        "comb": "update_text_field_comb",
        "alignment": "update_text_field_alignment",
        "multiline": "update_text_field_multiline",
    }

    def __init__(
        self,
        name: str,
        value: str = None,
    ) -> None:
        super().__init__(name, value)

        self.font = None
        self.font_size = None
        self.font_color = None
        self.text_wrap_length = None
        self.max_length = None
        self.comb = None
        self.character_paddings = []
        self.text_lines = None
        self.text_line_x_coordinates = None
        self.preview = False
        self.alignment = None
        self.multiline = None

    @property
    def value(self) -> Any:
        if isinstance(self._value, (int, float)):
            return str(self._value)

        return self._value

    @value.setter
    def value(self, value: str) -> None:
        self._value = value

    @property
    def schema_definition(self) -> dict:
        result = {"type": "string"}

        if self.max_length is not None:
            result["maxLength"] = self.max_length

        return {**result, **super().schema_definition}

    @property
    def sample_value(self) -> str:
        return (
            self.name[: self.max_length] if self.max_length is not None else self.name
        )
