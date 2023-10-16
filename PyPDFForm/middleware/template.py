# -*- coding: utf-8 -*-
"""Contains helpers for template middleware."""

from typing import Dict

from ..core import template
from . import constants
from .dropdown import Dropdown
from .radio import Radio
from .text import Text


def set_character_x_paddings(
    pdf_stream: bytes, eles: Dict[str, constants.ELEMENT_TYPES]
) -> Dict[str, constants.ELEMENT_TYPES]:
    """Sets paddings between characters for combed text fields."""

    for elements in template.get_elements_by_page(pdf_stream).values():
        for element in elements:
            key = template.get_element_key(element)
            _element = eles[key]

            if isinstance(_element, Text) and _element.comb is True:
                _element.character_paddings = template.get_character_x_paddings(
                    element, _element
                )

    return eles


def build_elements(pdf_stream: bytes) -> Dict[str, constants.ELEMENT_TYPES]:
    """Builds an element dict given a PDF form stream."""

    results = {}

    for elements in template.get_elements_by_page(pdf_stream).values():
        for element in elements:
            key = template.get_element_key(element)

            _element = template.construct_element(element, key)

            if _element is not None:
                if isinstance(_element, Text):
                    _element.max_length = template.get_text_field_max_length(element)
                    if _element.max_length is not None and template.is_text_field_comb(
                        element
                    ):
                        _element.comb = True

                if isinstance(_element, Dropdown):
                    _element.choices = template.get_dropdown_choices(element)

                if isinstance(_element, Radio):
                    if key not in results:
                        results[key] = _element

                    results[key].number_of_options += 1
                    continue

                results[key] = _element

    return results


def dropdown_to_text(dropdown: Dropdown) -> Text:
    """Converts a dropdown element to a text element."""

    result = Text(dropdown.name)

    result.font = constants.GLOBAL_FONT

    if dropdown.value is not None:
        result.value = (
            dropdown.choices[dropdown.value]
            if dropdown.value < len(dropdown.choices)
            else ""
        )

    return result
