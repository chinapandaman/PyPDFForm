# -*- coding: utf-8 -*-
"""Contains widget middleware."""

from typing import Any


class Widget:
    """Base class for all PDF form widgets."""

    def __init__(
        self,
        name: str,
        value: Any = None,
    ) -> None:
        """Constructs basic attributes for the object."""

        super().__init__()
        self._name = name
        self.full_name = None
        self._value = value
        self.desc = None
        self.border_color = None
        self.background_color = None
        self.border_width = None
        self.border_style = None
        self.dash_array = None
        self.render_widget = None

    @property
    def name(self) -> str:
        """Name of the widget."""

        return self._name

    @property
    def value(self) -> Any:
        """Value to fill for the widget."""

        return self._value

    @value.setter
    def value(self, value: Any) -> None:
        """Sets value to fill for the widget."""

        self._value = value

    @property
    def schema_definition(self) -> dict:
        """Json schema definition of the widget."""

        result = {}

        if self.desc is not None:
            result["description"] = self.desc

        return result

    @property
    def sample_value(self) -> Any:
        """Sample value of the widget."""

        raise NotImplementedError
