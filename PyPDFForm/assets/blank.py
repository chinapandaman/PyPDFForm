# -*- coding: utf-8 -*-
"""
Module for creating and managing a blank PDF page asset.

This module provides the BlankPage class, which acts as a utility to generate
a simple, empty PDF page with customizable dimensions (width and height).
The primary use case is creating new PDF documents starting with a blank canvas
or adding blank pages to existing documents. It supports multiplication to
easily generate a PDF containing multiple identical blank pages.
"""

from __future__ import annotations

from functools import cached_property
from io import BytesIO

from reportlab.pdfgen.canvas import Canvas

from ..constants import BLANK_PAGE_DEFAULT_HEIGHT, BLANK_PAGE_DEFAULT_WIDTH
from ..utils import merge_two_pdfs


class BlankPage:
    """
    Class for creating a blank PDF page asset.

    This class manages the generation and representation of a single blank PDF page
    using reportlab. It provides a simple interface to access the page content as
    a byte stream and supports page duplication via the multiplication operator.
    """

    def __init__(
        self,
        width: float = BLANK_PAGE_DEFAULT_WIDTH,
        height: float = BLANK_PAGE_DEFAULT_HEIGHT,
    ) -> None:
        """
        Initializes a BlankPage object.

        Args:
            width (float): The width of the blank page in points. Defaults to
                           BLANK_PAGE_DEFAULT_WIDTH (612 points).
            height (float): The height of the blank page in points. Defaults to
                            BLANK_PAGE_DEFAULT_HEIGHT (792 points).
        """
        super().__init__()
        self.width = width
        self.height = height

    def __mul__(self, count: int) -> bytes:
        """
        Multiplication operator to merge multiple blank pages into one PDF.

        This allows syntax like `BlankPage() * 3` to create a 3-page PDF.
        It merges copies of the current blank page asset using `merge_two_pdfs`.

        Args:
            count (int): The number of blank pages to merge. Must be an integer >= 1.

        Returns:
            bytes: The byte stream of the resulting PDF containing `count` blank pages.
        """
        if count == 1:
            return self.read()

        result = b""

        for _ in range(count - 1):
            if not result:
                result = merge_two_pdfs(self.read(), self.read())
            else:
                result = merge_two_pdfs(result, self.read())

        return result

    def read(self) -> bytes:
        """
        Read the generated blank page PDF content.

        This is a public interface to retrieve the cached byte stream of the single
        blank PDF page created by this instance.

        Returns:
            bytes: The byte stream of the single blank PDF page.
        """
        return self._stream

    @cached_property
    def _stream(self) -> bytes:
        """
        Generates and returns the PDF byte stream of a single blank page.

        This is a cached property that uses `reportlab.pdfgen.canvas.Canvas` to create
        a minimal PDF document consisting of one blank page with the configured
        dimensions (`self.width`, `self.height`). This generation occurs only once.

        Returns:
            bytes: The byte stream of the generated blank PDF page.
        """
        result = BytesIO()

        canvas = Canvas(result, pagesize=(self.width, self.height))
        canvas.showPage()
        canvas.save()
        result.seek(0)

        return result.read()
