# -*- coding: utf-8 -*-

import pdfrw
from typing import List

from ..middleware.element import Element as ElementMiddleware
from .constants import Template as TemplateConstants
from .template import Template as TemplateCore
from .utils import Utils
from .watermark import Watermark as WatermarkCore


class Filler(object):
    """Contains methods for filling a PDF form with dict."""

    @staticmethod
    def fill(template_stream: bytes, elements: List["ElementMiddleware"]) -> bytes:
        """Fills a PDF using watermarks."""

        template_pdf = pdfrw.PdfReader(fdata=template_stream)

        elements_to_fill = {}
        element_name_to_element_map = {
            each.name: each
            for each in elements
        }

        for page, elements in TemplateCore().get_elements_by_page(template_pdf).items():
            elements_to_fill[page] = []
            for j in reversed(range(len(elements))):
                element = elements[j]
                key = TemplateCore().get_element_key(element)
                if isinstance(element_name_to_element_map[key].value, bool):
                    element.update(pdfrw.PdfDict(**{
                        TemplateConstants().checkbox_field_value_key.replace(
                            "/", ""
                        ): Utils().bool_to_checkbox(element_name_to_element_map[key].value)
                    }))
                else:
                    elements_to_fill[page].append(
                        [
                            element_name_to_element_map[key],
                            TemplateCore().get_element_coordinates(element)[0],
                            TemplateCore().get_element_coordinates(element)[1]
                        ]
                    )
                    elements.pop(j)

        final_stream = Utils().generate_stream(template_pdf)

        for page, elements in elements_to_fill.items():
            watermarks = WatermarkCore().create_watermarks_and_draw(
                final_stream,
                page,
                "text",
                elements
            )

            final_stream = WatermarkCore().merge_watermarks_with_pdf(final_stream, watermarks)

        return final_stream

    @staticmethod
    def simple_fill(template_stream: bytes, data: dict, editable: bool) -> bytes:
        """Fills a PDF form in simple mode."""

        template_pdf = pdfrw.PdfReader(fdata=template_stream)

        for element in TemplateCore().iterate_elements(template_pdf):
            key = TemplateCore().get_element_key(element)

            if key in data.keys():
                if data[key] in [
                    pdfrw.PdfName.Yes,
                    pdfrw.PdfName.Off,
                ]:
                    update_dict = {
                        TemplateConstants().checkbox_field_value_key.replace(
                            "/", ""
                        ): data[key]
                    }
                else:
                    update_dict = {
                        TemplateConstants().text_field_value_key.replace("/", ""): data[
                            key
                        ]
                    }

                if not editable:
                    update_dict[
                        TemplateConstants().field_editable_key.replace("/", "")
                    ] = pdfrw.PdfObject(1)

                element.update(pdfrw.PdfDict(**update_dict))

        return Utils().generate_stream(template_pdf)
