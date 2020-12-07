# -*- coding: utf-8 -*-

import pdfrw
from .template import Template as TemplateCore
from .utils import Utils
from .constants import Filler as FillerConstants


class Filler(object):
    @staticmethod
    def simple_fill(template_stream: bytes, data: dict) -> bytes:
        """Fill a PDF form in simple mode."""

        template_pdf = pdfrw.PdfReader(fdata=template_stream)

        for element in TemplateCore().iterate_elements(template_pdf):
            key = TemplateCore().get_element_key(element)

            if key in data.keys():
                if data[key] in [
                    pdfrw.PdfName.Yes,
                    pdfrw.PdfName.Off,
                ]:
                    update_dict = {
                        FillerConstants().checkbox_field_value_key.replace(
                            "/", ""
                        ): data[key]
                    }
                else:
                    update_dict = {
                        FillerConstants().text_field_value_key.replace("/", ""): data[
                            key
                        ]
                    }

                element.update(pdfrw.PdfDict(**update_dict))

        return Utils().generate_stream(template_pdf)
