# -*- coding: utf-8 -*-

from typing import Union

from .base import Widget


class Checkbox(Widget):
    SET_ATTR_TRIGGER_HOOK_MAP = {
        "size": "update_check_radio_size",
    }

    BUTTON_STYLE_MAPPING = {
        "check": "4",
        "cross": "5",
        "circle": "l",
    }

    def __init__(
        self,
        name: str,
        value: bool = None,
    ) -> None:
        super().__init__(name, value)

        self.size = None
        self._button_style = self.BUTTON_STYLE_MAPPING["check"]

    @property
    def schema_definition(self) -> dict:
        return {"type": "boolean", **super().schema_definition}

    @property
    def sample_value(self) -> Union[bool, int]:
        return True

    @property
    def button_style(self) -> Union[str, None]:
        return self._button_style

    @button_style.setter
    def button_style(self, value) -> None:
        if value in self.BUTTON_STYLE_MAPPING:
            self._button_style = self.BUTTON_STYLE_MAPPING[value]
        elif value in self.BUTTON_STYLE_MAPPING.values():
            self._button_style = value
