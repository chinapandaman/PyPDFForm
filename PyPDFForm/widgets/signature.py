# -*- coding: utf-8 -*-
"""
This module defines the `SignatureField` and `SignatureWidget` classes, which are
used to represent and manipulate signature form fields within PDF documents.

The `SignatureField` class is a dataclass that encapsulates the properties of a
signature field, such as its dimensions.

The `SignatureWidget` class provides specific functionality for interacting with
signature form fields in PDFs, including handling their creation, rendering, and
integration into the document.
"""

from dataclasses import dataclass
from io import BytesIO
from typing import List, Optional

from pypdf import PdfReader, PdfWriter
from pypdf.generic import (ArrayObject, FloatObject, NameObject,
                           TextStringObject)

from ..constants import Annots, Rect, T
from ..template import get_widget_key
from ..utils import stream_to_io
from .base import Field
from .bedrock import BEDROCK_PDF


@dataclass
class SignatureField(Field):
    """
    Represents a signature field in a PDF document.

    This dataclass extends the `Field` base class and defines the specific
    attributes that can be configured for a signature input field.

    Attributes:
        _field_type (str): The type of the field, fixed as "signature".
        width (Optional[float]): The width of the signature field.
        height (Optional[float]): The height of the signature field.
    """

    _field_type: str = "signature"

    width: Optional[float] = None
    height: Optional[float] = None


class SignatureWidget:
    """
    Represents a signature widget in a PDF form.

    This class is responsible for handling the creation, rendering, and
    integration of signature fields in a PDF document. It inherits from
    the base Widget class and provides specific functionality for handling
    signatures.

    Attributes:
        OPTIONAL_PARAMS (list): A list of tuples, where each tuple contains the
            parameter name and its default value.
        ALLOWED_HOOK_PARAMS (list): A list of parameter names that can be
            used as hooks to trigger dynamic modifications.
        BEDROCK_WIDGET_TO_COPY (str): The name of the bedrock widget to copy.
    """

    OPTIONAL_PARAMS = [
        ("width", 160),
        ("height", 90),
    ]
    ALLOWED_HOOK_PARAMS = ["required", "tooltip"]
    BEDROCK_WIDGET_TO_COPY = "signature"

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
        self.optional_params = {
            each[0]: kwargs.get(each[0], each[1]) for each in self.OPTIONAL_PARAMS
        }
        for each in self.ALLOWED_HOOK_PARAMS:
            if each in kwargs:
                self.hook_params.append((each, kwargs.get(each)))

    def watermarks(self, stream: bytes) -> List[bytes]:
        """
        Generates watermarks for the signature widget.

        This method takes a PDF stream as input, reads a "bedrock" PDF, and
        creates a new PDF with the signature widget added as a watermark on the
        specified page. The signature's name and rectangle are then added to the
        new PDF.

        Args:
            stream (bytes): The PDF stream.

        Returns:
            List[bytes]: A list of watermarks for the signature widget. Each
            element in the list represents a page in the PDF. If the current
            page matches the signature's page number, the corresponding element
            will contain the watermark data. Otherwise, the element will be an
            empty byte string.
        """
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
