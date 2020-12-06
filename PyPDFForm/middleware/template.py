# -*- coding: utf-8 -*-

from typing import Dict

from ..core.template import Template as TemplateCore
from .constants import Template as TemplateConstants
from .element import Element, ElementType
from .exceptions.template import InvalidTemplateError


class Template(object):
    @staticmethod
    def validate_stream(pdf_stream: bytes) -> None:
        """Validate if a template stream is indeed a PDF stream."""

        if b"%PDF" not in pdf_stream:
            raise InvalidTemplateError

    @staticmethod
    def build_elements(pdf_stream: bytes) -> Dict[str, "Element"]:
        """Builds an element list given a PDF form stream."""

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
                    str(element[TemplateConstants().element_type_key])
                ),
            )

        return results
