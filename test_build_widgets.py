# -*- coding: utf-8 -*-
"""
Tests for build_widgets error handling.
"""

import warnings
from unittest.mock import patch

import pytest

from PyPDFForm.constants import FT, T, Tx
from PyPDFForm.middleware.text import Text
from PyPDFForm.template import build_widgets


def test_build_widgets_handles_exception_in_get_widget_key():
    """Test that build_widgets continues processing when get_widget_key raises an exception."""
    mock_pdf_stream = b"mock_pdf"

    # Create simple dict widgets
    faulty_widget = {T: "faulty_widget", FT: Tx}
    valid_widget = {T: "valid_widget", FT: Tx}

    mock_widgets_by_page = {1: [faulty_widget, valid_widget]}

    with (
        patch("PyPDFForm.template.get_widgets_by_page") as mock_get_widgets,
        patch("PyPDFForm.template.get_widget_key") as mock_get_key,
        patch("PyPDFForm.template.construct_widget") as mock_construct,
        patch("PyPDFForm.template.extract_widget_property") as mock_extract,
    ):

        mock_get_widgets.return_value = mock_widgets_by_page

        # First widget raises an exception, second succeeds
        mock_get_key.side_effect = [KeyError("Missing required key"), "valid_widget"]

        mock_construct.return_value = Text("valid_widget")
        mock_extract.return_value = None

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")

            result = build_widgets(mock_pdf_stream, use_full_widget_name=False)

            # Check that a warning was issued for the faulty widget
            assert len(w) == 1
            assert issubclass(w[0].category, RuntimeWarning)
            assert "Failed to process widget 'faulty_widget'" in str(w[0].message)
            assert "Missing required key" in str(w[0].message)
            assert "Skipping this widget" in str(w[0].message)

            # Check that the valid widget was still processed
            assert "valid_widget" in result


def test_build_widgets_handles_exception_in_construct_widget():
    """Test that build_widgets handles exceptions when constructing widgets."""
    mock_pdf_stream = b"mock_pdf"

    faulty_widget = {T: "faulty_widget", FT: Tx}
    valid_widget = {T: "valid_widget", FT: Tx}

    mock_widgets_by_page = {1: [faulty_widget, valid_widget]}

    with (
        patch("PyPDFForm.template.get_widgets_by_page") as mock_get_widgets,
        patch("PyPDFForm.template.get_widget_key") as mock_get_key,
        patch("PyPDFForm.template.construct_widget") as mock_construct,
        patch("PyPDFForm.template.extract_widget_property") as mock_extract,
    ):

        mock_get_widgets.return_value = mock_widgets_by_page
        mock_get_key.side_effect = ["faulty_widget", "valid_widget"]

        # First call raises exception, second succeeds
        mock_construct.side_effect = [
            ValueError("Cannot construct widget"),
            Text("valid_widget"),
        ]
        mock_extract.return_value = None

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")

            result = build_widgets(mock_pdf_stream, use_full_widget_name=False)

            # Check that a warning was issued
            assert len(w) == 1
            assert issubclass(w[0].category, RuntimeWarning)
            assert "Failed to process widget 'faulty_widget'" in str(w[0].message)
            assert "Cannot construct widget" in str(w[0].message)

            # Valid widget should still be processed
            assert "valid_widget" in result


def test_build_widgets_handles_exception_in_extract_widget_property():
    """Test that build_widgets handles exceptions when extracting widget properties."""
    mock_pdf_stream = b"mock_pdf"

    faulty_widget = {T: "faulty_text_widget", FT: Tx}
    valid_widget = {T: "valid_widget", FT: Tx}

    mock_widgets_by_page = {1: [faulty_widget, valid_widget]}

    with (
        patch("PyPDFForm.template.get_widgets_by_page") as mock_get_widgets,
        patch("PyPDFForm.template.get_widget_key") as mock_get_key,
        patch("PyPDFForm.template.construct_widget") as mock_construct,
        patch("PyPDFForm.template.extract_widget_property") as mock_extract,
    ):

        mock_get_widgets.return_value = mock_widgets_by_page
        mock_get_key.side_effect = ["faulty_text_widget", "valid_widget"]

        mock_construct.side_effect = [Text("faulty_text_widget"), Text("valid_widget")]

        # Make extract_widget_property raise an exception for the first call
        mock_extract.side_effect = [
            TypeError("Cannot extract property"),
            None,  # Second call succeeds
        ]

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")

            result = build_widgets(mock_pdf_stream, use_full_widget_name=False)

            # Check that a warning was issued
            assert len(w) == 1
            assert issubclass(w[0].category, RuntimeWarning)
            assert "Failed to process widget 'faulty_text_widget'" in str(w[0].message)
            assert "Cannot extract property" in str(w[0].message)

            # Valid widget should still be processed
            assert "valid_widget" in result


def test_build_widgets_handles_widget_without_name():
    """Test that build_widgets handles widgets without a name field (unknown widget)."""
    mock_pdf_stream = b"mock_pdf"

    unnamed_widget = {FT: Tx}  # Missing T field
    valid_widget = {T: "valid_widget", FT: Tx}

    mock_widgets_by_page = {1: [unnamed_widget, valid_widget]}

    with (
        patch("PyPDFForm.template.get_widgets_by_page") as mock_get_widgets,
        patch("PyPDFForm.template.get_widget_key") as mock_get_key,
        patch("PyPDFForm.template.construct_widget") as mock_construct,
        patch("PyPDFForm.template.extract_widget_property") as mock_extract,
    ):

        mock_get_widgets.return_value = mock_widgets_by_page

        # First widget fails, second succeeds
        mock_get_key.side_effect = [
            AttributeError("'NoneType' object has no attribute 'get'"),
            "valid_widget",
        ]

        mock_construct.return_value = Text("valid_widget")
        mock_extract.return_value = None

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")

            result = build_widgets(mock_pdf_stream, use_full_widget_name=False)

            # Should issue warning with 'unknown' as the widget name since T field is missing
            assert len(w) == 1
            assert "Failed to process widget 'unknown'" in str(w[0].message)

            # Valid widget should still be processed
            assert "valid_widget" in result


def test_build_widgets_no_errors():
    """Test that build_widgets works normally when all widgets are valid."""
    mock_pdf_stream = b"mock_pdf"

    valid_widget_1 = {T: "widget_1", FT: Tx}
    valid_widget_2 = {T: "widget_2", FT: Tx}

    mock_widgets_by_page = {1: [valid_widget_1, valid_widget_2]}

    with (
        patch("PyPDFForm.template.get_widgets_by_page") as mock_get_widgets,
        patch("PyPDFForm.template.get_widget_key") as mock_get_key,
        patch("PyPDFForm.template.construct_widget") as mock_construct,
        patch("PyPDFForm.template.extract_widget_property") as mock_extract,
    ):

        mock_get_widgets.return_value = mock_widgets_by_page
        mock_get_key.side_effect = ["widget_1", "widget_2"]

        mock_construct.side_effect = [Text("widget_1"), Text("widget_2")]
        mock_extract.return_value = None

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")

            result = build_widgets(mock_pdf_stream, use_full_widget_name=False)

            # No warnings should be issued
            assert len(w) == 0

            # Both widgets should be in the result
            assert len(result) == 2
            assert "widget_1" in result
            assert "widget_2" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
