# -*- coding: utf-8 -*-

from typing import Union, Tuple, List
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from io import BytesIO
import pdfrw


class Watermark(object):
    """Contains methods for interacting with watermark created by canvas."""

    @staticmethod
    def draw_image(
        *args: Union[
            "canvas.Canvas",
            bytes,
            float,
            int
        ]
    ) -> None:
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

        c.drawImage(
            ImageReader(image_buff), x, y, width=width, height=height
        )

        image_buff.close()

    def create_watermarks_and_draw(
        self,
        pdf: bytes,
        page_number: int,
        action: Tuple[str, List[List]]
    ) -> List[bytes]:
        """Creates a canvas watermark and draw some stuffs on it."""

        pdf_file = pdfrw.PdfReader(fdata=pdf)
        buff = BytesIO()

        c = canvas.Canvas(
            buff,
            pagesize=(
                float(pdf_file.pages[page_number - 1].MediaBox[2]),
                float(pdf_file.pages[page_number - 1].MediaBox[3]),
            )
        )

        if action[0] == "image":
            for each in action[1]:
                self.draw_image(*([c] + each))

        c.save()
        buff.seek(0)

        watermark = buff.read()
        buff.close()

        results = []

        for i in range(len(pdf_file.pages)):
            results.append(
                watermark if i == page_number - 1 else b""
            )

        return results

    @staticmethod
    def merge_watermarks_with_pdf(
        pdf: bytes,
        watermarks: List[bytes],
    ):
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
