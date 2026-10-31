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
underlying PDF manipulation. `PdfArray` is a list of `PdfWrapper` objects
that merges them when sliced or merged.
"""

from __future__ import annotations

from collections import defaultdict
from copy import deepcopy
from dataclasses import asdict
from functools import lru_cache
from os import PathLike
from typing import (
    TYPE_CHECKING,
    Any,
    BinaryIO,
    Dict,
    List,
    Sequence,
    TextIO,
    Tuple,
)

from .adapter import (
    fp_or_f_obj_or_f_content_to_content,
    fp_or_f_obj_or_stream_to_stream,
    readable,
)
from .coordinate import generate_coordinate_grid
from .deprecation import reject_unsupported_kwargs
from .egress import (
    appearance_streams_handler,
    rebuild_acroform_fields,
    write_path,
)
from .filler import fill
from .font import (
    get_all_available_fonts,
    register_font_acroform,
    temporary_font_registration,
    validate_font,
)
from .hooks import trigger_widget_hooks
from .middleware.dropdown import Dropdown
from .middleware.text import Text
from .template import (
    build_widgets,
    create_annotations,
    get_on_open_javascript,
    get_title,
    remove_widgets_by_keys,
    set_on_open_javascript,
    set_title,
    update_widget_keys,
)
from .utils import (
    generate_unique_suffix,
    generic_merge,
    get_page_streams,
    get_version,
    merge_pdfs,
    remove_all_widgets,
    set_version,
)
from .watermark import (
    copy_watermark_widgets,
    create_watermarks_and_draw,
    merge_watermarks_with_pdf,
)
from .widgets import (
    CheckBoxField,
    DropdownField,
    ImageField,
    RadioGroup,
    SignatureField,
)

if TYPE_CHECKING:
    from .annotations import AnnotationTypes
    from .assets.blank import BlankPage
    from .raw import RawTypes
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
                - `title` (str | None): The title stored in the PDF's document
                  metadata. A non-None value replaces the existing title; None
                  preserves it.

    """

    USER_PARAMS = [
        ("use_full_widget_name", False),
        ("need_appearances", False),
        ("generate_appearance_streams", False),
        ("title", None),
    ]

    def __init__(
        self,
        template: bytes | str | PathLike | BinaryIO | BlankPage = b"",
        **kwargs,
    ) -> None:
        """
        Constructor method for the `PdfWrapper` class.

        Initializes a new `PdfWrapper` object with the given template PDF and optional keyword arguments.
        The template is normalized to bytes and existing widgets are loaded immediately.
        Omitting the template, or passing empty bytes or an empty stream, creates an empty
        wrapper; a missing path raises instead.
        The title and document-open JavaScript remain in the PDF stream and are read
        lazily when their properties are accessed. A non-None `title` keyword updates
        the title in the PDF stream; None leaves the template's title unchanged. Enabling
        `generate_appearance_streams` also enables `need_appearances`.

        Args:
            template (bytes | str | PathLike | BinaryIO | BlankPage): The template PDF, provided as either:
                - bytes: The raw PDF data as a byte string.
                - str | PathLike: The file path to the PDF.
                - BinaryIO: An open file-like object containing the PDF data.
                - BlankPage: A blank page object.
                Defaults to an empty byte string (b"").
            **kwargs: Additional keyword arguments to configure the `PdfWrapper`.
                These arguments are used to set the user-configurable parameters defined in `USER_PARAMS`.
                For example: `use_full_widget_name=True` or `need_appearances=False`.

        Raises:
            TypeError: If a keyword argument is not in `USER_PARAMS` or the template type is unsupported.
            OSError: If the template path cannot be opened, such as `FileNotFoundError`.
        """

        super().__init__()
        reject_unsupported_kwargs(
            self, "__init__", kwargs, [each[0] for each in self.USER_PARAMS]
        )
        self._stream = fp_or_f_obj_or_stream_to_stream(template)
        self.widgets = {}

        self._version = None
        self._available_fonts = {}  # for setting /F1
        self._available_fonts_loaded = None  # for lazy loading fonts
        self._font_register_events = []  # for reregister
        self._key_update_tracker = {}  # for update key preserve old key attrs
        self._keys_to_update = []  # for bulk update keys

        # sets attrs from kwargs
        for attr, default in self.USER_PARAMS:
            setattr(self, attr, kwargs.get(attr, default))

        if getattr(self, "generate_appearance_streams") is True:
            self.need_appearances = True

        self._init_helper()

    def __add__(self, other: PdfWrapper | Sequence[PdfWrapper]) -> PdfWrapper:
        """
        Merges PDF wrappers together, creating a new `PdfWrapper` containing the combined content.

        Field-name conflicts are resolved by adding a unique suffix to names in the right-hand
        wrapper. Renames are committed only when queued, modifying that wrapper. The result uses
        the left-hand wrapper's user parameters and inherits its registered custom fonts. Links
        to internal pages keep pointing to the same pages in the merged PDF.

        Collision-free merges work in full-name mode. A collision requiring a rename of a
        full-name field still raises `NotImplementedError`.

        Args:
            other (PdfWrapper | Sequence[PdfWrapper]): The other `PdfWrapper` object or
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
                other.update_widget_key(k, f"{k}-{unique_suffix}")

        if other._keys_to_update:
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

    def _copy(self) -> PdfWrapper:
        """
        Creates an independent copy of this wrapper.

        The copy starts from the current PDF stream, which already contains the title
        and registered font resources, so fonts are not embedded again; their mappings
        and registration events are copied instead. The cached PDF version is copied
        so the copy restores the same header when serialized. Widgets and pending key
        updates are copied so either wrapper can change without affecting the other.
        Readable stream values on widgets are shared because they cannot be duplicated.

        Returns:
            PdfWrapper: The copied `PdfWrapper` object.
        """

        # pylint: disable=W0212
        result: PdfWrapper = self.__class__(
            self._read(),
            **{
                each[0]: getattr(self, each[0], each[1])
                for each in self.USER_PARAMS
                if each[0] != "title"
            },
        )
        result.widgets = deepcopy(
            self.widgets,
            {
                id(value): value
                for widget in self.widgets.values()
                for value in vars(widget).values()
                if readable(value)
            },
        )
        result._version = self._version
        result._available_fonts = dict(self._available_fonts)
        result._available_fonts_loaded = self._available_fonts_loaded
        result._font_register_events = list(self._font_register_events)
        result._keys_to_update = list(self._keys_to_update)

        return result

    def _init_helper(self) -> None:
        """
        Helper method to initialize widgets.

        This method is called during initialization and after certain operations
        that modify the PDF content (e.g., filling, creating widgets, updating keys).
        It rebuilds the widget dictionary and invalidates the lazily loaded font cache.
        """

        self._available_fonts_loaded = False
        stream = self._read()
        new_widgets = (
            build_widgets(
                stream,
                getattr(self, "use_full_widget_name"),
            )
            if stream
            else {}
        )
        # ensure old widgets don't get overwritten
        for k, v in self.widgets.items():
            if k in new_widgets:
                new_widgets[k] = v

        # update key preserve old key attrs
        for k, v in new_widgets.items():
            if k in self._key_update_tracker:
                old_widget = self.widgets[self._key_update_tracker[k]]
                for name in old_widget.attr_set_tracker:
                    setattr(v, name, getattr(old_widget, name, None))
        self._key_update_tracker = {}

        self.widgets = new_widgets

    def _ensure_available_fonts_loaded(self) -> dict:
        """
        Loads AcroForm fonts from the PDF stream the first time they are needed.

        Custom fonts registered through `register_font` are stored in the same
        mapping, so loading updates the existing dictionary instead of replacing it.

        Returns:
            dict: A mapping from font names to internal PDF font identifiers.
        """

        if not self._available_fonts_loaded:
            if self._stream:
                self._available_fonts.update(**get_all_available_fonts(self._stream))
            self._available_fonts_loaded = True

        return self._available_fonts

    @staticmethod
    @lru_cache(maxsize=8)
    def _get_page_streams_with_widgets(stream: bytes) -> tuple[bytes, ...]:
        """
        Extracts page streams while preserving the original page widgets.

        Widgets are removed before splitting the PDF into pages, then cloned back
        from the original stream onto the matching single-page PDF. This avoids
        page extraction losing form field annotations.

        Args:
            stream (bytes): The PDF stream to split into pages.

        Returns:
            tuple[bytes, ...]: Single-page PDF streams with widgets preserved.
        """

        return tuple(
            # Case: Single watermark PDF, extracting a specific page to the first output page.
            copy_watermark_widgets(page_stream, stream, None, i)
            for i, page_stream in enumerate(
                get_page_streams(remove_all_widgets(stream))
            )
        )

    def _reregister_font(self) -> PdfWrapper:
        """
        Reregisters fonts after PDF content modifications.

        This method is called after operations that modify the PDF content
        (e.g., drawing text, drawing images) to ensure that custom fonts
        are correctly registered and available for use. It replays the font
        registration events that existed at method entry, then trims those
        replayed events so only newly added events remain queued.
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
    def title(self) -> str | None:
        """
        Gets the title stored in the PDF's document metadata.

        The title is read lazily from the current PDF stream.

        Returns:
            str | None: The current document title, or None when no title exists.
        """

        result = get_title(self._read())
        return str(result) if result is not None else None

    @title.setter
    def title(self, value: str | None) -> None:
        """
        Updates the title stored in the PDF's document metadata.

        A non-None value is written to the underlying PDF stream immediately.
        None is ignored so the current title is preserved.

        Args:
            value (str | None): The new document title, or None to preserve the
                current title.
        """

        if value is not None:
            self._stream = set_title(self._read(), value)

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
            "additionalProperties": False,
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
                  their corresponding data (str | bool | int | None).
        """

        return {key: value.value for key, value in self.widgets.items()}

    @property
    def sample_data(self) -> dict:
        """
        Returns sample data for the PDF form, providing example values for each form field.

        This sample data can be used for testing or demonstration purposes.
        Fields without a usable sample value, including empty dropdowns and
        radio groups, are omitted so the sample remains valid against the schema.

        Returns:
            dict: A dictionary containing sample data for the PDF form.
        """

        return {
            key: sample
            for key, widget in self.widgets.items()
            if (sample := widget.sample_value) is not None
        }

    @property
    def version(self) -> str | None:
        """
        Returns the PDF version of the underlying PDF document.

        The version is read from the PDF header lazily and cached so egress-only
        rewrites can restore the wrapper's original version even if an underlying
        PDF writer emits a different default header.

        Returns:
            str | None: The PDF version as a string, or None if the version cannot be determined.
        """

        if self._version is None:
            self._version = get_version(self._read())

        return self._version

    @property
    def fonts(self) -> list:
        """
        Returns a list of the names of the currently registered fonts.

        Accessing this property loads AcroForm fonts from the PDF stream if
        they have not already been loaded.

        Returns:
            list: A list of font names (str).
        """

        return list(self._ensure_available_fonts_loaded().keys())

    @property
    def pages(self) -> Sequence[PdfWrapper]:
        """
        Returns a list of `PdfWrapper` objects, each representing a single page in the PDF document.

        This allows you to work with individual pages of the PDF. Each page wrapper
        preserves the page's original widgets and inherits the current wrapper's user
        parameters. Links to other pages are removed. Custom font registration events
        are replayed onto the page wrappers when needed.

        Returns:
            Sequence[PdfWrapper]: A list of `PdfWrapper` objects, one for each page in the PDF.
        """

        result = [
            self.__class__(
                each,
                **{param: getattr(self, param) for param, _ in self.USER_PARAMS},
            )
            for each in self._get_page_streams_with_widgets(self._read())
        ]

        # because copy_watermark_widgets and remove_all_widgets
        if self._font_register_events:
            for event in self._font_register_events:
                for page in result:
                    page.register_font(event[0], event[1])

        return PdfArray(result)

    @property
    def on_open_javascript(self) -> str | None:
        """
        Gets the JavaScript stored in the PDF's document-open action.

        The script is read lazily from the current PDF stream, including an existing
        JavaScript `/OpenAction` in the input template.

        Returns:
            str | None: The current document-open JavaScript, or None when the PDF
                does not contain a JavaScript document-open action.
        """

        return get_on_open_javascript(self._read())

    @on_open_javascript.setter
    def on_open_javascript(self, value: str | TextIO) -> None:
        """
        Sets the JavaScript script that executes when the PDF is opened.

        Assignment immediately writes a JavaScript `/OpenAction` to the stored
        PDF stream, replacing any existing document-open action.

        Args:
            value (str | TextIO): The JavaScript script, provided as either:
                - str: The JavaScript code as a string, or a file path to a .js file.
                - TextIO: An open file-like object containing the JavaScript code.
        """

        script = fp_or_f_obj_or_f_content_to_content(value)
        self._stream = set_on_open_javascript(self._read(), script)

    def read(self) -> bytes:
        """
        Reads the PDF document and returns its content as bytes.

        This method retrieves the PDF stream and performs several processing steps:
        1. Triggers widget hooks and updates font mappings (via `_read`).
        2. If `need_appearances` is enabled, it handles appearance streams and the
           `/NeedAppearances` flag, which may include removing XFA and explicitly
           generating appearance streams.
        3. Rebuilds the AcroForm `/Fields` array from page annotations for
           widgets known to this wrapper, leaving the stream unchanged when no
           matching widget annotations are found.
        4. Restores the wrapper's cached PDF header version after egress
           processing, since PDF writers may emit their own default version.
        The wrapper's stored stream is not replaced by these final egress-only changes.

        Returns:
            bytes: The processed PDF document content as a byte string.
        """

        result = self._read()
        if getattr(self, "need_appearances") and result:
            result = appearance_streams_handler(
                result, getattr(self, "generate_appearance_streams")
            )  # cached

        if result:
            result = rebuild_acroform_fields(
                result,
                set(self.widgets.keys()),
                getattr(self, "use_full_widget_name"),
            )
            if self.version:
                result = set_version(result, get_version(result), self.version)
        return result

    def _read(self) -> bytes:
        """
        Reads the PDF stream, triggering widget hooks and updating fonts if necessary.

        This internal method executes queued widget hooks. When a pending font hook
        exists, user-facing registered font names are mapped to their internal PDF
        resource names before hooks are applied. Applying hooks updates the wrapper's
        stored stream and clears each widget's hook queue.

        Returns:
            bytes: The raw PDF stream.
        """

        widgets_with_hooks = [
            widget for widget in self.widgets.values() if widget.hooks_to_trigger
        ]

        if widgets_with_hooks:
            has_font_hook = any(
                hook[0] == "update_text_field_font"
                for widget in widgets_with_hooks
                for hook in widget.hooks_to_trigger
            )

            if has_font_hook:
                available_fonts = self._ensure_available_fonts_loaded()
                for widget in self.widgets.values():
                    if (
                        isinstance(widget, (Text, Dropdown))
                        and widget.font not in available_fonts.values()
                        and widget.font in available_fonts
                    ):
                        # from `new_font` to `/F1`
                        widget.font = available_fonts.get(widget.font)

            self._stream = trigger_widget_hooks(
                self._stream,
                self.widgets,
                getattr(self, "use_full_widget_name"),
            )

        return self._stream

    def write(self, dest: str | bytes | PathLike | BinaryIO) -> PdfWrapper:
        """
        Serialize the PDF, then write it to a path or an open binary stream.

        Paths use atomic replacement after a sibling temporary file closes; failures preserve existing bytes.
        Symlinks are followed and permission bits preserved; new files are private (0600 on POSIX).
        Other metadata and hard links are not preserved. Stream write failures can leave partial output.

        Args:
            dest (str | bytes | PathLike | BinaryIO): A regular file path or writable binary stream.

        Returns:
            PdfWrapper: The `PdfWrapper` object, allowing for method chaining.
        """

        content = self.read()
        if isinstance(dest, (str, bytes, PathLike)):
            write_path(dest, content)
        else:
            dest.write(content)

        return self

    def change_version(self, version: str) -> PdfWrapper:
        """
        Changes the PDF version of the underlying document.

        The method replaces the first PDF header version marker in the current stream
        and updates the cached version used by later egress processing. It does not
        otherwise validate or rewrite the document for version-specific compatibility.

        Args:
            version (str): The new PDF version string (e.g., "1.7").

        Returns:
            PdfWrapper: The `PdfWrapper` object, allowing for method chaining.
        """

        current_stream = self._read()
        updated_stream = set_version(current_stream, self.version, version)
        if updated_stream != current_stream:
            self._stream = updated_stream
            self._version = version

        return self

    def generate_coordinate_grid(
        self, color: Tuple[float, float, float] = (1, 0, 0), margin: float = 100
    ) -> PdfWrapper:
        """
        Generates a coordinate grid on the PDF, useful for debugging layout issues.

        Existing widgets are temporarily removed while the grid is drawn as page
        watermarks, then copied back onto the resulting stream. Registered fonts are
        restored afterward because the remove/copy cycle rewrites the PDF.

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
        data: Dict[str, str | bool | int | BinaryIO | bytes],
        **kwargs,
    ) -> PdfWrapper:
        """
        Fills the PDF form with data from a dictionary.

        Only keys that already exist in `self.widgets` are applied. Filling delegates
        to the lower-level filler, which draws image/signature values onto the page
        and removes only the consumed widgets. Other annotations and unfilled
        signature/image fields are preserved. After image drawing, the widget cache
        is refreshed to remove consumed fields while retaining the middleware objects
        for surviving fields so subsequent style updates can still use them.
        Supplied and retained values are prepared before any assignments or PDF
        hooks are applied, so an invalid choice index leaves widget values,
        pending hooks, and PDF state unchanged. Only supplied values are assigned.
        Errors during later PDF processing are not rolled back by this preparation.

        Args:
            data (Dict[str, str | bool | int | BinaryIO | bytes]): A dictionary where keys
                are form field names and values are the data to fill the fields with.
                Values can be strings, booleans, integers, file-like objects, or bytes.
            **kwargs: Additional keyword arguments:
                - `readonly` (bool): Whether to make form fields read-only when filling (default: False).
                  False does not make existing read-only fields editable.

        Returns:
            PdfWrapper: The `PdfWrapper` object, allowing for method chaining.

        Raises:
            TypeError: If a keyword argument other than `readonly` is passed. Nothing is changed.
            ValueError: If an integer dropdown or radio index is out of range.
        """

        reject_unsupported_kwargs(self, "fill", kwargs, ["readonly"])
        pending = [
            (self.widgets[key], self.widgets[key].prepare_value(value))
            for key, value in data.items()
            if key in self.widgets
        ]
        for key, widget in self.widgets.items():
            if key not in data:
                widget.prepare_value(widget.value)
        for widget, update in pending:
            widget.apply_value(update)

        filled_stream, image_drawn_stream = fill(
            self._read(),
            self.widgets,
            need_appearances=getattr(self, "need_appearances"),
            use_full_widget_name=getattr(self, "use_full_widget_name"),
            readonly=kwargs.get("readonly", False),
        )

        self._stream = (
            image_drawn_stream if image_drawn_stream is not None else filled_stream
        )
        if image_drawn_stream is not None:
            self._init_helper()

        return self

    def annotate(self, annotations: Sequence[AnnotationTypes]) -> PdfWrapper:
        """
        Adds annotations to the PDF.

        This method allows you to add various types of annotations (e.g., text
        annotations/sticky notes) to the PDF pages. The annotation objects are
        converted to PDF dictionaries and appended to the target pages.

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
        groups them by creation strategy, and then delegates each group to the
        internal `_bulk_create_fields` method. Signatures and images are processed
        separately because each constructs a different PDF annotation; checkboxes
        and radio groups are grouped together because they share ReportLab button
        handling; multiple dropdown fields are routed through the general creation
        path.

        Args:
            fields (Sequence[FieldTypes]): A list of field definition objects
                (e.g., `TextField`, `CheckBoxField`, etc.) to be created.

        Returns:
            PdfWrapper: The `PdfWrapper` object, allowing for method chaining.
        """

        needs_separate_creation = [
            CheckBoxField,
            RadioGroup,
            DropdownField,
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

        needs_separate_creation_dict[CheckBoxField] = needs_separate_creation_dict.pop(
            CheckBoxField, []
        ) + needs_separate_creation_dict.pop(RadioGroup, [])

        if (
            DropdownField in needs_separate_creation_dict
            and len(needs_separate_creation_dict[DropdownField]) > 1
        ):
            general_creation += needs_separate_creation_dict.pop(DropdownField, [])

        for each in list(needs_separate_creation_dict.values()) + [general_creation]:
            if each:
                self._bulk_create_fields(each)

        return self

    def _bulk_create_fields(self, fields: Sequence[FieldTypes]) -> PdfWrapper:
        """
        Internal method to create multiple new form fields (widgets) on the PDF in a single operation.

        This method takes a list of field definition objects (`FieldTypes`),
        converts them into widget objects, creates page-aligned watermark PDFs for
        those widgets, copies the generated widget annotations into the current PDF,
        refreshes the widget cache, and applies any hook parameters captured during
        field construction.

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

    def remove_fields(self, keys: List[str]) -> PdfWrapper:
        """
        Removes form fields from the PDF by their keys.

        This method removes any fields whose keys are included in `keys` and
        refreshes the wrapper's widget metadata after the PDF stream is updated.

        Args:
            keys (List[str]): A list of form field keys to remove.

        Returns:
            PdfWrapper: The `PdfWrapper` object, allowing for method chaining.
        """

        self._stream = remove_widgets_by_keys(
            self._read(), keys, getattr(self, "use_full_widget_name")
        )
        self._init_helper()

        return self

    def update_widget_key(
        self, old_key: str, new_key: str, index: int = 0
    ) -> PdfWrapper:
        """
        Updates the key (name) of a widget, allowing you to rename form fields.

        This method queues a change to the name of a form field in the PDF. This can be useful for
        standardizing field names or resolving naming conflicts. The queued update is applied when
        `commit_widget_key_updates` is called. Renaming is not supported while full widget names are
        being used for lookup.

        Args:
            old_key (str): The old key of the widget that you want to rename.
            new_key (str): The new key to assign to the widget.
            index (int): The index of the widget if there are multiple widgets with the same name (default: 0).

        Returns:
            PdfWrapper: The PdfWrapper object.
        """

        if getattr(self, "use_full_widget_name"):
            raise NotImplementedError

        self._keys_to_update.append((old_key, new_key, index))
        return self

    def commit_widget_key_updates(self) -> PdfWrapper:
        """
        Commits deferred widget key updates, applying all queued key renames to the PDF.

        This method applies all widget key updates queued by the `update_widget_key` method. It updates
        the underlying PDF stream with the new key names, rebuilds the widget cache, preserves attributes
        that were set on the old widget objects, and clears the queue.

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
        It takes a list of raw element objects, temporarily registers custom fonts
        for ReportLab drawing, renders the elements onto page watermarks, merges those
        watermarks into the PDF, and copies the original widgets back onto the output.

        Args:
            elements (Sequence[RawTypes]): A list of raw elements to draw (e.g., [RawText(...), RawImage(...)]).

        Returns:
            PdfWrapper: The `PdfWrapper` object, allowing for method chaining.
        """

        with temporary_font_registration(self._font_register_events) as font_mapping:
            watermarks = create_watermarks_and_draw(
                self._read(), [each.to_draw for each in elements], font_mapping
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
        ttf_file: bytes | str | PathLike | BinaryIO,
    ) -> PdfWrapper:
        """
        Registers a custom font for use in the PDF.

        Valid TrueType font data is embedded into the PDF's AcroForm resources and
        recorded under the user-provided `font_name`. The original registration input
        is kept so font resources can be replayed after operations that rewrite the
        PDF stream. Invalid font streams are ignored, but a missing font path raises.

        Args:
            font_name (str): The name of the font. This name will be used to reference the font when drawing text.
            ttf_file (bytes | str | PathLike | BinaryIO): The TTF file data, provided as either:
                - bytes: The raw TTF file data as a byte string.
                - str | PathLike: The file path to the TTF file.
                - BinaryIO: An open file-like object containing the TTF file data.

        Returns:
            PdfWrapper: The `PdfWrapper` object, allowing for method chaining.

        Raises:
            OSError: If the font path cannot be opened, such as `FileNotFoundError`.
            TypeError: If the font input type is unsupported.
        """

        ttf_file = fp_or_f_obj_or_stream_to_stream(ttf_file)

        if validate_font(font_name, ttf_file) if ttf_file is not None else False:
            self._ensure_available_fonts_loaded()
            self._stream, new_font_name = register_font_acroform(
                self._read(), ttf_file, getattr(self, "need_appearances")
            )
            self._available_fonts[font_name] = new_font_name
            self._font_register_events.append((font_name, ttf_file))

        return self


class PdfArray(list):
    """
    A specialized list subclass designed to hold PdfWrapper objects.

    When sliced, this list automatically merges the contained PdfWrapper
    objects using the PdfWrapper.__add__ method, returning a single
    merged PdfWrapper object. If the slice is empty, it returns None.
    For non-slice indexing, it behaves like a standard list.
    """

    def __getitem__(self, key: Any) -> list | Any:
        """
        Retrieves an item or a slice of items from the list.

        If the key is a slice, it merges the PdfWrapper objects in the slice
        and returns a single merged PdfWrapper.
        If the key is an index, it returns the PdfWrapper at that index.

        Args:
            key (int | slice): The index or slice to retrieve.

        Returns:
            PdfWrapper | list | Any: A single merged PdfWrapper if sliced,
                                          or the item at the index if indexed.
        """

        if isinstance(key, slice):
            result = None
            wrappers = super().__getitem__(key)
            for each in wrappers:
                if not result:
                    result = each
                else:
                    result += each

            return result
        return super().__getitem__(key)

    def merge(self) -> Any:
        """
        Merges all PdfWrapper objects in the list into a single new PdfWrapper.

        This method uses a pairwise merging strategy to combine all PdfWrapper
        objects contained in the list into one. An empty array returns a new empty
        PdfWrapper. The result is never one of the contained wrappers: when merging
        would return an input unchanged, such as for a one-item array or when the
        other wrappers are empty, an independent copy of that wrapper is returned
        instead, including its user parameters, widget settings, and custom fonts.

        Returns:
            Any: A single new merged PdfWrapper object.
        """

        if not self:
            return PdfWrapper()

        result = (
            generic_merge(list(self), lambda x, y: x + y) if len(self) > 1 else self[0]
        )
        if any(result is each for each in self):
            result = result._copy()  # noqa: SLF001 # pylint: disable=W0212

        return result
