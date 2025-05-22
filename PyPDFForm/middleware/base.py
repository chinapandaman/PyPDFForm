# -*- coding: utf-8 -*-

from typing import Any


class Widget:
    SET_ATTR_TRIGGER_HOOK_MAP = {}

    def __init__(
        self,
        name: str,
        value: Any = None,
    ) -> None:
        super().__init__()
        self._name = name
        self._value = value
        self.desc = None
        self.border_color = None
        self.background_color = None
        self.border_width = None
        self.border_style = None
        self.dash_array = None
        self.render_widget = None
        self.hooks_to_trigger = []

    def __setattr__(self, name: str, value: Any) -> None:
        if name in self.SET_ATTR_TRIGGER_HOOK_MAP and value is not None:
            self.hooks_to_trigger.append((self.SET_ATTR_TRIGGER_HOOK_MAP[name], value))
        super().__setattr__(name, value)

    @property
    def name(self) -> str:
        return self._name

    @property
    def value(self) -> Any:
        return self._value

    @value.setter
    def value(self, value: Any) -> None:
        self._value = value

    @property
    def schema_definition(self) -> dict:
        result = {}

        if self.desc is not None:
            result["description"] = self.desc

        return result

    @property
    def sample_value(self) -> Any:
        raise NotImplementedError
