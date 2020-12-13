# -*- coding: utf-8 -*-

from io import BytesIO
from typing import List, Union, Tuple

import pdfrw
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas


class Watermark(object):
    """Contains methods for interacting with watermark created by canvas."""

    @staticmethod
    def draw_text(
        *args: Union[
            "canvas.Canvas",
            str,
            float,
            int,
            Tuple[
                Union[float, int],
                Union[float, int],
                Union[float, int]
            ]
        ]
    ) -> None:
        """Draws a text on the watermark."""

        c = args[0]
        text = args[1]
        x = args[2]
        y = args[3]

        font = args[4]
        font_size = args[5]
        font_color = args[6]
        text_x_offset = args[7]
        text_y_offset = args[8]
        text_wrap_length = args[9]

        c.setFont(font, font_size)
        c.setFillColorRGB(
            font_color[0],
            font_color[1],
            font_color[2]
        )

        if len(text) < text_wrap_length:
            c.drawString(
                x + text_x_offset,
                y + text_y_offset,
                text
            )
        else:
            text_obj = c.beginText(0, 0)

            start = 0
            end = text_wrap_length

            while end < len(text):
                text_obj.textLine(
                    text[start:end]
                )
                start += text_wrap_length
                end += text_wrap_length

            text_obj.textLine(text[start:])

            c.saveState()
            c.translate(
                x + text_x_offset,
                y + text_y_offset
            )
            c.drawText(text_obj)
            c.restoreState()

    @staticmethod
    def draw_image(*args: Union["canvas.Canvas", bytes, float, int]) -> None:
        """Draws an image on the watermark."""

        c = args[0]
        image_stream = args[1]
        x = args[2]
        y = args[3]
        width = args[4]
        height = args[5]

        image_buff = BytesIO()
        image_buff.write(image_stream)
        image_buff.seek(0)

        c.drawImage(ImageReader(image_buff), x, y, width=width, height=height)

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
                    str,
                    Tuple[
                        Union[float, int],
                        Union[float, int],
                        Union[float, int]
                    ]
                ]
            ]
        ],
    ) -> List[bytes]:
        """Creates a canvas watermark and draw some stuffs on it."""

        pdf_file = pdfrw.PdfReader(fdata=pdf)
        buff = BytesIO()

        c = canvas.Canvas(
            buff,
            pagesize=(
                float(pdf_file.pages[page_number - 1].MediaBox[2]),
                float(pdf_file.pages[page_number - 1].MediaBox[3]),
            ),
        )

        if action_type == "image":
            for each in actions:
                self.draw_image(*([c, *each]))
        elif action_type == "text":
            for each in actions:
                self.draw_text(*([c, *each]))

        c.save()
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

        for i in range(len(pdf_file.pages)):
            if watermarks[i]:
                merger = pdfrw.PageMerge(pdf_file.pages[i])
                merger.add(pdfrw.PdfReader(fdata=watermarks[i]).pages[0]).render()

        result = BytesIO()
        writer = pdfrw.PdfFileWriter()
        writer.write(result, pdf_file)
        result.seek(0)

        result_stream = result.read()
        result.close()

        return result_stream
