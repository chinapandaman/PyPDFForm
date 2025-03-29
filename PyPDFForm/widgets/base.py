# -*- coding: utf-8 -*-
"""Contains base class for all widgets to create."""

from io import BytesIO
from typing import List, cast

from pypdf import PdfReader, PdfWriter
from pypdf.generic import DictionaryObject
from reportlab.lib.colors import Color
from reportlab.pdfgen.canvas import Canvas

from ..constants import Annots
from ..patterns import NON_ACRO_FORM_PARAM_TO_FUNC, WIDGET_KEY_PATTERNS
from ..utils import extract_widget_property, stream_to_io


class Widget:
    """Base class for all widgets to create."""

    USER_PARAMS = []
    COLOR_PARAMS = []
    ALLOWED_NON_ACRO_FORM_PARAMS = []
    NONE_DEFAULTS = []
    ACRO_FORM_FUNC = ""

    def __init__(
        self,
        name: str,
        page_number: int,
        x: float,
        y: float,
        **kwargs,
    ) -> None:
        """Sets acro form parameters."""

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
                    ((type(self).__name__, each), kwargs.get(each))
                )

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

        return [
            watermark.read() if i == self.page_number - 1 else b""
            for i in range(page_count)
        ]


def handle_non_acro_form_params(pdf: bytes, key: str, params: list) -> bytes:
    """Handles non acro form parameters when creating a widget."""

    pdf_file = PdfReader(stream_to_io(pdf))
    out = PdfWriter()
    out.append(pdf_file)

    for page in out.pages:
        for annot in page.get(Annots, []):  # noqa
            annot = cast(DictionaryObject, annot.get_object())
            _key = extract_widget_property(
                annot.get_object(), WIDGET_KEY_PATTERNS, None, str
            )

            if _key == key:
                for param in params:
                    if param[0] in NON_ACRO_FORM_PARAM_TO_FUNC:
                        NON_ACRO_FORM_PARAM_TO_FUNC[param[0]](annot, param[1])

    with BytesIO() as f:
        out.write(f)
        f.seek(0)
        return f.read()
