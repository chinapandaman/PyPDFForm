# -*- coding: utf-8 -*-

from typing import Union, Tuple, List
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from io import BytesIO


class Watermark(object):
    """Contains methods for interacting with watermark created by canvas."""

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

        c.drawImage(
            ImageReader(image_buff), x, y, width=width, height=height
        )

        image_buff.close()

    def create_watermark_and_draw(
        self,
        x_dimension: Union[float, int],
        y_dimension: Union[float, int],
        action: Tuple[str, List]
    ) -> bytes:
        """Creates a canvas watermark and draw something on it."""

        buff = BytesIO()

        c = canvas.Canvas(
            buff,
            pagesize=(
                x_dimension, y_dimension
            )
        )

        if action[0] == "image":
            self.draw_image(*([c] + action[1]))

        c.save()
        buff.seek(0)

        result = buff.read()
        buff.close()

        return result