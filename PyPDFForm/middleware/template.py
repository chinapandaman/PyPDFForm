# -*- coding: utf-8 -*-
"""Contains helpers for template middleware."""

from typing import Dict

from ..core import template
from .element import Element, ElementType


def set_character_x_paddings(
    pdf_stream: bytes, eles: Dict[str, Element]
) -> Dict[str, Element]:
    """Sets paddings between characters for combed text fields."""

    for elements in template.get_elements_by_page_v2(pdf_stream).values():
        for element in elements:
            key = template.get_element_key_v2(element)
            _element = eles[key]

            if _element.type == ElementType.text and _element.comb is True:
                _element.character_paddings = template.get_character_x_paddings(
                    element, _element
                )

    return eles


def build_elements_v2(pdf_stream: bytes) -> Dict[str, Element]:
    """Builds an element dict given a PDF form stream."""

    results = {}

    for elements in template.get_elements_by_page_v2(pdf_stream).values():
        for element in elements:
            key = template.get_element_key_v2(element)

            element_type = template.get_element_type_v2(element)

            if element_type is not None:
                _element = Element(
                    element_name=key,
                    element_type=element_type,
                )

                if _element.type == ElementType.text:
                    _element.max_length = template.get_text_field_max_length(element)
                    if _element.max_length is not None and template.is_text_field_comb(
                        element
                    ):
                        _element.comb = True

                if _element.type == ElementType.dropdown:
                    _element.choices = template.get_dropdown_choices(element)

                if _element.type == ElementType.radio:
                    if key not in results:
                        results[key] = _element

                    results[key].number_of_options += 1
                    continue

                results[key] = _element

    return results
