# -*- coding: utf-8 -*-
"""Contains helpers for template."""

import uuid
from typing import Dict, List, Tuple, Union

import pdfrw

from ..middleware.element import ElementType
from .constants import Merge as MergeConstants
from .constants import Template as TemplateCoreConstants
from .utils import Utils


class Template:
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
    def get_elements_by_page(
        pdf: Union[bytes, "pdfrw.PdfReader"]
    ) -> Dict[int, List["pdfrw.PdfDict"]]:
        """Iterates through a PDF and returns all elements found grouped by page."""

        if isinstance(pdf, bytes):
            pdf = pdfrw.PdfReader(fdata=pdf)

        result = {}

        for i in range(len(pdf.pages)):
            elements = pdf.pages[i][TemplateCoreConstants().annotation_key]
            if elements:
                result[i + 1] = []
                for element in elements:
                    if (
                        element[TemplateCoreConstants().subtype_key]
                        == TemplateCoreConstants().widget_subtype_key
                        and element[TemplateCoreConstants().annotation_field_key]
                    ):
                        result[i + 1].append(element)

        return result

    @staticmethod
    def get_element_key(element: "pdfrw.PdfDict") -> str:
        """Returns its annotated key given a PDF form element."""

        return element[TemplateCoreConstants().annotation_field_key][1:-1]

    @staticmethod
    def get_element_type(element: "pdfrw.PdfDict") -> "ElementType":
        """Returns its annotated type given a PDF form element."""

        element_type_mapping = {
            "/Btn": "MULTIPLE",
            "/Tx": ElementType.text,
        }

        result = element_type_mapping.get(
            str(element[TemplateCoreConstants().element_type_key])
        )

        if result == "MULTIPLE":
            if element[TemplateCoreConstants().checkbox_field_value_key]:
                return ElementType.checkbox
            else:
                return ElementType.image

        return result

    @staticmethod
    def get_draw_text_coordinates(
        element: "pdfrw.PdfDict",
    ) -> Tuple[Union[float, int], Union[float, int]]:
        """Returns coordinates to draw text at given a PDF form text element."""

        return (
            float(element[TemplateCoreConstants().annotation_rectangle_key][0]),
            (
                float(element[TemplateCoreConstants().annotation_rectangle_key][1])
                + float(element[TemplateCoreConstants().annotation_rectangle_key][3])
            )
            / 2
            - 2,
        )

    @staticmethod
    def get_draw_image_coordinates(
        element: "pdfrw.PdfDict",
    ) -> Tuple[Union[float, int], Union[float, int]]:
        """Returns coordinates to draw image at given a PDF form image element."""

        return (
            float(element[TemplateCoreConstants().annotation_rectangle_key][0]),
            float(element[TemplateCoreConstants().annotation_rectangle_key][1]),
        )

    @staticmethod
    def get_draw_image_resolutions(
        element: "pdfrw.PdfDict",
    ) -> Tuple[Union[float, int], Union[float, int]]:
        """Returns width and height of the image given a PDF form image element."""

        return (
            float(element[TemplateCoreConstants().annotation_rectangle_key][2])
            - float(element[TemplateCoreConstants().annotation_rectangle_key][0]),
            float(element[TemplateCoreConstants().annotation_rectangle_key][3])
            - float(element[TemplateCoreConstants().annotation_rectangle_key][1]),
        )

    def assign_uuid(self, pdf: bytes) -> bytes:
        """Appends a separator and uuid after each element's annotated name."""

        _uuid = uuid.uuid4().hex

        pdf_file = pdfrw.PdfReader(fdata=pdf)

        for element in self.iterate_elements(pdf_file):
            base_key = self.get_element_key(element)
            existed_uuid = ""
            if MergeConstants().separator in base_key:
                base_key, existed_uuid = base_key.split(MergeConstants().separator)

            update_dict = {
                TemplateCoreConstants().annotation_field_key.replace(
                    "/", ""
                ): "{}{}{}".format(
                    base_key, MergeConstants().separator, existed_uuid or _uuid
                )
            }
            element.update(pdfrw.PdfDict(**update_dict))

        return Utils().generate_stream(pdf_file)
