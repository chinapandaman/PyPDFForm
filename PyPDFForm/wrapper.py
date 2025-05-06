# -*- coding: utf-8 -*-
"""Provides high-level wrapper classes for working with PDF forms.

This module contains the FormWrapper and PdfWrapper classes which provide
a user-friendly interface for:
- Filling PDF form fields
- Creating and modifying PDF form widgets
- Drawing text and images on PDFs
- Merging PDF documents
- Generating coordinate grids
- Other PDF manipulation tasks

The wrappers handle low-level PDF operations while exposing simple methods
for common use cases.
"""

from __future__ import annotations

from functools import cached_property
from typing import BinaryIO, Dict, List, Tuple, Union

from .adapter import fp_or_f_obj_or_stream_to_stream
from .constants import (DEFAULT_FONT, DEFAULT_FONT_COLOR, DEFAULT_FONT_SIZE,
                        NEW_LINE_SYMBOL, VERSION_IDENTIFIER_PREFIX,
                        VERSION_IDENTIFIERS)
from .coordinate import generate_coordinate_grid
from .filler import fill, simple_fill
from .font import register_font
from .image import rotate_image
from .middleware.dropdown import Dropdown
from .middleware.text import Text
from .template import (build_widgets, dropdown_to_text,
                       set_character_x_paddings, update_text_field_attributes,
                       update_widget_keys)
from .utils import (generate_unique_suffix, get_page_streams, merge_two_pdfs,
                    preview_widget_to_draw, remove_all_widgets)
from .watermark import (copy_watermark_widgets, create_watermarks_and_draw,
                        merge_watermarks_with_pdf)
from .widgets.base import handle_non_acro_form_params
from .widgets.checkbox import CheckBoxWidget
from .widgets.dropdown import DropdownWidget
from .widgets.image import ImageWidget
from .widgets.radio import RadioWidget
from .widgets.signature import SignatureWidget
from .widgets.text import TextWidget


class FormWrapper:
    """Base class providing core PDF form filling functionality.

    This wrapper handles basic PDF form operations:
    - Accessing raw PDF data through the read() method
    - Filling existing form fields with provided values

    Note: This class does not parse or analyze form fields - it only fills values
    into fields that already exist in the template PDF.

    The FormWrapper is designed to be extended by PdfWrapper which adds
    more advanced features like form analysis and widget creation.
    """

    def __init__(
        self,
        template: Union[bytes, str, BinaryIO] = b"",
    ) -> None:
        """Initializes the base form wrapper with a PDF template.

        Args:
            template: PDF form as bytes, file path, or file object. Defaults to
                empty bytes if not provided.

        Initializes:
            - Internal PDF stream from the template
            - Basic form filling capabilities

        Note:
            This base class is designed to be extended by PdfWrapper which adds
            more advanced features. For most use cases, you'll want to use PdfWrapper.
        """

        super().__init__()
        self.stream = fp_or_f_obj_or_stream_to_stream(template)

    def read(self) -> bytes:
        """Returns the raw bytes of the PDF form data.

        This method provides access to the underlying PDF bytes after operations
        like fill() have been performed. No parsing or analysis of the PDF
        content is done - the bytes are returned as-is.

        Returns:
            bytes: The complete PDF document as a byte string
        """

        return self.stream

    def fill(
        self,
        data: Dict[str, Union[str, bool, int]],
        **kwargs,
    ) -> FormWrapper:
        """Fills form fields in the PDF with provided values.

        Takes a dictionary of field names to values and updates the corresponding
        form fields in the PDF. Only fields that exist in the template PDF will
        be filled - unknown field names are silently ignored.

        Args:
            data: Dictionary mapping field names to values (str, bool or int)
            **kwargs: Additional options:
                flatten: If True, makes form fields read-only after filling
                adobe_mode: If True, uses Adobe-compatible filling logic

        Returns:
            FormWrapper: Returns self to allow method chaining
        """

        widgets = build_widgets(self.stream, False, False) if self.stream else {}

        for key, value in data.items():
            if key in widgets:
                widgets[key].value = value

        self.stream = simple_fill(
            self.read(),
            widgets,
            flatten=kwargs.get("flatten", False),
            adobe_mode=kwargs.get("adobe_mode", False),
        )

        return self


class PdfWrapper(FormWrapper):
    """Extended PDF form wrapper with advanced features.

    Inherits from FormWrapper and adds capabilities for:
    - Creating and modifying form widgets
    - Drawing text and images
    - Merging PDF documents
    - Generating coordinate grids
    - Form schema generation
    - Font registration

    Key Features:
    - Maintains widget state and properties
    - Supports per-page operations
    - Handles PDF version management
    - Provides preview functionality
    """

    USER_PARAMS = [
        ("global_font", None),
        ("global_font_size", None),
        ("global_font_color", None),
        ("use_full_widget_name", False),
        ("render_widgets", True),
    ]

    def __init__(
        self,
        template: Union[bytes, str, BinaryIO] = b"",
        **kwargs,
    ) -> None:
        """Initializes the PDF wrapper with template and configuration.

        Args:
            template: PDF form as bytes, file path, or file object. Defaults to
                empty bytes if not provided.
            **kwargs: Optional configuration parameters including:
                global_font: Default font name for text fields
                global_font_size: Default font size
                global_font_color: Default font color as RGB tuple
                use_full_widget_name: Whether to use full widget names
                render_widgets: Whether to render widgets in the PDF

        Initializes:
            - Widgets dictionary to track form fields
            - Keys update queue for deferred operations
            - Any specified global settings from kwargs
        """

        super().__init__(template)
        self.widgets = {}
        self._keys_to_update = []

        for attr, default in self.USER_PARAMS:
            setattr(self, attr, kwargs.get(attr, default))

        self._init_helper()

    def _init_helper(self, key_to_refresh: str = None) -> None:
        """Internal method to refresh widget state after PDF stream changes.

        Called whenever the underlying PDF stream is modified to:
        - Rebuild the widgets dictionary
        - Preserve existing widget properties
        - Apply global font settings to text widgets
        - Handle special refresh cases for specific widgets

        Args:
            key_to_refresh: Optional specific widget key that needs refreshing.
                If provided, only that widget's font properties will be updated.
                If None, all text widgets will have their fonts updated.

        Note:
            This is an internal method and typically shouldn't be called directly.
            It's automatically invoked after operations that modify the PDF stream.
        """

        refresh_not_needed = {}
        new_widgets = (
            build_widgets(
                self.read(),
                getattr(self, "use_full_widget_name"),
                getattr(self, "render_widgets"),
            )
            if self.read()
            else {}
        )
        for k, v in self.widgets.items():
            if k in new_widgets:
                new_widgets[k] = v
                refresh_not_needed[k] = True
        self.widgets = new_widgets

        for key, value in self.widgets.items():
            if (key_to_refresh and key == key_to_refresh) or (
                key_to_refresh is None
                and isinstance(value, Text)
                and not refresh_not_needed.get(key)
            ):
                value.font = getattr(self, "global_font")
                value.font_size = getattr(self, "global_font_size")
                value.font_color = getattr(self, "global_font_color")

    @property
    def sample_data(self) -> dict:
        """Generates a dictionary of sample values for all form fields.

        Returns a dictionary mapping each widget/field name to an appropriate
        sample value based on its type:
        - Text fields: Field name (truncated if max_length specified)
        - Checkboxes: True
        - Dropdowns: Index of last available choice
        - Other fields: Type-specific sample values

        Returns:
            dict: Field names mapped to their sample values
        """

        return {key: value.sample_value for key, value in self.widgets.items()}

    @property
    def version(self) -> Union[str, None]:
        """Gets the PDF version number from the document header.

        The version is extracted from the PDF header which contains a version
        identifier like '%PDF-1.4'. This method returns just the version number
        portion (e.g. '1.4') if found, or None if no valid version identifier
        is present.

        Returns:
            str: The PDF version number (e.g. '1.4') if found
            None: If no valid version identifier exists in the PDF
        """

        for each in VERSION_IDENTIFIERS:
            if self.stream.startswith(each):
                return each.replace(VERSION_IDENTIFIER_PREFIX, b"").decode()

        return None

    @cached_property
    def pages(self) -> List[PdfWrapper]:
        """Returns individual page wrappers for each page in the PDF.

        Creates a separate PdfWrapper instance for each page, maintaining all
        the original wrapper's settings (fonts, rendering options etc.). This
        allows per-page operations while preserving the parent's configuration.

        The result is cached after first access for better performance with
        repeated calls.

        Returns:
            List[PdfWrapper]: List of wrapper objects, one per page
        """

        return [
            self.__class__(
                copy_watermark_widgets(each, self.stream, None, i),
                **{param: getattr(self, param) for param, _ in self.USER_PARAMS},
            )
            for i, each in enumerate(get_page_streams(remove_all_widgets(self.read())))
        ]

    def change_version(self, version: str) -> PdfWrapper:
        """Changes the PDF version identifier in the document header.

        Modifies the version header (e.g. '%PDF-1.4') to match the specified version.
        Note this only changes the version identifier, not the actual PDF features used.

        Args:
            version: Target version string (e.g. '1.4', '1.7')

        Returns:
            PdfWrapper: Returns self to allow method chaining
        """

        self.stream = self.stream.replace(
            VERSION_IDENTIFIER_PREFIX + bytes(self.version, "utf-8"),
            VERSION_IDENTIFIER_PREFIX + bytes(version, "utf-8"),
            1,
        )

        return self

    def __add__(self, other: PdfWrapper) -> PdfWrapper:
        """Merges two PDF forms together using the + operator.

        Combines the content of both PDF forms while:
        - Preserving each form's widgets and data
        - Adding unique suffixes to duplicate field names
        - Maintaining all page content and ordering

        Args:
            other: Another PdfWrapper instance to merge with

        Returns:
            PdfWrapper: New wrapper containing merged PDF
        """

        if not self.stream:
            return other

        if not other.stream:
            return self

        unique_suffix = generate_unique_suffix()
        for k in self.widgets:
            if k in other.widgets:
                other.update_widget_key(k, f"{k}-{unique_suffix}", defer=True)

        other.commit_widget_key_updates()

        return self.__class__(merge_two_pdfs(self.stream, other.stream))

    @property
    def preview(self) -> bytes:
        """Generates a preview PDF showing widget names above their locations.

        Creates a modified version of the PDF where:
        - All form widgets are removed
        - Widget names are drawn slightly above their original positions
        - Helps visualize form field locations without interactive widgets

        Returns:
            bytes: PDF bytes containing the preview annotations
        """

        return remove_all_widgets(
            fill(
                self.stream,
                {
                    key: preview_widget_to_draw(key, value, True)
                    for key, value in self.widgets.items()
                },
                getattr(self, "use_full_widget_name"),
            )
        )

    def generate_coordinate_grid(
        self, color: Tuple[float, float, float] = (1, 0, 0), margin: float = 100
    ) -> PdfWrapper:
        """Generates a coordinate grid overlay for the PDF.

        Creates a visual grid showing x,y coordinates to help with:
        - Precise widget placement
        - Measuring distances between elements
        - Debugging layout issues

        Args:
            color: RGB tuple (0-1 range) for grid line color (default: red)
            margin: Spacing between grid lines in PDF units (default: 100)

        Returns:
            PdfWrapper: Returns self to allow method chaining
        """

        self.stream = generate_coordinate_grid(
            remove_all_widgets(
                fill(
                    self.stream,
                    {
                        key: preview_widget_to_draw(key, value, False)
                        for key, value in self.widgets.items()
                    },
                    getattr(self, "use_full_widget_name"),
                )
            ),
            color,
            margin,
        )

        return self

    def fill(
        self,
        data: Dict[str, Union[str, bool, int]],
        **kwargs,
    ) -> PdfWrapper:
        """Fills form fields while preserving widget properties and positions.

        Extends FormWrapper.fill() with additional features:
        - Maintains widget properties like fonts and styles
        - Converts dropdowns to text fields while preserving choices
        - Updates text field attributes and character spacing

        Args:
            data: Dictionary mapping field names to values (str, bool or int)
            **kwargs: Currently unused, maintained for future compatibility

        Returns:
            PdfWrapper: Returns self to allow method chaining
        """

        for key, value in data.items():
            if key in self.widgets:
                self.widgets[key].value = value

        for key, value in self.widgets.items():
            if isinstance(value, Dropdown):
                self.widgets[key] = dropdown_to_text(value)

        update_text_field_attributes(self.stream, self.widgets)
        if self.read():
            self.widgets = set_character_x_paddings(self.stream, self.widgets)

        self.stream = remove_all_widgets(
            fill(self.stream, self.widgets, getattr(self, "use_full_widget_name"))
        )

        return self

    def create_widget(
        self,
        widget_type: str,
        name: str,
        page_number: int,
        x: Union[float, List[float]],
        y: Union[float, List[float]],
        **kwargs,
    ) -> PdfWrapper:
        """
        Creates a new interactive widget (form field) on the PDF.

        Supported widget types:
            - "text": Text input field
            - "checkbox": Checkbox field
            - "dropdown": Dropdown/combobox field
            - "radio": Radio button field
            - "signature": Signature field
            - "image": Image field

        Args:
            widget_type (str): Type of widget to create. Must be one of:
                "text", "checkbox", "dropdown", "radio", "signature", or "image".
            name (str): Unique name/identifier for the widget.
            page_number (int): 1-based page number to add the widget to.
            x (float or List[float]): X coordinate(s) for widget position.
            y (float or List[float]): Y coordinate(s) for widget position.
            **kwargs: Additional widget-specific parameters:
                For text fields: width, height, font, font_size, etc.
                For checkboxes: size, checked, etc.
                For dropdowns: choices, default_index, etc.
                For signature/image: width, height, etc.

        Returns:
            PdfWrapper: Returns self to allow method chaining.

        Notes:
            - If an unsupported widget_type is provided, the method returns self unchanged.
            - After widget creation, the internal widget state is refreshed.
        """

        _class = None
        if widget_type == "text":
            _class = TextWidget
        if widget_type == "checkbox":
            _class = CheckBoxWidget
        if widget_type == "dropdown":
            _class = DropdownWidget
        if widget_type == "radio":
            _class = RadioWidget
        if widget_type == "signature":
            _class = SignatureWidget
        if widget_type == "image":
            _class = ImageWidget
        if _class is None:
            return self

        obj = _class(name=name, page_number=page_number, x=x, y=y, **kwargs)
        watermarks = obj.watermarks(self.read())

        self.stream = copy_watermark_widgets(self.read(), watermarks, [name], None)
        if obj.non_acro_form_params:
            self.stream = handle_non_acro_form_params(
                self.stream, name, obj.non_acro_form_params
            )

        key_to_refresh = ""
        if widget_type in ("text", "dropdown"):
            key_to_refresh = name

        self._init_helper(key_to_refresh)

        return self

    def update_widget_key(
        self, old_key: str, new_key: str, index: int = 0, defer: bool = False
    ) -> PdfWrapper:
        """Updates the field name/key of an existing widget in the PDF form.

        Allows renaming form fields while preserving all other properties.
        Supports both immediate and deferred (batched) updates.

        Args:
            old_key: Current field name/key to be updated
            new_key: New field name/key to use
            index: Index for widgets with duplicate names (default: 0)
            defer: If True, queues the update for later batch processing

        Returns:
            PdfWrapper: Returns self to allow method chaining

        Raises:
            NotImplementedError: When use_full_widget_name is enabled
        """

        if getattr(self, "use_full_widget_name"):
            raise NotImplementedError

        if defer:
            self._keys_to_update.append((old_key, new_key, index))
            return self

        self.stream = update_widget_keys(
            self.read(), self.widgets, [old_key], [new_key], [index]
        )
        self._init_helper()

        return self

    def commit_widget_key_updates(self) -> PdfWrapper:
        """Processes all deferred widget key updates in a single batch operation.

        Applies all key updates that were queued using update_widget_key() with
        defer=True. This is more efficient than individual updates when renaming
        multiple fields.

        Returns:
            PdfWrapper: Returns self to allow method chaining

        Raises:
            NotImplementedError: When use_full_widget_name is enabled
        """

        if getattr(self, "use_full_widget_name"):
            raise NotImplementedError

        old_keys = [each[0] for each in self._keys_to_update]
        new_keys = [each[1] for each in self._keys_to_update]
        indices = [each[2] for each in self._keys_to_update]

        self.stream = update_widget_keys(
            self.read(), self.widgets, old_keys, new_keys, indices
        )
        self._init_helper()
        self._keys_to_update = []

        return self

    def draw_text(
        self,
        text: str,
        page_number: int,
        x: Union[float, int],
        y: Union[float, int],
        **kwargs,
    ) -> PdfWrapper:
        """Draws static text onto the PDF document at specified coordinates.

        Adds non-interactive text that becomes part of the PDF content rather
        than a form field. The text is drawn using a temporary Text widget and
        merged via watermark operations, preserving existing form fields.

        Supports multi-line text (using NEW_LINE_SYMBOL) and custom formatting.

        Args:
            text: The text content to draw (supports newlines with NEW_LINE_SYMBOL)
            page_number: Page number (1-based) to draw text on
            x: X coordinate for text position
            y: Y coordinate for text position
            **kwargs: Text formatting options:
                font: Font name (default: "Helvetica")
                font_size: Font size in points (default: 12)
                font_color: Font color as RGB tuple (default: (0, 0, 0))

        Returns:
            PdfWrapper: Returns self to allow method chaining
        """

        new_widget = Text("new")
        new_widget.value = text
        new_widget.font = kwargs.get("font", DEFAULT_FONT)
        new_widget.font_size = kwargs.get("font_size", DEFAULT_FONT_SIZE)
        new_widget.font_color = kwargs.get("font_color", DEFAULT_FONT_COLOR)

        if NEW_LINE_SYMBOL in text:
            new_widget.text_lines = text.split(NEW_LINE_SYMBOL)

        watermarks = create_watermarks_and_draw(
            self.stream,
            page_number,
            "text",
            [
                {
                    "widget": new_widget,
                    "x": x,
                    "y": y,
                }
            ],
        )

        stream_with_widgets = self.read()
        self.stream = merge_watermarks_with_pdf(self.stream, watermarks)
        self.stream = copy_watermark_widgets(
            remove_all_widgets(self.stream), stream_with_widgets, None, None
        )

        return self

    def draw_image(
        self,
        image: Union[bytes, str, BinaryIO],
        page_number: int,
        x: Union[float, int],
        y: Union[float, int],
        width: Union[float, int],
        height: Union[float, int],
        rotation: Union[float, int] = 0,
    ) -> PdfWrapper:
        """Draws an image onto the PDF document at specified coordinates.

        The image is merged via watermark operations, preserving existing form fields.
        Supports common formats (JPEG, PNG) from bytes, file paths, or file objects.

        Args:
            image: Image data as bytes, file path, or file object
            page_number: Page number (1-based) to draw image on
            x: X coordinate for image position (lower-left corner)
            y: Y coordinate for image position (lower-left corner)
            width: Width of the drawn image in PDF units
            height: Height of the drawn image in PDF units
            rotation: Rotation angle in degrees (default: 0)

        Returns:
            PdfWrapper: Returns self to allow method chaining
        """

        image = fp_or_f_obj_or_stream_to_stream(image)
        image = rotate_image(image, rotation)
        watermarks = create_watermarks_and_draw(
            self.stream,
            page_number,
            "image",
            [{"stream": image, "x": x, "y": y, "width": width, "height": height}],
        )

        stream_with_widgets = self.read()
        self.stream = merge_watermarks_with_pdf(self.stream, watermarks)
        self.stream = copy_watermark_widgets(
            remove_all_widgets(self.stream), stream_with_widgets, None, None
        )

        return self

    @property
    def schema(self) -> dict:
        """Generates a JSON schema describing the PDF form's fields and types.

        The schema includes:
        - Field names as property names
        - Type information (string, boolean, integer)
        - Field-specific constraints like max lengths for text fields
        - Choice indices for dropdown fields

        Note: Does not include required field indicators since the PDF form's
        validation rules are not extracted.

        Returns:
            dict: A JSON Schema dictionary following Draft 7 format
        """

        return {
            "type": "object",
            "properties": {
                key: value.schema_definition for key, value in self.widgets.items()
            },
        }

    @classmethod
    def register_font(
        cls, font_name: str, ttf_file: Union[bytes, str, BinaryIO]
    ) -> bool:
        """Class method to register a TrueType font for use in PDF form text fields.

        Registers the font globally so it can be used by all PdfWrapper instances.
        The font will be available when specified by name in text operations.

        Args:
            font_name: Name to register the font under (used when setting font)
            ttf_file: The TTF font data as bytes, file path, or file object

        Returns:
            bool: True if registration succeeded, False if failed
        """

        ttf_file = fp_or_f_obj_or_stream_to_stream(ttf_file)

        return register_font(font_name, ttf_file) if ttf_file is not None else False
