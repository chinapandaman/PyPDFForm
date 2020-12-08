# -*- coding: utf-8 -*-

from ..core.filler import Filler as FillerCore
from .template import Template as TemplateMiddleware


class PyPDFForm(object):
    """A class to represent a PDF form."""

    def __init__(self, template: bytes = b"", simple_mode: bool = True) -> None:
        """Constructs all attributes for the PyPDFForm object."""

        self.stream = template
        self.simple_mode = simple_mode
        self.fill = self._simple_fill

        if not simple_mode:
            self.elements = TemplateMiddleware().build_elements(template)

    def _simple_fill(self, data: dict, editable: bool = False) -> "PyPDFForm":
        """Fills a PDF form in simple mode."""

        self.stream = FillerCore().simple_fill(self.stream, data, editable)

        return self
