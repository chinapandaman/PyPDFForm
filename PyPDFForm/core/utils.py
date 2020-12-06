# -*- coding: utf-8 -*-

import pdfrw
from io import BytesIO
from copy import deepcopy


class Utils(object):
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
