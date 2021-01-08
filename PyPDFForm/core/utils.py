# -*- coding: utf-8 -*-
"""Contains utility helpers."""

from copy import deepcopy
from io import BytesIO
from typing import Dict, Union

import pdfrw
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


class Utils:
    """Contains utility methods for core modules."""

    @staticmethod
    def register_font(font_name: str, ttf_stream: bytes) -> bool:
        """Registers a font from a ttf file stream."""

        buff = BytesIO()
        buff.write(ttf_stream)
        buff.seek(0)

        pdfmetrics.registerFont(TTFont(name=font_name, filename=buff))

        buff.close()
        return True

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
        data: Dict[str, Union[str, bool]]
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
