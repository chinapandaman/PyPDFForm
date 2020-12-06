# -*- coding: utf-8 -*-

from typing import List

import pdfrw

from ..middleware.constants import Template as TemplateConstants


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

    @staticmethod
    def get_element_key(element: "pdfrw.PdfDict") -> str:
        """Returns its annotated key given a PDF form element."""

        return element[TemplateConstants().annotation_field_key][1:-1]
