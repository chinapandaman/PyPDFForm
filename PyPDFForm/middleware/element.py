# -*- coding: utf-8 -*-
"""Contains element middleware."""

from typing import Union


class Element:
    """Base class for all PDF form elements."""

    def __init__(
            self,
            element_name: str,
            element_value: Union[str, bool, int] = None,
            ) -> None:
        """Constructs basic attributes for the object."""

        self._name = element_name
        self.value = element_value

    @property
    def name(self) -> str:
        """Name of the element."""

        return self._name

    @property
    def schema_definition(self) -> dict:
        """Json schema definition of the element."""

        raise NotImplementedError
