# -*- coding: utf-8 -*-

from io import BytesIO
from typing import List

from pypdf import PdfReader, PdfWriter
from pypdf.generic import (ArrayObject, FloatObject, NameObject,
                           TextStringObject)

from ..constants import Annots, Rect, T
from ..template import get_widget_key
from ..utils import stream_to_io
from .bedrock import BEDROCK_PDF


class SignatureWidget:
    OPTIONAL_PARAMS = [
        ("width", 160),
        ("height", 90),
    ]
    BEDROCK_WIDGET_TO_COPY = "signature"

    def __init__(
        self,
        name: str,
        page_number: int,
        x: float,
        y: float,
        **kwargs,
    ) -> None:
        super().__init__()
        self.hook_params = []

        self.page_number = page_number
        self.name = name
        self.x = x
        self.y = y
        self.optional_params = {
            each[0]: kwargs.get(each[0], each[1]) for each in self.OPTIONAL_PARAMS
        }

    def watermarks(self, stream: bytes) -> List[bytes]:
        input_pdf = PdfReader(stream_to_io(stream))
        page_count = len(input_pdf.pages)
        pdf = PdfReader(stream_to_io(BEDROCK_PDF))
        out = PdfWriter()
        out.append(pdf)

        for page in out.pages:
            for annot in page.get(Annots, []):
                key = get_widget_key(annot.get_object(), False)

                if key != self.BEDROCK_WIDGET_TO_COPY:
                    continue

                annot.get_object()[NameObject(T)] = TextStringObject(self.name)
                annot.get_object()[NameObject(Rect)] = ArrayObject(
                    [
                        FloatObject(self.x),
                        FloatObject(self.y),
                        FloatObject(self.x + self.optional_params.get("width")),
                        FloatObject(self.y + self.optional_params.get("height")),
                    ]
                )

        with BytesIO() as f:
            out.write(f)
            f.seek(0)
            return [
                f.read() if i == self.page_number - 1 else b""
                for i in range(page_count)
            ]
