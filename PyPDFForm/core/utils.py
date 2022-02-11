# -*- coding: utf-8 -*-
"""Contains utility helpers."""

from copy import deepcopy
from io import BytesIO
from math import sqrt
from typing import Dict, Union

import pdfrw

from ..middleware.constants import Text
from ..middleware.element import Element, ElementType
from .constants import Template as TemplateCoreConstants


class Utils:
    """Contains utility methods for core modules."""

    @staticmethod
    def generate_stream(pdf: "pdfrw.PdfReader") -> bytes:
        """Generates new stream for manipulated PDF form."""

        result_stream = BytesIO()

        pdfrw.PdfWriter().write(result_stream, pdf)
        result_stream.seek(0)

        result = result_stream.read()
        result_stream.close()

        return result

    @staticmethod
    def bool_to_checkboxes(
        data: Dict[str, Union[str, bool, int]]
    ) -> Dict[str, Union[str, "pdfrw.PdfName"]]:
        """Converts all boolean values in input data dictionary into PDF checkbox objects."""

        result = deepcopy(data)

        for key, value in result.items():
            if isinstance(value, bool):
                result[key] = pdfrw.PdfName.Yes if value else pdfrw.PdfName.Off

        return result

    @staticmethod
    def bool_to_checkbox(data: bool) -> "pdfrw.PdfName":
        """Converts a boolean value into a PDF checkbox object."""

        return pdfrw.PdfName.Yes if data else pdfrw.PdfName.Off

    @staticmethod
    def checkbox_radio_font_size(element: "pdfrw.PdfDict") -> Union[float, int]:
        """
        Calculates the font size it should be drawn with
        given a checkbox/radio button element.
        """

        area = abs(
            float(element[TemplateCoreConstants().annotation_rectangle_key][0])
            - float(element[TemplateCoreConstants().annotation_rectangle_key][2])
        ) * abs(
            float(element[TemplateCoreConstants().annotation_rectangle_key][1])
            - float(element[TemplateCoreConstants().annotation_rectangle_key][3])
        )

        return sqrt(area) * 72 / 96

    @staticmethod
    def checkbox_radio_to_draw(
        element: "Element", font_size: Union[float, int] = Text().global_font_size
    ) -> "Element":
        """Converts a checkbox/radio element to a drawable text element."""

        _map = {
            ElementType.radio: "\u25CF",
            ElementType.checkbox: "\u2713",
        }
        new_element = Element(
            element_name=element.name,
            element_type=ElementType.text,
            element_value="",
        )

        if _map.get(element.type):
            new_element.value = _map[element.type]
            new_element.font = "Helvetica"
            new_element.font_size = font_size
            new_element.font_color = (0, 0, 0)
            new_element.text_x_offset = 0
            new_element.text_y_offset = 0
            new_element.text_wrap_length = 100

        return new_element

    @staticmethod
    def merge_two_pdfs(pdf: bytes, other: bytes) -> bytes:
        """Merges two PDFs into one PDF."""

        writer = pdfrw.PdfWriter()

        writer.addpages(pdfrw.PdfReader(fdata=pdf).pages)
        writer.addpages(pdfrw.PdfReader(fdata=other).pages)

        result_stream = BytesIO()
        writer.write(result_stream)
        result_stream.seek(0)

        result = result_stream.read()
        result_stream.close()

        return result
