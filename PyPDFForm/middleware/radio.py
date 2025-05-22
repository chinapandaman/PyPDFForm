# -*- coding: utf-8 -*-

from .checkbox import Checkbox


class Radio(Checkbox):
    def __init__(
        self,
        name: str,
        value: int = None,
    ) -> None:
        super().__init__(name, value)

        self.size = None
        self.number_of_options = 0
        self._button_style = self.BUTTON_STYLE_MAPPING["circle"]

    @property
    def schema_definition(self) -> dict:
        return {
            "maximum": self.number_of_options - 1,
            **super().schema_definition,
            "type": "integer",
        }

    @property
    def sample_value(self) -> int:
        return self.number_of_options - 1
