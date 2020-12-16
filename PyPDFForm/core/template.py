# -*- coding: utf-8 -*-

from typing import List, Union, Tuple, Dict

import pdfrw

from .constants import Template as TemplateCoreConstants


class Template(object):
    """Contains methods for interacting with a pdfrw parsed PDF form."""

    @staticmethod
    def iterate_elements(pdf: Union[bytes, "pdfrw.PdfReader"]) -> List["pdfrw.PdfDict"]:
        """Iterates through a PDF and returns all elements found."""

        if isinstance(pdf, bytes):
            pdf = pdfrw.PdfReader(fdata=pdf)

        result = []

        for i in range(len(pdf.pages)):
            elements = pdf.pages[i][TemplateCoreConstants().annotation_key]
            if elements:
                for element in elements:
                    if (
                        element[TemplateCoreConstants().subtype_key]
                        == TemplateCoreConstants().widget_subtype_key
                        and element[TemplateCoreConstants().annotation_field_key]
                    ):
                        result.append(element)

        return result

    @staticmethod
    def get_elements_by_page(pdf: Union[bytes, "pdfrw.PdfReader"]) -> Dict[int, List["pdfrw.PdfDict"]]:
        """Iterates through a PDF and returns all elements found grouped by page."""

        if isinstance(pdf, bytes):
            pdf = pdfrw.PdfReader(fdata=pdf)

        result = {}

        for i in range(len(pdf.pages)):
            elements = pdf.pages[i][TemplateCoreConstants().annotation_key]
            if elements:
                result[i+1] = []
                for element in elements:
                    if (
                        element[TemplateCoreConstants().subtype_key]
                        == TemplateCoreConstants().widget_subtype_key
                        and element[TemplateCoreConstants().annotation_field_key]
                    ):
                        result[i+1].append(element)

        return result

    @staticmethod
    def get_element_key(element: "pdfrw.PdfDict") -> str:
        """Returns its annotated key given a PDF form element."""

        return element[TemplateCoreConstants().annotation_field_key][1:-1]

    @staticmethod
    def get_element_type(element: "pdfrw.PdfDict") -> str:
        """Returns its annotated type given a PDF form element."""

        return str(element[TemplateCoreConstants().element_type_key])

    @staticmethod
    def get_element_coordinates(element: "pdfrw.PdfDict") -> Tuple[Union[float, int], Union[float, int]]:
        """Returns its coordinates given a PDF form element."""

        return (float(element[TemplateCoreConstants().annotation_rectangle_key][0]),
                (float(element[TemplateCoreConstants().annotation_rectangle_key][1])
                 + float(element[TemplateCoreConstants().annotation_rectangle_key][3])) / 2)
