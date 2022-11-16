# -*- coding: utf-8 -*-
"""Contains helpers for watermark."""

from io import BytesIO
from typing import List, Union

import pdfrw
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas

from ..middleware.element import Element as ElementMiddleware
from .utils import Utils


class Watermark:
    """Contains methods for interacting with watermark created by canvas."""

    @staticmethod
    def draw_text(
        *args: Union[
            "canvas.Canvas",
            "ElementMiddleware",
            float,
            int,
            str,
        ]
    ) -> None:
        """Draws a text on the watermark."""

        canv = args[0]
        element = args[1]
        coordinate_x = args[2]
        coordinate_y = args[3]

        text_to_draw = element.value

        if not text_to_draw:
            text_to_draw = ""

        if element.max_length is not None:
            text_to_draw = text_to_draw[: element.max_length]

        canv.setFont(element.font, element.font_size)
        canv.setFillColorRGB(
            element.font_color[0], element.font_color[1], element.font_color[2]
        )

        if len(text_to_draw) < element.text_wrap_length:
            canv.drawString(
                coordinate_x + element.text_x_offset,
                coordinate_y + element.text_y_offset,
                text_to_draw,
            )
        else:
            text_obj = canv.beginText(0, 0)

            start = 0
            end = element.text_wrap_length

            while end < len(text_to_draw):
                text_obj.textLine(text_to_draw[start:end])
                start += element.text_wrap_length
                end += element.text_wrap_length

            text_obj.textLine(text_to_draw[start:])

            canv.saveState()
            canv.translate(
                coordinate_x + element.text_x_offset,
                coordinate_y + element.text_y_offset,
            )
            canv.drawText(text_obj)
            canv.restoreState()

    @staticmethod
    def draw_image(*args: Union["canvas.Canvas", bytes, float, int]) -> None:
        """Draws an image on the watermark."""

        canv = args[0]
        image_stream = args[1]
        coordinate_x = args[2]
        coordinate_y = args[3]
        width = args[4]
        height = args[5]

        image_buff = BytesIO()
        image_buff.write(image_stream)
        image_buff.seek(0)

        canv.drawImage(
            ImageReader(image_buff),
            coordinate_x,
            coordinate_y,
            width=width,
            height=height,
        )

        image_buff.close()

    def create_watermarks_and_draw(
        self,
        pdf: bytes,
        page_number: int,
        action_type: str,
        actions: List[
            List[
                Union[
                    bytes,
                    float,
                    int,
                    "ElementMiddleware",
                    str,
                ]
            ]
        ],
    ) -> List[bytes]:
        """Creates a canvas watermark and draw some stuffs on it."""

        pdf_file = pdfrw.PdfReader(fdata=pdf)
        buff = BytesIO()

        canv = canvas.Canvas(
            buff,
            pagesize=(
                float(pdf_file.pages[page_number - 1].MediaBox[2]),
                float(pdf_file.pages[page_number - 1].MediaBox[3]),
            ),
        )

        if action_type == "image":
            for each in actions:
                self.draw_image(*([canv, *each]))
        elif action_type == "text":
            for each in actions:
                self.draw_text(*([canv, *each]))

        canv.save()
        buff.seek(0)

        watermark = buff.read()
        buff.close()

        results = []

        for i in range(len(pdf_file.pages)):
            results.append(watermark if i == page_number - 1 else b"")

        return results

    @staticmethod
    def merge_watermarks_with_pdf(
        pdf: bytes,
        watermarks: List[bytes],
    ) -> bytes:
        """Merges watermarks with PDF."""

        pdf_file = pdfrw.PdfReader(fdata=pdf)

        for i, page in enumerate(pdf_file.pages):
            if watermarks[i]:
                watermark = pdfrw.PdfReader(fdata=watermarks[i])
                if watermark.pages:
                    merger = pdfrw.PageMerge(page)
                    merger.add(watermark.pages[0]).render()

        return Utils().generate_stream(pdf_file)
