# -*- coding: utf-8 -*-
"""Contains helpers for filling a PDF form."""

from typing import Dict, Union

import pdfrw

from ..middleware.element import Element as ElementMiddleware
from ..middleware.element import ElementType
from .constants import Template as TemplateConstants
from .template import Template as TemplateCore
from .utils import Utils
from .watermark import Watermark as WatermarkCore


class Filler:
    """Contains methods for filling a PDF form with dict."""

    @staticmethod
    def fill(template_stream: bytes, elements: Dict[str, "ElementMiddleware"]) -> bytes:
        """Fills a PDF using watermarks."""

        template_pdf = pdfrw.PdfReader(fdata=template_stream)

        elements_to_fill = {}
        images_to_draw = {}
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
                elif elements[key].type == ElementType.image:
                    images_to_draw[page].append(
                        [
                            elements[key].value,
                            TemplateCore().get_draw_image_coordinates(_element)[0],
                            TemplateCore().get_draw_image_coordinates(_element)[1],
                            TemplateCore().get_draw_image_resolutions(_element)[0],
                            TemplateCore().get_draw_image_resolutions(_element)[1],
                        ]
                    )
                else:
                    elements_to_fill[page].append(
                        [
                            elements[key],
                            TemplateCore().get_draw_text_coordinates(_element)[0],
                            TemplateCore().get_draw_text_coordinates(_element)[1],
                        ]
                    )
                _element.update(pdfrw.PdfDict(**update_dict))

        for page, _elements in elements_to_fill.items():
            _watermarks = WatermarkCore().create_watermarks_and_draw(
                template_stream, page, "text", _elements
            )
            for i, watermark in enumerate(_watermarks):
                if watermark:
                    watermarks[i] = watermark

        result = WatermarkCore().merge_watermarks_with_pdf(
            Utils().generate_stream(template_pdf), watermarks
        )

        for page, images in images_to_draw.items():
            if images:
                watermarks = WatermarkCore().create_watermarks_and_draw(
                    result, page, "image", images
                )

                result = WatermarkCore().merge_watermarks_with_pdf(result, watermarks)

        return result

    @staticmethod
    def simple_fill(
        template_stream: bytes, data: Dict[str, Union[str, bool]], editable: bool
    ) -> bytes:
        """Fills a PDF form in simple mode."""

        template_pdf = pdfrw.PdfReader(fdata=template_stream)
        data = Utils().bool_to_checkboxes(data)

        images_to_draw = {}

        for page, elements in (
            TemplateCore().get_elements_by_page(template_pdf).items()
        ):
            images_to_draw[page] = []
            for element in elements:
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
                    elif isinstance(data[key], bytes):
                        images_to_draw[page].append(
                            [
                                data[key],
                                TemplateCore().get_draw_image_coordinates(element)[0],
                                TemplateCore().get_draw_image_coordinates(element)[1],
                                TemplateCore().get_draw_image_resolutions(element)[0],
                                TemplateCore().get_draw_image_resolutions(element)[1],
                            ]
                        )
                        element.update(pdfrw.PdfDict(**{
                            TemplateConstants().field_editable_key.replace("/", ""): pdfrw.PdfObject(1)
                        }))
                        continue
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

        result = Utils().generate_stream(template_pdf)

        for page, images in images_to_draw.items():
            if images:
                watermarks = WatermarkCore().create_watermarks_and_draw(
                    result, page, "image", images
                )

                result = WatermarkCore().merge_watermarks_with_pdf(result, watermarks)

        return result
