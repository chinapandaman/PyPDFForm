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
from functools import lru_cache
from os import PathLike
from typing import (
    TYPE_CHECKING,
    BinaryIO,
    Dict,
    List,
    Optional,
    Sequence,
    TextIO,
    Tuple,
)

from .adapter import (
    fp_or_f_obj_or_f_content_to_content,
    fp_or_f_obj_or_stream_to_stream,
)
from .constants import VERSION_IDENTIFIER_PREFIX, VERSION_IDENTIFIERS
from .coordinate import generate_coordinate_grid
from .egress import (
    appearance_streams_handler,
    preserve_field_tree,
    preserve_pdf_properties,
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
from .middleware.signature import Signature
from .middleware.text import Text
from .template import (
    build_widgets,
    create_annotations,
    get_metadata,
    remove_widgets_by_keys,
    update_widget_keys,
)
from .types import PdfArray
from .utils import (
    generate_unique_suffix,
    get_page_streams,
    merge_pdfs,
    remove_all_widgets,
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
                - `preserve_metadata` (bool): Whether to preserve the original metadata of the PDF.
                - `title` (str): The title of the PDF document.

    """

    USER_PARAMS = [
        ("use_full_widget_name", False),
        ("need_appearances", False),
        ("generate_appearance_streams", False),
        ("preserve_metadata", False),
        ("preserve_field_tree", False),
        ("title", None),
    ]

    def __init__(
        self,
        template: bytes | str | BinaryIO | BlankPage = b"",
        **kwargs,
    ) -> None:
        """
        Constructor method for the `PdfWrapper` class.

        Initializes a new `PdfWrapper` object with the given template PDF and optional keyword arguments.
        The template is normalized to bytes, existing widgets are loaded immediately, and
        original metadata is captured only when `preserve_metadata` is requested.
        Enabling `generate_appearance_streams` also enables `need_appearances`.

        Args:
            template (bytes | str | BinaryIO | BlankPage): The template PDF, provided as either:
                - bytes: The raw PDF data as a byte string.
                - str: The file path to the PDF.
                - BinaryIO: An open file-like object containing the PDF data.
                - BlankPage: A blank page object.
                Defaults to an empty byte string (b"").
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

        This method allows you to combine PDF forms into a single form. It handles potential
        naming conflicts between form fields by adding a unique suffix to the field names in the
        form being merged, commits those queued renames before merging, and returns a new wrapper
        configured with the left-hand wrapper's user parameters. Registered custom fonts from the
        left-hand wrapper are carried into the result.

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
    @lru_cache(maxsize=128)
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

        Returns:
            dict: A dictionary containing sample data for the PDF form.
        """

        return {key: value.sample_value for key, value in self.widgets.items()}

    @property
    def version(self) -> str | None:
        """
        Returns the PDF version of the underlying PDF document.

        Returns:
            str | None: The PDF version as a string, or None if the version cannot be determined.
        """

        for each in VERSION_IDENTIFIERS:
            if self._read().startswith(each):
                return each.replace(VERSION_IDENTIFIER_PREFIX, b"").decode()

        return None

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
        parameters. Custom font registration events are replayed onto the page wrappers
        when needed.

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
        Returns the JavaScript script that executes when the PDF is opened.

        Returns:
            str | None: The JavaScript script, or None if no script is set.
        """

        return self._on_open_javascript

    @on_open_javascript.setter
    def on_open_javascript(self, value: str | TextIO) -> None:
        """
        Sets the JavaScript script that executes when the PDF is opened.

        Args:
            value (str | TextIO): The JavaScript script, provided as either:
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
        3. If `preserve_metadata`, title, or on-open JavaScript are set, it preserves
           or updates the corresponding PDF properties accordingly.
        The wrapper's stored stream is not replaced by these final egress-only changes.

        Returns:
            bytes: The processed PDF document content as a byte string.
        """

        result = self._read()
        if getattr(self, "need_appearances") and result:
            result = appearance_streams_handler(
                result, getattr(self, "generate_appearance_streams")
            )  # cached

        if any(
            [getattr(self, "preserve_metadata"), self.title, self.on_open_javascript]
        ):
            result = preserve_pdf_properties(
                result,
                self.title,
                self.on_open_javascript,
                self._metadata if getattr(self, "preserve_metadata") else None,
            )
        if result and getattr(self, "preserve_field_tree"):
            result = preserve_field_tree(
                result, set(self.widgets.keys()), getattr(self, "use_full_widget_name")
            )
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

    def write(self, dest: str | BinaryIO) -> PdfWrapper:
        """
        Writes the PDF to a file.

        String, bytes, and PathLike destinations are opened in binary write mode.
        Other objects are treated as already-open writable binary streams.

        Args:
            dest (str | BinaryIO): The destination to write the PDF to.
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

        The method replaces the first PDF header version marker in the current stream.
        It does not otherwise validate or rewrite the document for version-specific
        compatibility.

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
        to the lower-level filler, then handles the special image/signature path by
        drawing those values as watermarks and copying the remaining widgets back onto
        the output. The wrapper's widget cache is intentionally left in place so
        subsequent style updates can still refer to the same middleware objects.

        Args:
            data (Dict[str, str | bool | int | BinaryIO | bytes]): A dictionary where keys
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
        internal `_bulk_create_fields` method. Signatures and images are grouped
        together because both copy bedrock annotations; checkboxes and radio groups
        are grouped together because they share ReportLab button handling; multiple
        dropdown fields are routed through the general creation path.

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

        needs_separate_creation_dict[SignatureField] = needs_separate_creation_dict.pop(
            SignatureField, []
        ) + needs_separate_creation_dict.pop(ImageField, [])
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
        ttf_file: bytes | str | BinaryIO,
    ) -> PdfWrapper:
        """
        Registers a custom font for use in the PDF.

        Valid TrueType font data is embedded into the PDF's AcroForm resources and
        recorded under the user-provided `font_name`. The original registration input
        is kept so font resources can be replayed after operations that rewrite the
        PDF stream. Invalid font streams are ignored.

        Args:
            font_name (str): The name of the font. This name will be used to reference the font when drawing text.
            ttf_file (bytes | str | BinaryIO): The TTF file data, provided as either:
                - bytes: The raw TTF file data as a byte string.
                - str: The file path to the TTF file.
                - BinaryIO: An open file-like object containing the TTF file data.

        Returns:
            PdfWrapper: The `PdfWrapper` object, allowing for method chaining.
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
