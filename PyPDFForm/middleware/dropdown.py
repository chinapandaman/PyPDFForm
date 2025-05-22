# -*- coding: utf-8 -*-

from .base import Widget


class Dropdown(Widget):
    def __init__(
        self,
        name: str,
        value: int = None,
    ) -> None:
        super().__init__(name, value)

        self.choices = []
        self.desc = None

    @property
    def schema_definition(self) -> dict:
        return {
            "type": "integer",
            "maximum": len(self.choices) - 1,
            **super().schema_definition,
        }

    @property
    def sample_value(self) -> int:
        return len(self.choices) - 1
