# -*- coding: utf-8 -*-

from copy import deepcopy
from io import BytesIO

import pdfrw


class Utils(object):
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
    def bool_to_checkboxes(data: dict) -> dict:
        """Converts all boolean values in input data dictionary into PDF checkbox objects."""

        result = deepcopy(data)

        for k, v in result.items():
            if isinstance(v, bool):
                result[k] = pdfrw.PdfName.Yes if v else pdfrw.PdfName.Off

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
