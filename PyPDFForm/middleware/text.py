# -*- coding: utf-8 -*-

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
        self.comb = None
        self.alignment = None
        self.multiline = None

        self.max_length = None

    @property
    def value(self) -> str:
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
