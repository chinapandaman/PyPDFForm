# -*- coding: utf-8 -*-
# pylint: disable=R0801
"""
This module defines the `SignatureField` and `SignatureWidget` classes, which are
used to represent and manipulate signature form fields within PDF documents.

The `SignatureField` class is a dataclass that encapsulates the properties of a
signature field, such as its dimensions.

The `SignatureWidget` class provides specific functionality for interacting with
signature form fields in PDFs, including handling their creation, rendering, and
integration into the document.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from io import BytesIO
from typing import Any, Callable, List, Optional, Type

from pypdf import PdfReader, PdfWriter
from pypdf.generic import (
    ArrayObject,
    DictionaryObject,
    FloatObject,
    NameObject,
    NumberObject,
    StreamObject,
    TextStringObject,
)
from reportlab.pdfgen.canvas import Canvas

from ..constants import AP, DA, FT, Annot, Annots, F, N, Rect, Sig, Subtype, T
from ..constants import Type as PdfType
from .base import Field


class SignatureWidget:
    """
    Represents a signature widget in a PDF form.

    This class is responsible for handling the creation and integration of
    signature fields in a PDF document. Unlike other widget types, it does not
    inherit from the base Widget class. Instead of using ReportLab's AcroForm
    API, it constructs signature annotations directly and places them at the
    specified coordinates.

    Attributes:
        OPTIONAL_PARAMS (list): A list of tuples, where each tuple contains the
            parameter name and its default value.
        ALLOWED_HOOK_PARAMS (list): A list of parameter names that can be
            used as hooks to trigger dynamic modifications.
    """

    OPTIONAL_PARAMS = [
        ("width", 160),
        ("height", 90),
    ]
    ALLOWED_HOOK_PARAMS = ["required", "tooltip"]

    def __init__(
        self,
        name: str,
        page_number: int,
        x: float,
        y: float,
        **kwargs,
    ) -> None:
        """
        Initializes a SignatureWidget object.

        The widget records placement information, resolves width and height with
        defaults, and captures supported hook parameters so they can be applied
        after the annotation is inserted into the target PDF.

        Args:
            name (str): The name of the signature widget.
            page_number (int): The page number of the signature widget.
            x (float): The x coordinate of the signature widget.
            y (float): The y coordinate of the signature widget.
            **kwargs: Additional keyword arguments.
        """
        super().__init__()
        self.hook_params = []

        self.page_number = page_number
        self.name = name
        self.x = x
        self.y = y
        self.optional_parameters = {
            each[0]: kwargs.get(each[0], each[1]) for each in self.OPTIONAL_PARAMS
        }
        for each in self.ALLOWED_HOOK_PARAMS:
            if each in kwargs:
                self.hook_params.append((each, kwargs.get(each)))

    @staticmethod
    def build_widget_watermarks(
        widgets: List[SignatureWidget],
        stream: bytes,
        annotation_builder: Callable[[PdfWriter, SignatureWidget], Any],
    ) -> List[bytes]:
        """
        Builds page-aligned watermark PDFs from widget annotation objects.

        Widgets are grouped by their 1-based page number. For every page that
        contains widgets, this method creates a blank, single-page PDF with the
        same dimensions as the source page, asks ``annotation_builder`` to add
        each widget's objects to that PDF's writer, and stores the returned
        annotation references in the page's `/Annots` array. Pages without
        widgets are represented by an empty byte string.

        Args:
            widgets (List[SignatureWidget]): Widgets to package into watermark PDFs.
            stream (bytes): Source PDF used to determine page count and dimensions.
            annotation_builder (Callable): Function that receives the destination
                writer and a widget, adds the annotation's dependent objects to
                the writer, and returns the annotation object or reference.

        Returns:
            List[bytes]: Page-aligned watermark streams. Each non-empty entry is
            a single-page PDF containing the annotations for that source page.
        """
        page_to_widgets = defaultdict(list)
        for widget in widgets:
            page_to_widgets[widget.page_number].append(widget)

        input_pdf = PdfReader(BytesIO(stream))
        page_count = len(input_pdf.pages)
        result = [b""] * page_count

        for page_num in range(1, page_count + 1):
            page_widgets = page_to_widgets.get(page_num, [])
            if not page_widgets:
                continue

            watermark = BytesIO()
            page = input_pdf.pages[page_num - 1]
            canvas = Canvas(
                watermark,
                pagesize=(
                    float(page.mediabox[2]),
                    float(page.mediabox[3]),
                ),
            )
            canvas.showPage()
            canvas.save()
            watermark.seek(0)

            out = PdfWriter(watermark)
            annotations = [annotation_builder(out, widget) for widget in page_widgets]
            out.pages[0][NameObject(Annots)] = ArrayObject(  # pylint: disable=E1137
                annotations
            )

            with BytesIO() as result_stream:
                out.write(result_stream)
                result_stream.seek(0)
                result[page_num - 1] = result_stream.read()

        return result

    @staticmethod
    def bulk_watermarks(widgets: List[SignatureWidget], stream: bytes) -> List[bytes]:
        """
        Constructs signature widgets in page-aligned watermark PDFs.

        Each widget is represented by a `/Sig` annotation with a transparent
        normal appearance and an explicitly disabled annotation border. The
        annotation and appearance are created in the destination writer so they
        do not retain references to an external PDF.
        ``build_widget_watermarks`` then packages the annotations by source page.

        Args:
            widgets (List[SignatureWidget]): Signature widgets to construct.
            stream (bytes): Source PDF used to determine page count and dimensions.

        Returns:
            List[bytes]: Page-aligned watermark streams containing the constructed
            signature annotations.
        """

        def build_annotation(out: PdfWriter, widget: SignatureWidget) -> Any:
            width = float(widget.optional_parameters["width"])
            height = float(widget.optional_parameters["height"])

            appearance = StreamObject()
            appearance.set_data(b"")
            appearance.update(
                {
                    NameObject(PdfType): NameObject("/XObject"),
                    NameObject(Subtype): NameObject("/Form"),
                    NameObject("/BBox"): ArrayObject(
                        [
                            FloatObject(0),
                            FloatObject(0),
                            FloatObject(width),
                            FloatObject(height),
                        ]
                    ),
                    NameObject("/Resources"): DictionaryObject(),
                }
            )
            appearance_ref = out._add_object(  # type: ignore # noqa: SLF001 # pylint: disable=W0212
                appearance.flate_encode()
            )

            annotation = DictionaryObject(
                {
                    NameObject(PdfType): NameObject(Annot),
                    NameObject(Subtype): NameObject("/Widget"),
                    NameObject(Rect): ArrayObject(
                        [
                            FloatObject(widget.x),
                            FloatObject(widget.y),
                            FloatObject(widget.x + width),
                            FloatObject(widget.y + height),
                        ]
                    ),
                    NameObject("/Border"): ArrayObject(
                        [FloatObject(0), FloatObject(0), FloatObject(0)]
                    ),
                    NameObject(AP): DictionaryObject({NameObject(N): appearance_ref}),
                    NameObject(DA): TextStringObject("/Helv 0 Tf 0 g"),
                    NameObject(F): NumberObject(4),
                    NameObject(FT): NameObject(Sig),
                    NameObject("/H"): NameObject(N),
                    NameObject(T): TextStringObject(widget.name),
                    NameObject("/Q"): NumberObject(0),
                }
            )
            return out._add_object(  # type: ignore # noqa: SLF001 # pylint: disable=W0212
                annotation
            )

        return SignatureWidget.build_widget_watermarks(
            widgets, stream, build_annotation
        )


@dataclass
class SignatureField(Field):
    """
    Represents a signature field in a PDF document.

    This dataclass extends the `Field` base class and defines the specific
    dimensions that can be configured for a signature input field.

    Attributes:
        _widget_class (Type[SignatureWidget]): The widget class associated with this field type.
        width (Optional[float]): The width of the signature field.
        height (Optional[float]): The height of the signature field.
    """

    _widget_class: Type[SignatureWidget] = SignatureWidget

    width: Optional[float] = None
    height: Optional[float] = None
