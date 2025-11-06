# -*- coding: utf-8 -*-
"""
This module defines the base classes for all form fields and widgets in PyPDFForm.

It provides a foundational structure for representing and interacting with
different types of PDF form elements, such as text fields, checkboxes,
and radio buttons.

Classes:
    - `Field`: A dataclass representing the common properties of a PDF form field.
    - `Widget`: A base class for all widget implementations, providing core
      functionality for rendering and manipulation.
"""

from __future__ import annotations

from dataclasses import dataclass
from inspect import signature
from io import BytesIO
from typing import List, Optional, Union

from pypdf import PdfReader
from reportlab.lib.colors import Color
from reportlab.pdfgen.canvas import Canvas

from ..constants import fieldFlags, required
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
        self.name = name
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
        """
        Handles the 'Required' flag for the widget's AcroForm field.

        This method inspects the default flags of the AcroForm function associated
        with the widget and modifies them based on the widget's 'required' parameter.
        If the widget is marked as required, the 'required' flag is added to the
        AcroForm field flags; otherwise, it is removed. This ensures the PDF form
        field's required status is correctly reflected.

        Args:
            canvas (Canvas): The ReportLab canvas object used for PDF operations.
        """
        default_flags = signature(
            getattr(canvas.acroForm, self.ACRO_FORM_FUNC)
        ).parameters.get(fieldFlags)
        default_flags = (
            default_flags.default.split(" ")
            if default_flags and default_flags.default
            else []
        )

        if self.acro_form_params.get(required):
            default_flags.append(required)
        else:
            if required in default_flags:
                default_flags.remove(required)

        default_flags = " ".join(list(set(default_flags)))
        self.acro_form_params[fieldFlags] = default_flags
        if required in self.acro_form_params:
            del self.acro_form_params[required]

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

    @staticmethod
    def bulk_watermarks(widgets: List[Widget], stream: bytes) -> List[bytes]:
        """
        Generates watermarks for multiple widgets in bulk.

        This static method processes a list of widgets and a PDF stream to create
        a list of watermark streams, one for each page of the PDF. Widgets are
        grouped by their page number, and all widgets for a given page are drawn
        onto a single ReportLab canvas, which is then returned as the watermark
        stream for that page. This is more efficient than generating watermarks
        for each widget individually.

        Args:
            widgets (List[Widget]): A list of Widget objects to be watermarked.
            stream (bytes): The PDF stream to be watermarked.

        Returns:
            List[bytes]: A list of watermark streams (bytes), where the index
                         corresponds to the 0-based page index of the original PDF.
                         Each element is a byte stream representing the combined
                         watermark for that page. Pages without any widgets will
                         have an empty byte string (b"").
        """
        result = []

        pdf = PdfReader(stream_to_io(stream))
        watermark = BytesIO()

        widgets_by_page = {}
        for widget in widgets:
            if widget.page_number not in widgets_by_page:
                widgets_by_page[widget.page_number] = []
            widgets_by_page[widget.page_number].append(widget)

        for i, page in enumerate(pdf.pages):
            page_num = i + 1
            if page_num not in widgets_by_page:
                result.append(b"")
                continue

            watermark.seek(0)
            watermark.flush()

            canvas = Canvas(
                watermark,
                pagesize=(
                    float(page.mediabox[2]),
                    float(page.mediabox[3]),
                ),
            )

            for widget in widgets_by_page[page_num]:
                getattr(widget, "_required_handler")(canvas)
                widget.canvas_operations(canvas)

            canvas.showPage()
            canvas.save()
            watermark.seek(0)
            result.append(watermark.read())

        return result


@dataclass
class Field:
    """
    Base dataclass for all PDF form fields.

    This class defines the common properties that all types of form fields
    (e.g., text fields, checkboxes, radio buttons) share. Specific field types
    will extend this class to add their unique attributes.

    Attributes:
        name (str): The name of the form field. This is used to identify the
            field within the PDF document.
        page_number (int): The 1-based page number on which the field is located.
        x (float): The x-coordinate of the field's position on the page.
        y (float): The y-coordinate of the field's position on the page.
        required (Optional[bool]): Indicates whether the field is required to be
            filled by the user. Defaults to None, meaning not explicitly set.
        tooltip (Optional[str]): A tooltip message that appears when the user
            hovers over the field. Defaults to None.
    """

    name: str
    page_number: int
    x: float
    y: float
    required: Optional[bool] = None
    tooltip: Optional[str] = None
