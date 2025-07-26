# -*- coding: utf-8 -*-
"""
This module defines the base class for all widgets in PyPDFForm.

It provides a common interface for interacting with different types of form fields,
such as text fields, checkboxes, and radio buttons. The Widget class handles
basic properties like name, page number, and coordinates, and provides methods
for rendering the widget on a PDF page.
"""
# TODO: In `watermarks`, `PdfReader(stream_to_io(stream))` is called, which re-parses the PDF for each widget. If multiple widgets are being processed, consider passing the `PdfReader` object directly to avoid redundant parsing.
# TODO: In `watermarks`, the list comprehension `[watermark.read() if i == self.page_number - 1 else b"" for i in range(page_count)]` creates a new `BytesIO` object and reads from it for each widget. If many widgets are created, this could be optimized by creating the `BytesIO` object once and passing it around, or by directly returning the watermark bytes and its page number.

from inspect import signature
from io import BytesIO
from typing import List, Union

from pypdf import PdfReader
from reportlab.lib.colors import Color
from reportlab.pdfgen.canvas import Canvas

from ..utils import stream_to_io


class Widget:
    """
    Base class for all widgets in PyPDFForm.

    This class provides a common interface for interacting with different types of
    form fields. It handles basic properties like name, page number, and
    coordinates, and provides methods for rendering the widget on a PDF page.

    Attributes:
        USER_PARAMS (list): List of user-defined parameters for the widget.
        COLOR_PARAMS (list): List of color-related parameters for the widget.
        ALLOWED_HOOK_PARAMS (list): List of allowed hook parameters for the widget.
        NONE_DEFAULTS (list): List of parameters that default to None.
        ACRO_FORM_FUNC (str): Name of the AcroForm function to use for rendering the widget.
    """

    USER_PARAMS = []
    COLOR_PARAMS = []
    ALLOWED_HOOK_PARAMS = []
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
        """
        Initializes a Widget object.

        This method sets up the basic properties of the widget, such as its name,
        page number, and coordinates. It also handles user-defined parameters,
        color parameters, and hook parameters.

        Args:
            name (str): Name of the widget.
            page_number (int): Page number of the widget.
            x (Union[float, List[float]]): X coordinate(s) of the widget. Can be a single float or a list of floats.
            y (Union[float, List[float]]): Y coordinate(s) of the widget. Can be a single float or a list of floats.
            **kwargs: Additional keyword arguments for customizing the widget.

        Returns:
            None
        """
        super().__init__()
        self.page_number = page_number
        self.acro_form_params = {
            "name": name,
            "x": x,
            "y": y,
        }
        self.hook_params = []

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

        for each in self.ALLOWED_HOOK_PARAMS:
            if each in kwargs:
                self.hook_params.append((each, kwargs.get(each)))

    def _required_handler(self, canvas: Canvas) -> None:
        default_flags = signature(
            getattr(canvas.acroForm, self.ACRO_FORM_FUNC)
        ).parameters.get("fieldFlags")
        if not default_flags:
            return
        default_flags = (
            (default_flags.default or "").split(" ") if default_flags.default else []
        )

        if self.acro_form_params.get("required"):
            default_flags.append("required")
        else:
            if "required" in default_flags:
                default_flags.remove("required")

        default_flags = " ".join(list(set(default_flags)))
        self.acro_form_params["fieldFlags"] = default_flags
        if "required" in self.acro_form_params:
            del self.acro_form_params["required"]

    def canvas_operations(self, canvas: Canvas) -> None:
        """
        Performs canvas operations for the widget.

        This method uses the ReportLab library to draw the widget on the PDF canvas.
        It retrieves the appropriate AcroForm function from the canvas and calls it
        with the widget's parameters.

        Args:
            canvas (Canvas): Canvas object to operate on.

        Returns:
            None
        """
        getattr(canvas.acroForm, self.ACRO_FORM_FUNC)(**self.acro_form_params)

    def watermarks(self, stream: bytes) -> List[bytes]:
        """
        Generates watermarks for the widget.

        This method takes a PDF stream as input and generates watermarks for each
        page of the PDF. The watermark is created by drawing the widget on a
        ReportLab canvas and then embedding the canvas as a watermark on the
        specified page.

        Args:
            stream (bytes): PDF stream.

        Returns:
            List[bytes]: List of watermarks for each page. Each element in the list
                         is a byte stream representing the watermark for that page.
                         If a page does not need a watermark, the corresponding
                         element will be an empty byte string.
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

        self._required_handler(canvas)
        self.canvas_operations(canvas)

        canvas.showPage()
        canvas.save()
        watermark.seek(0)

        return [
            watermark.read() if i == self.page_number - 1 else b""
            for i in range(page_count)
        ]
