# -*- coding: utf-8 -*-
"""Provides radio button widget creation functionality for PDF forms.

This module contains the RadioWidget class which handles creation of:
- Interactive radio button fields for mutually exclusive selections
- Custom button styles and color styling
- Size adjustments
- PDF form field integration

Supports all standard PDF radio button properties and integrates with both
AcroForm and non-AcroForm PDF documents.
"""

from typing import List
from io import BytesIO
from pypdf import PdfReader
from reportlab.pdfgen.canvas import Canvas

from .checkbox import CheckBoxWidget
from ..utils import stream_to_io


class RadioWidget(CheckBoxWidget):
    """Creates and configures PDF radio button widgets.

    Supports all standard radio button properties including:
    - Mutually exclusive selection handling
    - Button style customization and color styling
    - Size adjustments
    - PDF form field integration

    Inherits from CheckBoxWidget, adding radio-specific parameters and logic.
    """

    ACRO_FORM_FUNC = "radio"

    def __init__(
        self,
        name: str,
        page_number: int,
        x: List[float],
        y: List[float],
        **kwargs,
    ) -> None:
        """Initializes a new radio button widget with options.

        Args:
            name: Field name/key for the radio group.
            page_number: Page number to place widget on (1-based).
            x: List of X coordinates for each radio button.
            y: List of Y coordinates for each radio button.
            **kwargs: Additional widget parameters including:
                width/height: Field dimensions.
                font/font_size: Text styling.
                options: List of radio button choices.
                shape: Button style (e.g., circle, check, cross, etc.).
                color: Button color and border styling.
        """

        self.USER_PARAMS.append(("shape", "shape"))
        super().__init__(name, page_number, x, y, **kwargs)

    def watermarks(self, stream: bytes) -> List[bytes]:
        """Generates watermarks containing the radio button widget for each page.

        Args:
            stream: PDF document as bytes to add radio button widget to

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

        for i, x in enumerate(self.acro_form_params["x"]):
            y = self.acro_form_params["y"][i]
            new_acro_form_params = self.acro_form_params.copy()
            new_acro_form_params["x"] = x
            new_acro_form_params["y"] = y
            new_acro_form_params["value"] = str(i)
            getattr(canvas.acroForm, self.ACRO_FORM_FUNC)(**new_acro_form_params)

        canvas.showPage()
        canvas.save()
        watermark.seek(0)

        return [
            watermark.read() if i == self.page_number - 1 else b""
            for i in range(page_count)
        ]
