# -*- coding: utf-8 -*-

from typing import List
from io import BytesIO
from pypdf import PdfReader
from reportlab.pdfgen.canvas import Canvas

from .checkbox import CheckBoxWidget
from ..utils import stream_to_io


class RadioWidget(CheckBoxWidget):
    ACRO_FORM_FUNC = "radio"

    def watermarks(self, stream: bytes) -> List[bytes]:
        pdf = PdfReader(stream_to_io(stream))
        page_count = len(pdf.pages)
        watermark = BytesIO()

        canvas = Canvas(
            watermark,
            pagesize=(
                float(pdf.pages[self.page_number - 1].mediabox[2]),
                float(pdf.pages[self.page_number - 1].mediabox[3]),
            ),
        )

        if not isinstance(self.acro_form_params["x"], list):
            self.acro_form_params["x"] = [self.acro_form_params["x"]]
        if not isinstance(self.acro_form_params["y"], list):
            self.acro_form_params["y"] = [self.acro_form_params["y"]]

        for i, x in enumerate(self.acro_form_params["x"]):
            y = self.acro_form_params["y"][i]
            new_acro_form_params = self.acro_form_params.copy()
            new_acro_form_params["x"] = x
            new_acro_form_params["y"] = y
            new_acro_form_params["value"] = str(i)
            getattr(canvas.acroForm, self.ACRO_FORM_FUNC)(**new_acro_form_params)

        canvas.showPage()
        canvas.save()
        watermark.seek(0)

        return [
            watermark.read() if i == self.page_number - 1 else b""
            for i in range(page_count)
        ]
