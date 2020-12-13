# -*- coding: utf-8 -*-

from typing import Union

from ..core.filler import Filler as FillerCore
from ..core.image import Image as ImageCore
from ..core.utils import Utils as UtilsCore
from ..core.watermark import Watermark as WatermarkCore
from .exceptions.input import (InvalidCoordinateError,
                               InvalidEditableParameterError,
                               InvalidFormDataError,
                               InvalidImageDimensionError, InvalidImageError,
                               InvalidImageRotationAngleError,
                               InvalidModeError, InvalidPageNumberError)
from .template import Template as TemplateMiddleware


class PyPDFForm(object):
    """A class to represent a PDF form."""

    def __init__(self, template: bytes = b"", simple_mode: bool = True) -> None:
        """Constructs all attributes for the PyPDFForm object."""

        TemplateMiddleware().validate_template(template)
        if not isinstance(simple_mode, bool):
            raise InvalidModeError

        self.stream = template
        self.simple_mode = simple_mode
        self.fill = self._simple_fill

        if not simple_mode:
            self.elements = TemplateMiddleware().build_elements(template)

            for each in self.elements.values():
                each.validate_constants()
                each.validate_value()
                each.validate_text_attributes()

    def _simple_fill(self, data: dict, editable: bool = False) -> "PyPDFForm":
        """Fills a PDF form in simple mode."""

        TemplateMiddleware().validate_stream(self.stream)

        if not isinstance(data, dict):
            raise InvalidFormDataError

        if not (isinstance(editable, bool)):
            raise InvalidEditableParameterError

        self.stream = FillerCore().simple_fill(
            self.stream, UtilsCore().bool_to_checkboxes(data), editable
        )

        return self

    def draw_image(
        self,
        image: bytes,
        page_number: int,
        x: Union[float, int],
        y: Union[float, int],
        width: Union[float, int],
        height: Union[float, int],
        rotation: Union[float, int] = 0,
    ) -> "PyPDFForm":
        """Draw an image on a PDF form."""

        if not (isinstance(rotation, float) or isinstance(rotation, int)):
            raise InvalidImageRotationAngleError

        try:
            image = ImageCore().rotate_image(image, rotation)
        except Exception:
            raise InvalidImageError

        if not isinstance(page_number, int):
            raise InvalidPageNumberError

        if not (isinstance(x, float) or isinstance(x, int)):
            raise InvalidCoordinateError

        if not (isinstance(y, float) or isinstance(y, int)):
            raise InvalidCoordinateError

        if not (isinstance(width, float) or isinstance(width, int)):
            raise InvalidImageDimensionError

        if not (isinstance(height, float) or isinstance(height, int)):
            raise InvalidImageDimensionError

        watermarks = WatermarkCore().create_watermarks_and_draw(
            self.stream, page_number, "image", [[image, x, y, width, height]]
        )

        self.stream = WatermarkCore().merge_watermarks_with_pdf(self.stream, watermarks)

        return self
