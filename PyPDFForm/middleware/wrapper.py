# -*- coding: utf-8 -*-
from .exceptions.input import InvalidFormDataError, InvalidModeError
from ..core.filler import Filler as FillerCore
from .template import Template as TemplateMiddleware


class PyPDFForm(object):
    """A class to represent a PDF form."""

    def __init__(self, template: bytes = b"", simple_mode: bool = True) -> None:
        """Constructs all attributes for the PyPDFForm object."""

        TemplateMiddleware().validate_stream(template)
        if not isinstance(simple_mode, bool):
            raise InvalidModeError

        self.stream = template
        self.simple_mode = simple_mode
        self.fill = self._simple_fill

        if not simple_mode:
            self.elements = TemplateMiddleware().build_elements(template)

    def _simple_fill(self, data: dict, editable: bool = False) -> "PyPDFForm":
        """Fills a PDF form in simple mode."""

        TemplateMiddleware().validate_stream(self.stream)

        if not isinstance(data, dict):
            raise InvalidFormDataError

        self.stream = FillerCore().simple_fill(self.stream, data, editable)

        return self
