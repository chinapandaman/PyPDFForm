# -*- coding: utf-8 -*-
"""
This module defines the `ImageField` and `ImageWidget` classes, which are used
to describe and construct image-import form fields.

`ImageField` inherits the signature field's sizing properties. `ImageWidget`
reuses the signature widget's placement and carrier-PDF infrastructure while
constructing a push-button annotation with an Acrobat JavaScript image-import
action.
"""

from dataclasses import dataclass
from typing import Type

from pypdf import PdfWriter
from pypdf.generic import (
    ArrayObject,
    DictionaryObject,
    FloatObject,
    IndirectObject,
    NameObject,
    NumberObject,
    TextStringObject,
)

from ..constants import (
    AP,
    BC,
    BS,
    DA,
    FT,
    IF,
    IMAGE_IMPORT_JAVASCRIPT,
    JS,
    MK,
    TP,
    A,
    Action,
    Annot,
    Btn,
    D,
    F,
    Ff,
    JavaScript,
    Matrix,
    N,
    R,
    Rect,
    S,
    Subtype,
    T,
    W,
    Widget,
)
from ..constants import Type as PdfType
from .signature import SignatureField, SignatureWidget


class ImageWidget(SignatureWidget):
    """
    Represents an image widget in a PDF form.

    The widget inherits signature-field placement, dimensions, and deferred
    hooks, but constructs a push-button annotation identified by its
    `buttonImportIcon()` JavaScript action.
    """

    @staticmethod
    def _build_annotation(out: PdfWriter, widget: SignatureWidget) -> IndirectObject:
        """
        Constructs an image-import widget annotation owned by a PDF writer.

        This method creates a border-only Form XObject, reuses it for the normal,
        rollover, and pressed appearances, and builds a push-button `/Btn` widget
        whose JavaScript action invokes `buttonImportIcon()`. It registers the
        appearance and annotation with the same writer and implements the
        annotation-builder callback used by `build_widget_watermarks`.

        Args:
            out (PdfWriter): The writer that will own the appearance stream and
                widget annotation.
            widget (SignatureWidget): The normalized image widget definition to
                convert into a PDF annotation.

        Returns:
            IndirectObject: The writer-owned indirect reference to the widget
                annotation.
        """
        width = float(widget.optional_parameters["width"])
        height = float(widget.optional_parameters["height"])
        border_color = (0.1, 0.1, 0.1)

        appearance_stream = ImageWidget._build_border_appearance(
            width, height, border_color
        )
        appearance_stream[NameObject(Matrix)] = ArrayObject(
            [
                FloatObject(1),
                FloatObject(0),
                FloatObject(0),
                FloatObject(1),
                FloatObject(0),
                FloatObject(0),
            ]
        )
        appearance = out._add_object(  # type: ignore # noqa: SLF001 # pylint: disable=W0212
            appearance_stream.flate_encode()
        )

        annotation = DictionaryObject(
            {
                NameObject(FT): NameObject(Btn),
                NameObject(Ff): NumberObject(1 << 16),
                NameObject(PdfType): NameObject(Annot),
                NameObject(Subtype): NameObject(Widget),
                NameObject(F): NumberObject(4),
                NameObject(MK): DictionaryObject(
                    {
                        NameObject(TP): NumberObject(1),
                        NameObject(IF): DictionaryObject(
                            {NameObject(S): NameObject(A)}
                        ),
                        NameObject(BC): ArrayObject(
                            FloatObject(value) for value in border_color
                        ),
                    }
                ),
                NameObject(BS): DictionaryObject(
                    {
                        NameObject(S): NameObject(S),
                        NameObject(W): NumberObject(1),
                    }
                ),
                NameObject(A): DictionaryObject(
                    {
                        NameObject(PdfType): NameObject(Action),
                        NameObject(S): NameObject(JavaScript),
                        NameObject(JS): TextStringObject(IMAGE_IMPORT_JAVASCRIPT),
                    }
                ),
                NameObject(DA): TextStringObject("/Micr 12 Tf 0 0 0 rg"),
                NameObject(Rect): ImageWidget._build_rectangle(widget, width, height),
                NameObject(AP): DictionaryObject(
                    {
                        NameObject(N): appearance,
                        NameObject(R): appearance,
                        NameObject(D): appearance,
                    }
                ),
                NameObject(T): TextStringObject(widget.name),
            }
        )
        return out._add_object(  # type: ignore # noqa: SLF001 # pylint: disable=W0212
            annotation
        )


@dataclass
class ImageField(SignatureField):
    """
    Represents an image field in a PDF document.

    This dataclass extends `SignatureField` and selects `ImageWidget` as its
    widget implementation. It inherits the optional width and height values;
    when omitted, the widget resolves them to 160 and 90 points.

    Attributes:
        _widget_class (Type[ImageWidget]): The widget class associated with this field type.
    """

    _widget_class: Type[ImageWidget] = ImageWidget
