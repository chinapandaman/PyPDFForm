# -*- coding: utf-8 -*-

from io import BytesIO
from typing import List, Union

from pypdf import PdfReader
from reportlab.lib.colors import Color
from reportlab.pdfgen.canvas import Canvas

from ..utils import stream_to_io


class Widget:
    USER_PARAMS = []
    COLOR_PARAMS = []
    ALLOWED_NON_ACRO_FORM_PARAMS = []
    NONE_DEFAULTS = []
    ACRO_FORM_FUNC = ""

    def __init__(
        self,
        name: str,
        page_number: int,
        x: Union[float, List[float]],
        y: Union[float, List[float]],
        **kwargs,
    ) -> None:
        super().__init__()
        self.page_number = page_number
        self.acro_form_params = {
            "name": name,
            "x": x,
            "y": y,
        }
        self.non_acro_form_params = []

        for each in self.USER_PARAMS:
            user_input, param = each
            if user_input in kwargs:
                value = kwargs[user_input]
                if user_input in self.COLOR_PARAMS:
                    value = Color(
                        value[0],
                        value[1],
                        value[2],
                        value[3] if len(value) == 4 else 1,
                    )
                self.acro_form_params[param] = value
            elif user_input in self.NONE_DEFAULTS:
                self.acro_form_params[param] = None

        for each in self.ALLOWED_NON_ACRO_FORM_PARAMS:
            if each in kwargs:
                self.non_acro_form_params.append(
                    (each, kwargs.get(each))
                )

    def canvas_operations(self, canvas: Canvas) -> None:
        getattr(canvas.acroForm, self.ACRO_FORM_FUNC)(**self.acro_form_params)

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

        self.canvas_operations(canvas)

        canvas.showPage()
        canvas.save()
        watermark.seek(0)

        return [
            watermark.read() if i == self.page_number - 1 else b""
            for i in range(page_count)
        ]
