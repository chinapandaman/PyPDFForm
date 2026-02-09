# -*- coding: utf-8 -*-
"""
A module for wrapping PDF form operations, providing a high-level interface
for filling, creating, and manipulating PDF forms.

This module simplifies common tasks such as:
- Filling PDF forms with data from a dictionary.
- Creating new form fields (widgets) on a PDF.
- Drawing text and images onto a PDF.
- Registering custom fonts for use in form fields.
- Merging multiple PDF forms.

The core class, `PdfWrapper`, encapsulates a PDF document and provides
methods for interacting with its form fields and content. It leverages
lower-level modules within the `PyPDFForm` library to handle the
underlying PDF manipulation.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import asdict
from functools import cached_property
from os import PathLike
from typing import (TYPE_CHECKING, BinaryIO, Dict, Optional, Sequence, TextIO,
                    Tuple, Union)

from .adapter import (fp_or_f_obj_or_f_content_to_content,
                      fp_or_f_obj_or_stream_to_stream)
from .ap import appearance_streams_handler, preserve_pdf_properties
from .constants import VERSION_IDENTIFIER_PREFIX, VERSION_IDENTIFIERS
from .coordinate import generate_coordinate_grid
from .filler import fill
from .font import (get_all_available_fonts, register_font,
                   register_font_acroform)
from .hooks import trigger_widget_hooks
from .middleware.dropdown import Dropdown
from .middleware.signature import Signature
from .middleware.text import Text
from .raw import RawTypes
from .template import (build_widgets, create_annotations, get_metadata,
                       set_metadata, update_widget_keys)
from .types import PdfArray
from .utils import (generate_unique_suffix, get_page_streams, merge_pdfs,
                    remove_all_widgets)
from .watermark import (copy_watermark_widgets, create_watermarks_and_draw,
                        merge_watermarks_with_pdf)
from .widgets import CheckBoxField, ImageField, RadioGroup, SignatureField

if TYPE_CHECKING:
    from .annotations import AnnotationTypes
    from .assets.blank import BlankPage
    from .widgets import FieldTypes


class PdfWrapper:
    """
    A class to wrap PDF form operations, providing a simplified interface
    for common tasks such as filling, creating, and manipulating PDF forms.

    The `PdfWrapper` class encapsulates a PDF document and provides methods
    for interacting with its form fields (widgets) and content. It leverages
    lower-level modules within the `PyPDFForm` library to handle the
    underlying PDF manipulation.

    Attributes:
        USER_PARAMS (list): A list of user-configurable parameters and their default values.
            These parameters can be set during initialization using keyword arguments.
            Current parameters include:
                - `use_full_widget_name` (bool): Whether to use the full widget name when filling the form.
                - `need_appearances` (bool): Whether to set the `NeedAppearances` flag in the PDF's AcroForm dictionary.
                - `generate_appearance_streams` (bool): Whether to explicitly generate appearance streams for all form fields using pikepdf.
                - `preserve_metadata` (bool): Whether to preserve the original metadata of the PDF.
                - `title` (str): The title of the PDF document.

    """

    USER_PARAMS = [
        ("use_full_widget_name", False),
        ("need_appearances", False),
        ("generate_appearance_streams", False),
        ("preserve_metadata", False),
        ("title", None),
    ]

    def __init__(
        self,
        template: Union[bytes, str, BinaryIO, BlankPage] = b"",
        **kwargs,
    ) -> None:
        """
        Constructor method for the `PdfWrapper` class.

        Initializes a new `PdfWrapper` object with the given template PDF and optional keyword arguments.

        Args:
            template (Union[bytes, str, BinaryIO, BlankPage]): The template PDF, provided as either:
                - bytes: The raw PDF data as a byte string.
                - str: The file path to the PDF.
                - BinaryIO: An open file-like object containing the PDF data.
                - BlankPage: A blank page object.
                Defaults to an empty byte string (b""), which creates a blank PDF.
            **kwargs: Additional keyword arguments to configure the `PdfWrapper`.
                These arguments are used to set the user-configurable parameters defined in `USER_PARAMS`.
                For example: `use_full_widget_name=True` or `need_appearances=False`.
        """

        super().__init__()
        self._stream = fp_or_f_obj_or_stream_to_stream(template)
        self.widgets = {}
        self.title: Optional[str] = None
        self._metadata = (
            get_metadata(self._read()) if kwargs.get("preserve_metadata") else {}
        )
        self._on_open_javascript = None
        self._available_fonts = {}  # for setting /F1
        self._font_register_events = []  # for reregister
        self._key_update_tracker = {}  # for update key preserve old key attrs
        self._keys_to_update = []  # for bulk update keys

        # sets attrs from kwargs
        for attr, default in self.USER_PARAMS:
            setattr(self, attr, kwargs.get(attr, default))

        if getattr(self, "generate_appearance_streams") is True:
            self.need_appearances = True

        self._init_helper()

    def __add__(self, other: Union[PdfWrapper, Sequence[PdfWrapper]]) -> PdfWrapper:
        """
        Merges PDF wrappers together, creating a new `PdfWrapper` containing the combined content.

        This method allows you to combine PDF forms into a single form. It handles potential
        naming conflicts between form fields by adding a unique suffix to the field names in the
        form being merged.

        Args:
            other (Union[PdfWrapper, Sequence[PdfWrapper]]): The other `PdfWrapper` object or
                a sequence of `PdfWrapper` objects to merge with.

        Returns:
            PdfWrapper: A new `PdfWrapper` object containing the merged PDFs.
        """

        if isinstance(other, Sequence):
            result = self
            for each in other:
                result += each
            return result

        if not self or not self._read():
            return other

        if not other or not other._read():
            return self

        unique_suffix = generate_unique_suffix()
        for k in self.widgets:
            if k in other.widgets:
                other.update_widget_key(k, f"{k}-{unique_suffix}", defer=True)

        other.commit_widget_key_updates()

        # user params are based on the first object
        result = self.__class__(
            merge_pdfs([self._read(), other._read()]),
            **{each[0]: getattr(self, each[0], each[1]) for each in self.USER_PARAMS},
        )

        # inherit fonts
        for event in self._font_register_events:
            result.register_font(event[0], event[1])

        return result

    def _init_helper(self) -> None:
        """
        Helper method to initialize widgets and available fonts.

        This method is called during initialization and after certain operations
        that modify the PDF content (e.g., filling, creating widgets, updating keys).
        It rebuilds the widget dictionary and updates the available fonts.
        """

        new_widgets = (
            build_widgets(
                self._read(),
                getattr(self, "use_full_widget_name"),
            )
            if self._read()
            else {}
        )
        # ensure old widgets don't get overwritten
        for k, v in self.widgets.items():
            if k in new_widgets:
                new_widgets[k] = v

        # update key preserve old key attrs
        for k, v in new_widgets.items():
            if k in self._key_update_tracker:
                for name, value in self.widgets[
                    self._key_update_tracker[k]
                ].__dict__.items():
                    if not name.startswith("_"):
                        setattr(v, name, value)
        self._key_update_tracker = {}

        self.widgets = new_widgets

        if self._read():
            self._available_fonts.update(**get_all_available_fonts(self._read()))

    def _reregister_font(self) -> PdfWrapper:
        """
        Reregisters fonts after PDF content modifications.

        This method is called after operations that modify the PDF content
        (e.g., drawing text, drawing images) to ensure that custom fonts
        are correctly registered and available for use.
        """

        font_register_events_len = len(self._font_register_events)
        for i in range(font_register_events_len):
            event = self._font_register_events[i]
            self.register_font(event[0], event[1])
        self._font_register_events = self._font_register_events[
            font_register_events_len:
        ]

        return self

    @property
    def schema(self) -> dict:
        """
        Returns the JSON schema of the PDF form, describing the structure and data types of the form fields.

        This schema can be used to generate user interfaces or validate data before filling the form.

        Returns:
            dict: A dictionary representing the JSON schema of the PDF form.
        """

        return {
            "type": "object",
            "properties": {
                key: value.schema_definition for key, value in self.widgets.items()
            },
        }

    @property
    def data(self) -> dict:
        """
        Returns a dictionary of the current data in the PDF form fields.

        The keys of the dictionary are the form field names, and the values are
        the current values of those fields. This property provides a convenient
        way to extract all filled data from the PDF.

        Returns:
            dict: A dictionary where keys are form field names (str) and values are
                  their corresponding data (Union[str, bool, int, None]).
        """

        return {key: value.value for key, value in self.widgets.items()}

    @property
    def sample_data(self) -> dict:
        """
        Returns sample data for the PDF form, providing example values for each form field.

        This sample data can be used for testing or demonstration purposes.

        Returns:
            dict: A dictionary containing sample data for the PDF form.
        """

        return {key: value.sample_value for key, value in self.widgets.items()}

    @property
    def version(self) -> Union[str, None]:
        """
        Returns the PDF version of the underlying PDF document.

        Returns:
            Union[str, None]: The PDF version as a string, or None if the version cannot be determined.
        """

        for each in VERSION_IDENTIFIERS:
            if self._read().startswith(each):
                return each.replace(VERSION_IDENTIFIER_PREFIX, b"").decode()

        return None

    @property
    def fonts(self) -> list:
        """
        Returns a list of the names of the currently registered fonts.

        Returns:
            list: A list of font names (str).
        """

        return list(self._available_fonts.keys())

    @cached_property
    def pages(self) -> Sequence[PdfWrapper]:
        """
        Returns a list of `PdfWrapper` objects, each representing a single page in the PDF document.

        This allows you to work with individual pages of the PDF, for example, to extract text or images from a specific page.

        Returns:
            Sequence[PdfWrapper]: A list of `PdfWrapper` objects, one for each page in the PDF.
        """

        result = [
            self.__class__(
                # Case: Single watermark PDF, extracting a specific page to the first output page.
                copy_watermark_widgets(each, self._read(), None, i),
                **{param: getattr(self, param) for param, _ in self.USER_PARAMS},
            )
            for i, each in enumerate(get_page_streams(remove_all_widgets(self._read())))
        ]

        # because copy_watermark_widgets and remove_all_widgets
        if self._font_register_events:
            for event in self._font_register_events:
                for page in result:
                    page.register_font(event[0], event[1])

        return PdfArray(result)

    @property
    def on_open_javascript(self) -> Union[str, None]:
        """
        Returns the JavaScript script that executes when the PDF is opened.

        Returns:
            Union[str, None]: The JavaScript script, or None if no script is set.
        """

        return self._on_open_javascript

    @on_open_javascript.setter
    def on_open_javascript(self, value: Union[str, TextIO]) -> None:
        """
        Sets the JavaScript script that executes when the PDF is opened.

        Args:
            value (Union[str, TextIO]): The JavaScript script, provided as either:
                - str: The JavaScript code as a string, or a file path to a .js file.
                - TextIO: An open file-like object containing the JavaScript code.
        """

        self._on_open_javascript = fp_or_f_obj_or_f_content_to_content(value)

    def read(self) -> bytes:
        """
        Reads the PDF document and returns its content as bytes.

        This method retrieves the PDF stream and performs several processing steps:
        1. Triggers widget hooks and updates font mappings (via `_read`).
        2. If `need_appearances` is enabled, it handles appearance streams and the
           `/NeedAppearances` flag, which may include removing XFA and explicitly
           generating appearance streams.
        3. If `preserve_metadata` is enabled, it preserves the original metadata of the PDF.
        4. If a title or on-open JavaScript is set, it updates the PDF properties
           accordingly.

        Returns:
            bytes: The processed PDF document content as a byte string.
        """

        result = self._read()
        if getattr(self, "need_appearances") and result:
            result = appearance_streams_handler(
                result, getattr(self, "generate_appearance_streams")
            )  # cached

        if getattr(self, "preserve_metadata"):
            # TODO: refactor with preserve_pdf_properties
            result = set_metadata(result, self._metadata)

        if any([self.title, self.on_open_javascript]):
            result = preserve_pdf_properties(
                result,
                self.title,
                self.on_open_javascript,
            )

        return result

    def _read(self) -> bytes:
        """
        Reads the PDF stream, triggering widget hooks and updating fonts if necessary.

        This internal method ensures that all widget hooks are executed and that
        fonts are correctly mapped to their internal PDF names before returning
        the raw PDF stream.

        Returns:
            bytes: The raw PDF stream.
        """

        if any(widget.hooks_to_trigger for widget in self.widgets.values()):
            for widget in self.widgets.values():
                if (
                    isinstance(widget, (Text, Dropdown))
                    and widget.font not in self._available_fonts.values()
                    and widget.font in self._available_fonts
                ):
                    widget.font = self._available_fonts.get(
                        widget.font
                    )  # from `new_font` to `/F1`

            self._stream = trigger_widget_hooks(
                self._stream,
                self.widgets,
                getattr(self, "use_full_widget_name"),
            )

        return self._stream

    def write(self, dest: Union[str, BinaryIO]) -> PdfWrapper:
        """
        Writes the PDF to a file.

        Args:
            dest (Union[str, BinaryIO]): The destination to write the PDF to.
                Can be a file path (str) or a file-like object (BinaryIO).

        Returns:
            PdfWrapper: The `PdfWrapper` object, allowing for method chaining.
        """

        if isinstance(dest, (str, bytes, PathLike)):
            with open(dest, "wb+") as f:
                f.write(self.read())
        else:
            dest.write(self.read())

        return self

    def change_version(self, version: str) -> PdfWrapper:
        """
        Changes the PDF version of the underlying document.

        Args:
            version (str): The new PDF version string (e.g., "1.7").

        Returns:
            PdfWrapper: The `PdfWrapper` object, allowing for method chaining.
        """

        self._stream = self._read().replace(
            VERSION_IDENTIFIER_PREFIX + bytes(self.version, "utf-8"),
            VERSION_IDENTIFIER_PREFIX + bytes(version, "utf-8"),
            1,
        )

        return self

    def generate_coordinate_grid(
        self, color: Tuple[float, float, float] = (1, 0, 0), margin: float = 100
    ) -> PdfWrapper:
        """
        Generates a coordinate grid on the PDF, useful for debugging layout issues.

        Args:
            color (Tuple[float, float, float]): The color of the grid lines, specified as an RGB tuple (default: red).
            margin (float): The margin around the grid, in points (default: 100).

        Returns:
            PdfWrapper: The `PdfWrapper` object, allowing for method chaining.
        """

        stream_with_widgets = self._read()
        # Case: Single watermark PDF, mapping pages 1:1 to output pages.
        self._stream = copy_watermark_widgets(
            generate_coordinate_grid(
                remove_all_widgets(self._read()),
                color,
                margin,
            ),
            stream_with_widgets,
            None,
            None,
        )
        # because copy_watermark_widgets and remove_all_widgets
        self._reregister_font()

        return self

    def fill(
        self,
        data: Dict[str, Union[str, bool, int, BinaryIO, bytes]],
        **kwargs,
    ) -> PdfWrapper:
        """
        Fills the PDF form with data from a dictionary.

        Args:
            data (Dict[str, Union[str, bool, int, BinaryIO, bytes]]): A dictionary where keys
                are form field names and values are the data to fill the fields with.
                Values can be strings, booleans, integers, file-like objects, or bytes.
            **kwargs: Additional keyword arguments:
                - `flatten` (bool): Whether to flatten the form after filling, making the fields read-only (default: False).

        Returns:
            PdfWrapper: The `PdfWrapper` object, allowing for method chaining.
        """

        for key, value in data.items():
            if key in self.widgets:
                self.widgets[key].value = value

        filled_stream, image_drawn_stream = fill(
            self._read(),
            self.widgets,
            need_appearances=getattr(self, "need_appearances"),
            use_full_widget_name=getattr(self, "use_full_widget_name"),
            flatten=kwargs.get("flatten", False),
        )

        if image_drawn_stream is not None:
            keys_to_copy = [
                k for k, v in self.widgets.items() if not isinstance(v, Signature)
            ]  # only copy non-image fields
            # Case: Single watermark PDF, mapping pages 1:1 to output pages.
            filled_stream = copy_watermark_widgets(
                remove_all_widgets(image_drawn_stream),
                filled_stream,
                keys_to_copy,
                None,
            )

        self._stream = filled_stream
        if image_drawn_stream is not None:
            # because copy_watermark_widgets and remove_all_widgets
            self._reregister_font()

        return self

    def annotate(self, annotations: Sequence[AnnotationTypes]) -> PdfWrapper:
        """
        Adds annotations to the PDF.

        This method allows you to add various types of annotations (e.g., text
        annotations/sticky notes) to the PDF pages.

        Args:
            annotations (Sequence[AnnotationTypes]): A list of annotation objects
                to be added to the PDF.

        Returns:
            PdfWrapper: The `PdfWrapper` object, allowing for method chaining.
        """

        self._stream = create_annotations(self._read(), annotations)

        return self

    def bulk_create_fields(self, fields: Sequence[FieldTypes]) -> PdfWrapper:
        """
        Creates multiple new form fields (widgets) on the PDF in a single operation.

        This method takes a list of field definition objects (`FieldTypes`),
        groups them by type (if necessary for specific widget handling, like CheckBoxField),
        and then delegates the creation to the internal `_bulk_create_fields` method.
        This is the preferred method for creating multiple fields as it minimizes
        PDF manipulation overhead.

        Args:
            fields (Sequence[FieldTypes]): A list of field definition objects
                (e.g., `TextField`, `CheckBoxField`, etc.) to be created.

        Returns:
            PdfWrapper: The `PdfWrapper` object, allowing for method chaining.
        """

        needs_separate_creation = [
            CheckBoxField,
            RadioGroup,
            SignatureField,
            ImageField,
        ]
        needs_separate_creation_dict = defaultdict(list)
        general_creation = []

        for each in fields:
            if type(each) in needs_separate_creation:
                needs_separate_creation_dict[type(each)].append(each)
            else:
                general_creation.append(each)

        needs_separate_creation_dict[SignatureField] = needs_separate_creation_dict.pop(
            SignatureField, []
        ) + needs_separate_creation_dict.pop(ImageField, [])
        needs_separate_creation_dict[CheckBoxField] = needs_separate_creation_dict.pop(
            CheckBoxField, []
        ) + needs_separate_creation_dict.pop(RadioGroup, [])

        for each in list(needs_separate_creation_dict.values()) + [general_creation]:
            if each:
                self._bulk_create_fields(each)

        return self

    def _bulk_create_fields(self, fields: Sequence[FieldTypes]) -> PdfWrapper:
        """
        Internal method to create multiple new form fields (widgets) on the PDF in a single operation.

        This method takes a list of field definition objects (`FieldTypes`),
        converts them into `Widget` objects, and efficiently draws them onto the
        PDF using bulk watermarking. It is designed to be called by the public
        `bulk_create_fields` method after fields have been grouped for creation.

        Args:
            fields (Sequence[FieldTypes]): A list of field definition objects
                (e.g., `TextField`, `CheckBoxField`, etc.) to be created.

        Returns:
            PdfWrapper: The `PdfWrapper` object, allowing for method chaining.
        """

        widgets = []
        widget_class = None
        for field in fields:
            field_dict = asdict(field)
            widget_class = getattr(field, "_widget_class")
            name = field_dict.pop("name")
            page_number = field_dict.pop("page_number")
            x = field_dict.pop("x")
            y = field_dict.pop("y")
            widgets.append(
                widget_class(
                    name=name,
                    page_number=page_number,
                    x=x,
                    y=y,
                    **{k: v for k, v in field_dict.items() if v is not None},
                )
            )

        watermarks = getattr(widget_class, "bulk_watermarks")(widgets, self._read())
        # Case: List of watermark PDFs, each corresponding to an output page.
        self._stream = copy_watermark_widgets(
            self._read(),
            watermarks,
            [widget.name for widget in widgets],
            None,
        )

        self._init_helper()

        for widget in widgets:
            for k, v in widget.hook_params:
                self.widgets[widget.name].__setattr__(k, v)

        return self

    def create_field(
        self,
        field: FieldTypes,
    ) -> PdfWrapper:
        """
        Creates a new form field (widget) on the PDF using a `FieldTypes` object.

        This method simplifies widget creation by taking a `FieldTypes` object
        and delegating to the internal `_bulk_create_fields` method.

        Args:
            field (FieldTypes): An object representing the field to create.
                This object encapsulates all necessary properties like name,
                page number, coordinates, and type of the field.

        Returns:
            PdfWrapper: The `PdfWrapper` object, allowing for method chaining.
        """

        return self._bulk_create_fields([field])

    def update_widget_key(
        self, old_key: str, new_key: str, index: int = 0, defer: bool = False
    ) -> PdfWrapper:
        """
        Updates the key (name) of a widget, allowing you to rename form fields.

        This method allows you to change the name of a form field in the PDF.  This can be useful for
        standardizing field names or resolving naming conflicts.  The update can be performed immediately
        or deferred until `commit_widget_key_updates` is called.

        Args:
            old_key (str): The old key of the widget that you want to rename.
            new_key (str): The new key to assign to the widget.
            index (int): The index of the widget if there are multiple widgets with the same name (default: 0).
            defer (bool): Whether to defer the update. If True, the update is added to a queue and applied
                when `commit_widget_key_updates` is called. If False, the update is applied immediately (default: False).

        Returns:
            PdfWrapper: The PdfWrapper object.
        """

        if getattr(self, "use_full_widget_name"):
            raise NotImplementedError

        if defer:
            self._keys_to_update.append((old_key, new_key, index))
            return self

        self._key_update_tracker[new_key] = old_key
        self._stream = update_widget_keys(
            self._read(), self.widgets, [old_key], [new_key], [index]
        )
        self._init_helper()

        return self

    def commit_widget_key_updates(self) -> PdfWrapper:
        """
        Commits deferred widget key updates, applying all queued key renames to the PDF.

        This method applies all widget key updates that were deferred using the `defer=True` option
        in the `update_widget_key` method.  It updates the underlying PDF stream with the new key names.

        Returns:
            PdfWrapper: The PdfWrapper object.
        """

        if getattr(self, "use_full_widget_name"):
            raise NotImplementedError

        old_keys = [each[0] for each in self._keys_to_update]
        new_keys = [each[1] for each in self._keys_to_update]
        indices = [each[2] for each in self._keys_to_update]

        self._stream = update_widget_keys(
            self._read(), self.widgets, old_keys, new_keys, indices
        )

        for each in self._keys_to_update:
            self._key_update_tracker[each[1]] = each[0]
        self._init_helper()
        self._keys_to_update = []

        return self

    def draw(self, elements: Sequence[RawTypes]) -> PdfWrapper:
        """
        Draws raw elements (text, images, etc.) directly onto the PDF pages.

        This method is the primary mechanism for drawing non-form field content.
        It takes a list of `RawText` or `RawImage` objects and renders them
        onto the PDF document as watermarks.

        Args:
            elements (Sequence[RawTypes]): A list of raw elements to draw (e.g., [RawText(...), RawImage(...)]).

        Returns:
            PdfWrapper: The `PdfWrapper` object, allowing for method chaining.
        """

        watermarks = create_watermarks_and_draw(
            self._read(), [each.to_draw for each in elements]
        )

        stream_with_widgets = self._read()
        self._stream = merge_watermarks_with_pdf(self._read(), watermarks)
        # Case: Single watermark PDF, mapping pages 1:1 to output pages.
        self._stream = copy_watermark_widgets(
            remove_all_widgets(self._read()), stream_with_widgets, None, None
        )
        # because copy_watermark_widgets and remove_all_widgets
        self._reregister_font()

        return self

    def register_font(
        self,
        font_name: str,
        ttf_file: Union[bytes, str, BinaryIO],
    ) -> PdfWrapper:
        """
        Registers a custom font for use in the PDF.

        Args:
            font_name (str): The name of the font. This name will be used to reference the font when drawing text.
            ttf_file (Union[bytes, str, BinaryIO]): The TTF file data, provided as either:
                - bytes: The raw TTF file data as a byte string.
                - str: The file path to the TTF file.
                - BinaryIO: An open file-like object containing the TTF file data.

        Returns:
            PdfWrapper: The `PdfWrapper` object, allowing for method chaining.
        """

        ttf_file = fp_or_f_obj_or_stream_to_stream(ttf_file)

        if register_font(font_name, ttf_file) if ttf_file is not None else False:
            self._stream, new_font_name = register_font_acroform(
                self._read(), font_name, ttf_file, getattr(self, "need_appearances")
            )
            self._available_fonts[font_name] = new_font_name
            self._font_register_events.append((font_name, ttf_file))

        return self
