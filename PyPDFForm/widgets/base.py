# -*- coding: utf-8 -*-
"""Provides base widget class and utilities for PDF form field creation.

This module contains:
- Widget base class with core form field creation functionality
- Watermark generation for form fields
- Parameter handling for both AcroForm and non-AcroForm fields
"""

from io import BytesIO
from typing import List, Union, cast

from pypdf import PdfReader, PdfWriter
from pypdf.generic import DictionaryObject
from reportlab.lib.colors import Color
from reportlab.pdfgen.canvas import Canvas

from ..constants import Annots
from ..patterns import NON_ACRO_FORM_PARAM_TO_FUNC, WIDGET_KEY_PATTERNS
from ..utils import extract_widget_property, stream_to_io


class Widget:
    """Abstract base class for all PDF form widget creators.

    Provides common functionality for:
    - Managing widget parameters
    - Generating watermarks for form fields
    - Handling both AcroForm and non-AcroForm parameters
    - PDF page integration

    Attributes:
        USER_PARAMS: List of (user_name, pdf_param) mappings
        COLOR_PARAMS: List of color parameters to convert
        ALLOWED_NON_ACRO_FORM_PARAMS: Supported non-AcroForm parameters
        NONE_DEFAULTS: Parameters that should default to None
        ACRO_FORM_FUNC: Name of AcroForm function for widget creation
    """

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
        """Initializes a new widget with position and parameters.

        Args:
            name: Field name/key for the widget
            page_number: Page number to place widget on (1-based)
            x: X coordinate(s) for widget position
            y: Y coordinate(s) for widget position
            **kwargs: Additional widget-specific parameters
        """

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
                self.acro_form_params[param] = None # noqa

        for each in self.ALLOWED_NON_ACRO_FORM_PARAMS:
            if each in kwargs:
                self.non_acro_form_params.append(
                    ((type(self).__name__, each), kwargs.get(each))
                )

    def canvas_operations(self, canvas: Canvas) -> None:
        """Draws the widget on the provided PDF canvas using AcroForm.

        Calls the appropriate AcroForm function on the canvas to create the widget
        with the parameters specified in self.acro_form_params.

        Args:
            canvas: The ReportLab Canvas object to draw the widget on.
        """

        getattr(canvas.acroForm, self.ACRO_FORM_FUNC)(**self.acro_form_params)

    def watermarks(self, stream: bytes) -> List[bytes]:
        """Generates watermarks containing the widget for each page.

        Args:
            stream: PDF document as bytes to add widget to

        Returns:
            List[bytes]: Watermark data for each page (empty for non-target pages)
        """

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


def handle_non_acro_form_params(pdf: bytes, key: str, params: list) -> bytes:
    """Processes non-AcroForm parameters for a widget.

    Args:
        pdf: PDF document as bytes to modify
        key: Field name/key of the widget to update
        params: List of (parameter_name, value) tuples to set

    Returns:
        bytes: Modified PDF with updated parameters
    """

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
