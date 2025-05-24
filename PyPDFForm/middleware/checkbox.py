# -*- coding: utf-8 -*-

from typing import Union

from .base import Widget


class Checkbox(Widget):
    SET_ATTR_TRIGGER_HOOK_MAP = {
        "size": "update_check_radio_size",
    }

    def __init__(
        self,
        name: str,
        value: bool = None,
    ) -> None:
        super().__init__(name, value)

        self.size = None

    @property
    def schema_definition(self) -> dict:
        return {"type": "boolean", **super().schema_definition}

    @property
    def sample_value(self) -> Union[bool, int]:
        return True
