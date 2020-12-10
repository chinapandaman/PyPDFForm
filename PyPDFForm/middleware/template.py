# -*- coding: utf-8 -*-

from typing import Dict

from ..core.template import Template as TemplateCore
from .element import Element, ElementType
from .exceptions.template import InvalidTemplateError


class Template(object):
    """Contains methods for interacting with template middlewares."""

    @staticmethod
    def validate_stream(pdf_stream: bytes) -> None:
        """Validates if a template stream is indeed a PDF stream."""

        if pdf_stream and b"%PDF" not in pdf_stream:
            raise InvalidTemplateError

    @staticmethod
    def build_elements(pdf_stream: bytes) -> Dict[str, "Element"]:
        """Builds an element dict given a PDF form stream."""

        element_type_mapping = {
            "/Btn": ElementType.checkbox,
            "/Tx": ElementType.text,
        }
        results = {}

        for element in TemplateCore().iterate_elements(pdf_stream):
            key = TemplateCore().get_element_key(element)

            results[key] = Element(
                element_name=key,
                element_type=element_type_mapping.get(
                    TemplateCore().get_element_type(element)
                ),
            )

        return results
