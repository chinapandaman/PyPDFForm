# -*- coding: utf-8 -*-

from typing import Dict, Union

import pdfrw

from ..middleware.constants import Text as TextConstants
from ..middleware.element import Element as ElementMiddleware
from ..middleware.element import ElementType
from .constants import Template as TemplateConstants
from .template import Template as TemplateCore
from .utils import Utils
from .watermark import Watermark as WatermarkCore


class Filler(object):
    """Contains methods for filling a PDF form with dict."""

    @staticmethod
    def fill(template_stream: bytes, elements: Dict[str, "ElementMiddleware"]) -> bytes:
        """Fills a PDF using watermarks."""

        template_pdf = pdfrw.PdfReader(fdata=template_stream)

        elements_to_fill = {}
        watermarks = []

        for page, _elements in (
            TemplateCore().get_elements_by_page(template_pdf).items()
        ):
            elements_to_fill[page] = []
            watermarks.append(b"")
            for _element in _elements:
                key = TemplateCore().get_element_key(_element)

                update_dict = {
                    TemplateConstants().field_editable_key.replace(
                        "/", ""
                    ): pdfrw.PdfObject(1)
                }
                if elements[key].type == ElementType.checkbox:
                    update_dict[
                        TemplateConstants().checkbox_field_value_key.replace("/", "")
                    ] = Utils().bool_to_checkbox(elements[key].value)
                else:
                    elements_to_fill[page].append(
                        [
                            elements[key],
                            TemplateCore().get_element_coordinates(_element)[0],
                            TemplateCore().get_element_coordinates(_element)[1],
                            TextConstants().global_font,
                        ]
                    )
                _element.update(pdfrw.PdfDict(**update_dict))

        for page, elements in elements_to_fill.items():
            _watermarks = WatermarkCore().create_watermarks_and_draw(
                template_stream, page, "text", elements
            )
            for i in range(len(_watermarks)):
                if _watermarks[i]:
                    watermarks[i] = _watermarks[i]

        return WatermarkCore().merge_watermarks_with_pdf(
            Utils().generate_stream(template_pdf), watermarks
        )

    @staticmethod
    def simple_fill(template_stream: bytes, data: Dict[str, Union[str, bool]], editable: bool) -> bytes:
        """Fills a PDF form in simple mode."""

        template_pdf = pdfrw.PdfReader(fdata=template_stream)
        data = Utils().bool_to_checkboxes(data)

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
