# -*- coding: utf-8 -*-
"""Contains element middleware."""

from enum import Enum
from typing import Union


class ElementType(Enum):
    """An enum to represent types of elements."""

    text = "text"
    checkbox = "checkbox"
    radio = "radio"
    dropdown = "dropdown"


class Element:
    """A class to represent an element of a PDF form."""

    def __init__(
        self,
        element_name: str,
        element_type: ElementType,
        element_value: Union[str, bool, int] = None,
    ) -> None:
        """Constructs all attributes for the Element object."""

        self._name = element_name
        self._type = element_type
        self.value = element_value

        if element_type in (ElementType.text, ElementType.dropdown):
            self.font = None
            self.font_size = None
            self.font_color = None
            self.text_x_offset = None
            self.text_y_offset = None
            self.text_wrap_length = None
            self.max_length = None
            self.comb = None
            self.character_paddings = None
            if element_type == ElementType.dropdown:
                self.choices = None

        if element_type == ElementType.radio:
            self.number_of_options = 0

    @property
    def name(self) -> str:
        """Name of the element."""

        return self._name

    @property
    def type(self) -> ElementType:
        """Type of the element."""

        return self._type

    @property
    def schema_definition(self) -> dict:
        """Json schema definition of the element."""

        mapping = {
            ElementType.text: "string",
            ElementType.checkbox: "boolean",
            ElementType.radio: "integer",
            ElementType.dropdown: "integer",
        }

        result = {"type": mapping[self._type]}
        if self._type == ElementType.text and self.max_length is not None:
            result["maxLength"] = self.max_length
        if self._type == ElementType.radio:
            result["maximum"] = self.number_of_options - 1
        if self._type == ElementType.dropdown:
            result["maximum"] = len(self.choices) - 1

        return result
