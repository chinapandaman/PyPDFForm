# -*- coding: utf-8 -*-

from typing import List
from io import BytesIO

from pypdf import PdfReader, PdfWriter
from pypdf.generic import NameObject, TextStringObject, ArrayObject, FloatObject

from .bedrock import BEDROCK_PDF
from ..constants import Annots, T, Rect
from ..utils import extract_widget_property, stream_to_io
from ..patterns import WIDGET_KEY_PATTERNS


class SignatureWidget:
    BEDROCK_WIDGET_TO_COPY = "signature"

    def __init__(
        self,
        name: str,
        page_number: int,
        x: float,
        y: float,
        width: float,
        height: float,
        **kwargs,
    ) -> None:
        super().__init__()
        self.non_acro_form_params = []

        self.page_number = page_number
        self.name = name
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def watermarks(self, stream: bytes) -> List[bytes]:
        input_pdf = PdfReader(stream_to_io(stream))
        page_count = len(input_pdf.pages)
        pdf = PdfReader(stream_to_io(BEDROCK_PDF))
        out = PdfWriter()
        out.append(pdf)

        for page in out.pages:
            for annot in page.get(Annots, []):  # noqa
                key = extract_widget_property(
                    annot.get_object(), WIDGET_KEY_PATTERNS, None, str
                )

                if key != self.BEDROCK_WIDGET_TO_COPY:
                    continue

                annot.get_object()[NameObject(T)] = TextStringObject(self.name)
                annot.get_object()[NameObject(Rect)] = ArrayObject(
                    [
                        FloatObject(self.x),
                        FloatObject(self.y),
                        FloatObject(self.x + self.width),
                        FloatObject(self.y + self.height)
                    ]
                )

        with BytesIO() as f:
            out.write(f)
            f.seek(0)
            return [
                f.read() if i == self.page_number - 1 else b""
                for i in range(page_count)
            ]
