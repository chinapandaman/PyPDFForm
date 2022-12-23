# -*- coding: utf-8 -*-
"""Contains helpers for template middleware."""

from typing import Dict, Union

from ..core.template import Template as TemplateCore
from .element import Element, ElementType
from .exceptions.template import InvalidTemplateError


class Template:
    """Contains methods for interacting with template middlewares."""

    @staticmethod
    def validate_template(pdf_stream: Union[bytes, None]) -> None:
        """Validates if a template stream is byte type."""

        if not isinstance(pdf_stream, bytes):
            raise InvalidTemplateError

    @staticmethod
    def validate_stream(pdf_stream: bytes) -> None:
        """Validates if a template stream is indeed a PDF stream."""

        if b"%PDF" not in pdf_stream:
            raise InvalidTemplateError

    @staticmethod
    def build_elements(pdf_stream: bytes, sejda: bool = False) -> Dict[str, "Element"]:
        """Builds an element dict given a PDF form stream."""

        results = {}

        for element in TemplateCore().iterate_elements(pdf_stream, sejda):
            key = TemplateCore().get_element_key(element, sejda)

            element_type = TemplateCore().get_element_type(element, sejda)
            if element_type is not None:
                results[key] = Element(
                    element_name=key,
                    element_type=element_type,
                )

        return results

    @staticmethod
    def build_elements_v2(pdf_stream: bytes) -> Dict[str, "Element"]:
        """Builds an element dict given a PDF form stream."""

        results = {}

        for elements in TemplateCore().get_elements_by_page_v2(pdf_stream).values():
            for element in elements:
                key = TemplateCore().get_element_key_v2(element)

                element_type = TemplateCore().get_element_type_v2(element)

                if element_type is not None:
                    _element = Element(
                        element_name=key,
                        element_type=element_type,
                    )

                    if _element.type == ElementType.text:
                        _element.max_length = TemplateCore().get_text_field_max_length(
                            element
                        )
                        if (
                            _element.max_length is not None
                            and TemplateCore().is_text_field_comb(element)
                        ):
                            _element.comb = True

                        if _element.max_length is not None:
                            _element.font_size = (
                                TemplateCore().font_size_for_text_field_with_max_length(
                                    element, _element.max_length
                                )
                            )

                    if _element.type == ElementType.radio:
                        if key not in results:
                            results[key] = _element

                        results[key].number_of_options += 1
                        continue

                    results[key] = _element

        return results
