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

        self._name = name
        self.value = value

    @property
    def name(self) -> str:
        """Name of the widget."""

        return self._name

    @property
    def schema_definition(self) -> dict:
        """Json schema definition of the widget."""

        raise NotImplementedError

    @property
    def sample_value(self) -> Any:
        """Sample value of the widget."""

        raise NotImplementedError
