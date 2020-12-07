# -*- coding: utf-8 -*-

import pdfrw
from .template import Template as TemplateCore
from .utils import Utils


class Filler(object):
    @staticmethod
    def simple_fill(template_stream: bytes, data: dict) -> bytes:
        """Fill a PDF form in simple mode."""

        template_pdf = pdfrw.PdfReader(fdata=template_stream)

        for element in TemplateCore().iterate_elements(template_pdf):
            key = TemplateCore().get_element_key(element)

            if key in data.keys():
                element.update(
                    pdfrw.PdfDict(
                        V=data[key],
                        AS=data[key],
                    )
                )

        return Utils().generate_stream(template_pdf)
