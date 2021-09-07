# -*- coding: utf-8 -*-
"""Contains helpers for template middleware."""

from typing import Dict, Union

from ..core.template import Template as TemplateCore
from .element import Element
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

            results[key] = Element(
                element_name=key,
                element_type=TemplateCore().get_element_type(element, sejda),
            )

        return results

    @staticmethod
    def build_elements_v2(pdf_stream: bytes) -> Dict[str, "Element"]:
        """Builds an element dict given a PDF form stream."""

        results = {}

        for page, elements in TemplateCore().get_elements_by_page_v2(pdf_stream).items():
            for element in elements:
                key = TemplateCore().get_element_key_v2(element)

                results[key] = Element(
                    element_name=key,
                    element_type=TemplateCore().get_element_type_v2(element)
                )

        return results
