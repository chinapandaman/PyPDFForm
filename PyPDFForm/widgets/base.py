# -*- coding: utf-8 -*-
"""Contains base class for all widgets to create."""

from typing import List
from reportlab.pdfgen.canvas import Canvas
from io import BytesIO
from pypdf import PdfReader
from ..core.utils import stream_to_io


class Widget:
    """Base class for all widgets to create."""

    USER_PARAMS = []
    ACRO_FORM_FUNC = ""

    def __init__(
        self,
        name: str,
        page_number: int,
        width: float,
        height: float,
        x: float,
        y: float,
        **kwargs,
    ) -> None:
        """Sets acro form parameters."""

        self.page_number = page_number
        self.acro_form_params = {
            "name": name,
            "width": width,
            "height": height,
            "x": x,
            "y": y,
        }

        for each in self.USER_PARAMS:
            if each in kwargs:
                self.acro_form_params[each] = kwargs[each]

    def watermarks(self, stream: bytes) -> List[bytes]:
        """Returns a list of watermarks after creating the widget."""

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

        getattr(canvas.acroForm, self.ACRO_FORM_FUNC)(**self.acro_form_params)

        canvas.showPage()
        canvas.save()
        watermark.seek(0)

        result = []
        for i in range(page_count):
            result.append(watermark.read() if i == self.page_number - 1 else b"")

        return result
