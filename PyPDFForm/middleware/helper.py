# -*- coding: utf-8 -*-

from typing import Dict, List

import pdfrw

from .constants import Template as TemplateConstants
from .element import Element, ElementType


class Template(object):
    @staticmethod
    def iterate_elements(pdf_stream: bytes) -> List["pdfrw.PdfDict"]:
        """Iterates through a PDF and returns all elements found."""

        pdf = pdfrw.PdfReader(fdata=pdf_stream)

        result = []

        for i in range(len(pdf.pages)):
            elements = pdf.pages[i][TemplateConstants().annotation_key]
            if elements:
                for element in elements:
                    if (
                        element[TemplateConstants().subtype_key]
                        == TemplateConstants().widget_subtype_key
                        and element[TemplateConstants().annotation_field_key]
                    ):
                        result.append(element)

        return result


class Elements(object):
    @staticmethod
    def build_elements(pdf_stream: bytes) -> Dict[str: "Element"]:
        """Builds an element list given a PDF form stream."""

        element_type_mapping = {
            "/Btn": ElementType.checkbox,
            "/Tx": ElementType.text,
        }
        results = {}

        for element in Template().iterate_elements(pdf_stream):
            key = element[TemplateConstants().annotation_field_key][1:-1]

            results[key] = Element(
                element_name=key,
                element_type=element_type_mapping.get(
                    str(element[TemplateConstants().element_type_key])
                ),
            )

        return results
