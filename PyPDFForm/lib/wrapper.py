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
from contextlib import contextmanager
from copy import deepcopy
from dataclasses import asdict
from functools import lru_cache
from os import PathLike
from types import SimpleNamespace
from typing import (
    TYPE_CHECKING,
    Any,
    BinaryIO,
    Collection,
    Dict,
    Iterator,
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
from .constants import CHOICES_HOOK, FEATURE_HOOKS, FONT_HOOK, JAVASCRIPT_HOOKS
from .coordinate import generate_coordinate_grid
from .deprecation import reject_unsupported_kwargs
from .egress import (
    appearance_streams_handler,
    sync_acroform_fields,
    write_path,
)
from .field_tree import remove_widgets_by_keys, share_inline_fields
from .filler import fill
from .font import (
    add_font_metrics,
    get_all_available_fonts,
    register_font_acroform,
    temporary_font_registration,
    validate_font,
)
from .hooks import (
    ClearedSelection,
    FontChange,
    check_cleared_selections,
    trigger_widget_hooks,
)
from .patterns import is_unchanged, record_pdf_value
from .template import (
    build_widgets,
    create_annotations,
    get_on_open_javascript,
    get_title,
    get_widget_positions,
    set_on_open_javascript,
    set_title,
    update_widget_keys,
)
from .utils import (
    can_need_newer_version,
    generate_unique_suffix,
    generic_merge,
    get_catalog_version,
    get_newest_version,
    get_output_version,
    get_page_streams,
    get_required_version,
    get_version,
    merge_pdfs,
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
                - `generate_appearance_streams` (bool): Whether to explicitly generate appearance streams for form fields using pikepdf,
                  except for text fields and dropdowns it can't draw, which PDF viewers draw instead.
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
        Widgets and their parent fields stored inline, as earlier versions of PyPDFForm
        could save them, are first shared with the form's field tree, so that later
        operations change one object.
        Omitting the template, or passing empty bytes or an empty stream, creates an empty
        wrapper; a missing path raises instead.
        The PDF version is read from the template's header before the `title` keyword
        is applied, so output keeps it after operations that rewrite the PDF. The
        version that the template's own content requires is recorded too, so only
        newer features that operations add raise the output's version.
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
        self._stream = share_inline_fields(fp_or_f_obj_or_stream_to_stream(template))
        self.widgets = {}

        self._version = get_version(self._stream)  # before PDF writers rewrite it
        # what the template's own content requires; read() raises the version
        # only for newer features, so a header that understates it is kept
        self._baseline_version = (
            get_required_version(self._stream)
            if can_need_newer_version(self._version)
            else None
        )
        self._available_fonts = {}  # for setting /F1
        self._available_fonts_loaded = None  # for lazy loading fonts
        self._font_register_events = []  # for drawing, font lookups, and new wrappers
        self._fonts_without_metrics = {}  # resource name to TTF, for read()
        self._key_update_tracker = {}  # new key to old key, for renamed widgets
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
        and registered font resources, so fonts are not embedded again; their mappings,
        registration events, and the fonts that still need metrics in `read()` are
        copied instead. The recorded PDF version and the version its content
        required are copied so the copy writes the same header when serialized,
        including for features added before copying. Widgets and pending key
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
        result._baseline_version = self._baseline_version
        result._available_fonts = dict(self._available_fonts)
        result._available_fonts_loaded = self._available_fonts_loaded
        result._font_register_events = list(self._font_register_events)
        result._fonts_without_metrics = dict(self._fonts_without_metrics)
        result._keys_to_update = list(self._keys_to_update)

        return result

    def _init_helper(self, repointed: Collection[str] = ()) -> None:
        """
        Helper method to initialize widgets.

        This method is called during initialization and after certain operations
        that modify the PDF content (e.g., filling, creating widgets, updating keys).
        It rebuilds the widget dictionary and invalidates the lazily loaded font cache.
        Fields no longer in the PDF are dropped. Existing widget objects are kept
        for keys that remain, since queued hooks were already applied to the PDF
        and their properties match it, unless the key gives access to another
        field than before. A renamed widget is built from the PDF and takes the
        state the PDF doesn't hold from the widget it replaces, with
        `Widget.copy_unread_state`.

        Args:
            repointed (Collection[str]): Keys that remain but give access to
                another field than before, such as after renaming the field a
                key gave access to by index. Their widgets are built from the
                PDF rather than kept.
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
        for k, v in new_widgets.items():
            if k in self.widgets and k not in repointed:
                new_widgets[k] = self.widgets[k]
            elif (
                k in self._key_update_tracker
                and self._key_update_tracker[k] in self.widgets
            ):
                v.copy_unread_state(self.widgets[self._key_update_tracker[k]])
        self._key_update_tracker = {}

        self.widgets = new_widgets

    @property
    def _generates_appearances(self) -> bool:
        """
        Whether `read()` generates appearance streams.

        It does only when both `need_appearances` and
        `generate_appearance_streams` are enabled, so filling and property
        changes keep the appearances that the generator draws in only then.

        Returns:
            bool: True if appearance streams are generated.
        """
        return bool(
            getattr(self, "need_appearances")
            and getattr(self, "generate_appearance_streams")
        )

    @contextmanager
    def _restore_on_failure(
        self, defer: bool = False
    ) -> Iterator[list[ClearedSelection]]:
        """
        Restores the wrapper's state if the enclosed operation raises.

        The wrapper's attributes, including the PDF stream and widgets, and
        each widget's attributes and queued hooks are recorded first. Queued
        widget hooks are then applied, so a hook that fails is reverted and
        raised by `_read` before the operation starts, and later reads don't
        retry it. With `defer`, a dropdown field whose cleared selection
        still inherits a value doesn't raise there, since the operation can
        give it a value of its own or remove it; it raises after the
        operation if the field still inherits one, as `check_cleared_selections`
        checks, so applying the hooks belongs to the operation. If the
        operation raises, the recorded state is restored, with the hooks
        queued again, before the exception propagates, so the wrapper and its
        PDF output are both unchanged. Widget objects keep their identity.

        Args:
            defer (bool): Whether the operation can give a field a value of
                its own or remove it. Defaults to False.

        Yields:
            list[ClearedSelection]: Each such field, empty without `defer`.
        """

        state = {
            name: value.copy() if isinstance(value, (dict, list)) else value
            for name, value in vars(self).items()
        }
        widget_states = [
            (widget, widget.save_state()) for widget in self.widgets.values()
        ]
        cleared: list[ClearedSelection] = []
        self._read(cleared if defer else None)

        try:
            yield cleared
            check_cleared_selections(self._stream, cleared)
        except Exception:
            self.__dict__.clear()
            self.__dict__.update(state)
            for widget, widget_state in widget_states:
                widget.restore_state(widget_state)
            raise

    def _ensure_available_fonts_loaded(self) -> dict:
        """
        Loads AcroForm fonts from the PDF stream the first time they are needed.

        Custom fonts registered through `register_font` are stored in the same
        mapping, so loading updates the existing dictionary instead of replacing it.
        A registered name keeps its registered font when a font in the PDF has the
        same name.

        Returns:
            dict: A mapping from font names to internal PDF font identifiers.
        """

        if not self._available_fonts_loaded:
            if self._stream:
                registered = {each[0] for each in self._font_register_events}
                self._available_fonts.update(
                    {
                        k: v
                        for k, v in get_all_available_fonts(self._stream).items()
                        if k not in registered
                    }
                )
            self._available_fonts_loaded = True

        return self._available_fonts

    @staticmethod
    @lru_cache(maxsize=8)
    def _get_page_streams_with_widgets(stream: bytes) -> tuple[bytes, ...]:
        """
        Extracts page streams while preserving the original page widgets.

        Each single-page PDF keeps the page's annotations and only the parts of
        their fields on that page, without copying content of other pages.

        Args:
            stream (bytes): The PDF stream to split into pages.

        Returns:
            tuple[bytes, ...]: Single-page PDF streams with widgets preserved.

        Raises:
            ValueError: If a page refers to content of another page in a way
                that cannot be removed, or a field shared with another page
                has a `/Parent` cycle before an entry it inherits.
        """

        return tuple(get_page_streams(stream))

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

        This is the version in the header of `read()` output. It is read from the
        template's header when the wrapper is created, or set by `change_version`,
        and raised when an operation adds a feature that requires a newer version,
        such as a form field added to a PDF 1.1 document. A header that already
        understates the template's own content is kept. When the template has no
        supported header, the version is read from the current PDF stream instead.
        Pending widget changes are not applied to the wrapper, but those that can
        change the version, such as comb, tooltips, and widget JavaScript, are
        applied to a copy of the PDF, so the result matches the next `read()`.
        When they can't be applied, the committed document's version is returned,
        and `read()` raises the error.

        Returns:
            str | None: The PDF version as a string, or None if the version cannot be determined.
        """

        version = self._recorded_version()
        if not can_need_newer_version(version):
            return version

        return self._choose_version(
            self._egress(self._with_pending_feature_changes(self._stream)), version
        )

    def _recorded_version(self) -> str | None:
        """
        Returns the PDF version read from the template or set by `change_version`.

        When the template has no supported header, the version is read from the
        stored PDF stream instead, without applying pending widget changes.

        Returns:
            str | None: The recorded PDF version, before any raise for features
                that operations added.
        """

        return self._version if self._version is not None else get_version(self._stream)

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
        parameters and PDF version, which is raised for the newer features that
        operations added to the page. A catalog `/Version` override, which the page
        doesn't keep, counts toward that version. Content of other pages is not
        copied: links and GoTo actions to other pages are removed, and a field
        shared with other pages keeps only its widgets on the page. Custom font
        registration events are replayed onto the page wrappers when needed.

        Returns:
            Sequence[PdfWrapper]: A list of `PdfWrapper` objects, one for each page in the PDF.

        Raises:
            ValueError: If a page refers to content of another page in another way,
                such as an action that resets a field on another page, or a
                field shared with another page has a `/Parent` cycle before an
                entry it inherits.
        """

        stream = self._read()
        version = self._recorded_version()
        # pages don't keep the catalog, so a /Version override moves to the header
        version = get_newest_version([version, get_catalog_version(stream)]) or version
        result = [
            self.__class__(
                # the stored stream's header may be a PDF writer's default
                set_version(each, get_version(each), version),
                **{param: getattr(self, param) for param, _ in self.USER_PARAMS},
            )
            for each in self._get_page_streams_with_widgets(stream)
        ]
        for page in result:
            # so features that operations added still raise the page's version
            page._baseline_version = self._baseline_version  # noqa: SLF001 # pylint: disable=W0212

        # because page streams do not copy the AcroForm fonts
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
        1. Triggers widget hooks and updates font mappings (via `_read`). If a
           hook raises, all queued widget updates are reverted before the error
           propagates.
        2. If `need_appearances` is enabled, it handles appearance streams and the
           `/NeedAppearances` flag, which may include removing XFA and explicitly
           generating appearance streams. Fonts registered while it was disabled
           first get the font metrics that appearance generation uses, and
           appearance streams are generated after step 3, since the generator
           draws only the fields that the AcroForm lists.
        3. Adds the fields of page widget annotations to the AcroForm `/Fields`
           array, keeping every field already listed, including fields without
           a widget on a page, and makes page widget appearances valid, such as
           by removing the value strings earlier versions wrote. The stream is
           left unchanged when no page has a widget annotation.
        4. Writes the wrapper's PDF version into the header after egress
           processing, since PDF writers may emit their own default version.
           The version read from the template or set by `change_version` is
           raised when the output has a newer feature than both it and the
           content it was read or set for, such as an interactive form added to
           a PDF 1.1 document.
        The wrapper's stored stream is not replaced by these final egress-only changes.

        Returns:
            bytes: The processed PDF document content as a byte string.
        """

        result = self._egress(self._read())
        version = self._choose_version(result, self._recorded_version())
        if version:
            result = set_version(result, get_version(result), version)
        return result

    def _egress(self, stream: bytes) -> bytes:
        """
        Applies the egress steps of `read()` to a PDF stream, except its version.

        These are the appearance handling for `need_appearances`, the update
        of the AcroForm `/Fields` array, and the repair of widget appearances
        that aren't valid. The fields are also listed before
        appearance streams are generated, since the generator draws only the
        fields that the AcroForm lists, such as created fields. The wrapper is
        not changed.

        Args:
            stream (bytes): The PDF stream, such as the wrapper's stored stream.

        Returns:
            bytes: The processed PDF stream, with the header of the last PDF
                writer that rewrote it.
        """

        result = stream
        if getattr(self, "need_appearances") and result:
            if self._fonts_without_metrics:
                result = add_font_metrics(
                    result, tuple(self._fonts_without_metrics.items())
                )
            if self._generates_appearances:
                result = sync_acroform_fields(result)
            result = appearance_streams_handler(
                result, getattr(self, "generate_appearance_streams")
            )  # cached

        return sync_acroform_fields(result) if result else result

    def _choose_version(self, output: bytes, version: str | None) -> str | None:
        """
        Chooses the PDF version to write into the header of an egress output.

        The version is raised only when the output requires a newer one than the
        recorded version, the baseline, and a catalog `/Version` override.

        Args:
            output (bytes): The output of `_egress`.
            version (str | None): The recorded PDF version.

        Returns:
            str | None: `version`, raised for the newer features that operations
                added, or None for an empty output.
        """

        if not output:
            return None

        if can_need_newer_version(version):
            return get_output_version(
                version,
                # a catalog /Version override also covers the output's features
                get_newest_version(
                    [self._baseline_version, get_catalog_version(output)]
                ),
                get_required_version(output),
            )

        return version

    def _with_pending_feature_changes(self, stream: bytes) -> bytes:
        """
        Applies the queued widget changes that can add or remove a table feature.

        These are the hooks in `FEATURE_HOOKS`, such as comb, tooltips, and
        widget JavaScript, applied in queue order to a copy of `stream`, so the
        result has the features that `read()` would write. Other changes can't
        change the version, and are left out, so a hook that would fail, such as
        a font size on a field without a valid `/DA`, doesn't raise here. The widgets
        and their queues are not changed. Every JavaScript value is applied as
        an empty script, since only whether a script is written matters, so a
        path or a readable object is left for `read()` to open or read. If a
        change still can't be applied, such as removing a tooltip that a shared
        parent field sets, `stream` is returned unchanged, so the version is the
        committed document's, and `read()` raises the error.

        Args:
            stream (bytes): The PDF stream, such as the wrapper's stored stream.

        Returns:
            bytes: The stream with those changes applied, or `stream` when none
                are queued or they can't be applied.
        """

        pending = {
            key: SimpleNamespace(
                hooks_to_trigger=[
                    (hook, "" if hook in JAVASCRIPT_HOOKS else value)
                    for hook, value in widget.hooks_to_trigger
                    if hook in FEATURE_HOOKS
                ]
            )
            for key, widget in self.widgets.items()
        }
        if not any(each.hooks_to_trigger for each in pending.values()):
            return stream

        try:
            return trigger_widget_hooks(
                stream, pending, getattr(self, "use_full_widget_name")
            )
        # any error a hook raises is left for read(), which reverts the queue
        except Exception:  # noqa: BLE001 # pylint: disable=W0718
            return stream

    def _read(self, cleared: list[ClearedSelection] | None = None) -> bytes:
        """
        Reads the PDF stream, triggering widget hooks and updating fonts if necessary.

        This internal method executes queued widget hooks. A font being changed is
        passed to its hook with the resource name of the registered font or font
        of the PDF with its name, and each changed widget's font is then read back
        from the changed PDF, as reopening it reads it. So is the selection of
        each dropdown whose choices were replaced, as `_commit_read_back`
        describes. The changed PDF and what is read back are committed
        together, which updates the wrapper's stored stream and clears each
        widget's hook queue. If a hook or reading back raises, every widget's
        queued hooks are discarded and their properties are restored to their
        committed values, so the stream and widgets are unchanged and later
        reads do not retry the failed updates.

        Args:
            cleared (list[ClearedSelection] | None): Where to collect the
                dropdown fields whose cleared selection still inherits a value,
                instead of raising, as `trigger_widget_hooks` describes.
                Defaults to None.

        Returns:
            bytes: The raw PDF stream.

        Raises:
            Exception: Any error raised while applying a hook or reading
                back is re-raised after the queued updates are reverted.
        """

        widgets_with_hooks = [
            widget for widget in self.widgets.values() if widget.hooks_to_trigger
        ]

        if widgets_with_hooks:
            font_widgets = self._queue_font_changes(widgets_with_hooks)
            chosen = {
                id(widget): widget
                for widget in widgets_with_hooks
                if any(hook == CHOICES_HOOK for hook, _ in widget.hooks_to_trigger)
            }
            # a None the PDF holds, not one assigned over its selection
            unselected = {
                key
                for key, widget in chosen.items()
                if widget.value is None and is_unchanged(widget)
            }

            # the changed PDF and what is read back from it are committed
            # only when both succeed
            try:
                stream = trigger_widget_hooks(
                    self._stream,
                    self.widgets,
                    getattr(self, "use_full_widget_name"),
                    self._generates_appearances,
                    cleared,
                )
                read_back = self._read_back(stream, font_widgets, chosen)
            except Exception:
                for widget in self.widgets.values():
                    widget.revert_property_updates()
                raise

            self._stream = stream
            for widget in self.widgets.values():
                self._commit_read_back(
                    widget, read_back.get(id(widget), {}), id(widget) in unselected
                )
                widget.clear_property_updates()

        return self._stream

    def _queue_font_changes(self, widgets: list) -> dict:
        """
        Passes each queued font change the resource name its font has.

        Only fonts being changed are looked up, so a font read from the PDF that
        has the name of a registered font, such as `Courier`, is left as it is.
        Each font hook gets a `FontChange` with the assigned name and the
        resource name of the registered font or font of the PDF with that name,
        which the hook uses unless the annotation already uses the font.

        Args:
            widgets (list): The widgets with queued hooks.

        Returns:
            dict: The widgets with a queued font change, by `id`.
        """
        font_widgets = {
            id(widget): widget
            for widget in widgets
            if any(hook == FONT_HOOK for hook, _ in widget.hooks_to_trigger)
        }
        if font_widgets:
            available_fonts = self._ensure_available_fonts_loaded()
            for widget in font_widgets.values():
                widget.hooks_to_trigger = [
                    (
                        hook,
                        FontChange(
                            value,
                            available_fonts[value]
                            if value in available_fonts
                            and value not in available_fonts.values()
                            else None,
                        )
                        if hook == FONT_HOOK
                        else value,
                    )
                    for hook, value in widget.hooks_to_trigger
                ]

        return font_widgets

    def _read_back(self, stream: bytes, font_widgets: dict, chosen: dict) -> dict:
        """
        Reads fonts and selections of widgets back from a changed PDF, as reopening it does.

        Each annotation's font hook decides by its own `/DA`, so the widgets of
        a field can get different fonts, and the key gives access to the last.
        The selection of a dropdown whose choices were replaced is read the
        same way.

        Args:
            stream (bytes): The PDF with the changes applied.
            font_widgets (dict): The widgets whose font was changed, by `id`.
            chosen (dict): The dropdowns whose choices were replaced, by `id`.

        Returns:
            dict: The `font` or `value` read back for each of those widgets,
                by `id`.
        """
        if not font_widgets and not chosen:
            return {}

        written = build_widgets(stream, getattr(self, "use_full_widget_name"))
        result = {}
        for key, widget in self.widgets.items():
            # a key the PDF no longer has keeps the widget's attributes
            new = written.get(key, widget)
            if id(widget) in font_widgets:
                result.setdefault(id(widget), {})["font"] = getattr(
                    new, "font", widget.font
                )
            if id(widget) in chosen:
                result.setdefault(id(widget), {})["value"] = new.value

        return result

    @staticmethod
    def _commit_read_back(widget: Any, read: dict, unselected: bool) -> None:
        """
        Gives a widget what `_read_back` read for it.

        A font replaces the widget's. A dropdown without a selection, as the
        PDF held none, takes the selection read back, which its value can name
        among the new choices. The selection read back is recorded as the
        PDF's value, as `record_pdf_value` describes, so the next fill doesn't
        write a dropdown that has it, such as to the other fields with its
        key, whose selections moved on their own, and writes one that doesn't.

        Args:
            widget (Any): The middleware widget.
            read (dict): The `font` or `value` read back for it.
            unselected (bool): Whether it is a dropdown whose None the PDF
                held, as opposed to one assigned over the PDF's selection.
        """
        if "font" in read:
            widget.__dict__["font"] = read["font"]
        if "value" in read:
            if unselected:
                widget.__dict__["_value"] = read["value"]
            record_pdf_value(widget, read["value"])

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

        The method replaces the PDF header version marker of the current stream, which
        an earlier operation's PDF writer may have set to its own default, and updates
        the version that `read()` writes into its output. The version is kept for the
        content the document has now, including what `read()` adds for the wrapper's
        current options, such as an AcroForm for `need_appearances`, even if that
        content requires a newer version. Later operations, and options enabled
        later, that add a newer feature raise it again. It does not
        otherwise validate or rewrite the document for version-specific compatibility.

        Args:
            version (str): The new PDF version string (e.g., "1.7").

        Returns:
            PdfWrapper: The `PdfWrapper` object, allowing for method chaining.
        """

        current_stream = self._read()
        updated_stream = set_version(
            current_stream, get_version(current_stream), version
        )
        if updated_stream != current_stream or get_version(updated_stream) == version:
            self._stream = updated_stream
            self._version = version
            self._baseline_version = (
                get_required_version(self._egress(updated_stream))
                if can_need_newer_version(version)
                else None
            )

        return self

    def generate_coordinate_grid(
        self, color: Tuple[float, float, float] = (1, 0, 0), margin: float = 100
    ) -> PdfWrapper:
        """
        Generates a coordinate grid on the PDF, useful for debugging layout issues.

        The grid is drawn as page watermarks merged into the page content.
        Annotations, including widgets, keep their objects, so references to
        them, such as the AcroForm field tree, are unchanged. Registered fonts
        stay in the AcroForm resources and are not embedded again.

        Args:
            color (Tuple[float, float, float]): The color of the grid lines, specified as an RGB tuple (default: red).
            margin (float): The margin around the grid, in points (default: 100).

        Returns:
            PdfWrapper: The `PdfWrapper` object, allowing for method chaining.
        """

        self._stream = generate_coordinate_grid(self._read(), color, margin)

        return self

    def fill(
        self,
        data: Dict[str, str | bool | int | BinaryIO | bytes],
        **kwargs,
    ) -> PdfWrapper:
        """
        Fills the PDF form with data from a dictionary.

        Only keys that already exist in `self.widgets` are applied. A field that
        shares a key with a widget of another type, such as a checkbox and a radio
        group with the same short name, keeps its value; its widgets are still made
        read-only with `readonly=True`. A radio group fills only its own options.
        A checkbox, text field, or dropdown whose value isn't supplied, and is
        still the one the PDF holds, as read or last filled, isn't written
        again, so it keeps its appearance. A text field or dropdown that is
        written loses its appearance, so PDF viewers draw the new value. When
        `read()` generates appearance streams, which needs both
        `need_appearances` and `generate_appearance_streams`, it keeps its
        appearance instead, which the generator draws the new value in.
        Filling delegates to the
        lower-level filler, which draws image/signature values onto the page
        and removes only the consumed widgets. Other annotations and unfilled
        signature/image fields are preserved. After image drawing, the widget cache
        is refreshed to remove consumed fields while retaining the middleware objects
        for surviving fields so subsequent style updates can still use them. With
        `readonly=True`, every remaining widget reports `readonly` as True.
        Supplied and retained values are prepared before any assignments or PDF
        hooks are applied, so an invalid choice index or ambiguous dropdown string
        leaves widget values, pending hooks, and PDF state unchanged. Only supplied
        values are assigned. If later processing raises, such as for an invalid
        image, widget values and the PDF are restored before the error propagates.

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
            ValueError: If an integer dropdown or radio index is out of range, a
                dropdown string matches options that differ, or `readonly` is
                True and the parent fields of a field form a cycle. Nothing is
                changed.
        """

        reject_unsupported_kwargs(self, "fill", kwargs, ["readonly"])
        readonly = kwargs.get("readonly", False)
        pending = {
            key: self.widgets[key].prepare_value(value)
            for key, value in data.items()
            if key in self.widgets
        }
        for key, widget in self.widgets.items():
            if key not in data:
                widget.prepare_value(widget.value)

        with self._restore_on_failure(defer=True) as cleared:
            for key, update in pending.items():
                self.widgets[key].apply_value(update)

            # the widget's own field lost its selection, so a value the
            # widget has was assigned since and is written
            replaced = {each.key for each in cleared if each.read}
            filled_stream, image_drawn_stream = fill(
                self._read(),
                self.widgets,
                generate_appearance_streams=self._generates_appearances,
                use_full_widget_name=getattr(self, "use_full_widget_name"),
                supplied=set(data) | replaced,
                readonly=readonly,
            )

            self._stream = (
                image_drawn_stream if image_drawn_stream is not None else filled_stream
            )
            for widget in self.widgets.values():
                if widget.value is not None:
                    # the PDF now holds it, so the next fill doesn't write it again
                    record_pdf_value(widget)
            if image_drawn_stream is not None:
                self._init_helper()

        if readonly:
            for widget in self.widgets.values():
                # the PDF already has the flag, so no hook is queued
                widget.__dict__["readonly"] = True

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
        path. If creating any group raises, the PDF and widgets are restored, so
        no field is created.

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

        with self._restore_on_failure():
            for each in list(needs_separate_creation_dict.values()) + [
                general_creation
            ]:
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
        Keys use the same names as `widgets` and also match fields without a
        widget on any page. Removed fields are taken off their pages and out of
        the PDF's form fields and calculation order. Reset, submit, and hide
        actions stop naming them. An action left with no field to act on does
        nothing, and is removed unless other actions run with it; JavaScript
        is not changed. Objects that only removed fields used are dropped from
        the PDF. Keys that match no field are ignored. If removal
        raises, the PDF and widgets are restored.

        Args:
            keys (List[str]): A list of form field keys to remove.

        Returns:
            PdfWrapper: The `PdfWrapper` object, allowing for method chaining.

        Raises:
            ValueError: If the `/Parent` chain of a field or widget to remove has
                a cycle.
        """

        with self._restore_on_failure(defer=True):
            self._stream = remove_widgets_by_keys(
                self._stream, keys, getattr(self, "use_full_widget_name")
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
        the underlying PDF stream with the new key names, rebuilds the widget cache, and clears the queue.
        Renamed widgets are read from the PDF. A renamed field keeps the state of the widget its old key
        gave access to that the PDF doesn't hold, such as a value not filled yet or JavaScript, without
        queuing hooks again, when it is that widget's field. A key that gives access to another field
        after the rename, such as one whose field was renamed by index, gets a widget read from the PDF,
        so that state stays with the field it was set on. If committing raises, the PDF, widgets, and
        queue are restored.

        Returns:
            PdfWrapper: The PdfWrapper object.
        """

        if getattr(self, "use_full_widget_name"):
            raise NotImplementedError

        old_keys = [each[0] for each in self._keys_to_update]
        new_keys = [each[1] for each in self._keys_to_update]
        indices = [each[2] for each in self._keys_to_update]

        with self._restore_on_failure():
            before = get_widget_positions(self._stream)
            self._stream = update_widget_keys(
                self._stream, self.widgets, old_keys, new_keys, indices
            )
            after = get_widget_positions(self._stream)

            for old_key, new_key, _ in self._keys_to_update:
                # only the field the old key gave access to takes its widget's state
                if old_key in before and after.get(new_key) == before[old_key]:
                    self._key_update_tracker[new_key] = old_key
            self._init_helper(
                {key for key in before if key in after and before[key] != after[key]}
            )
            self._keys_to_update = []

        return self

    def draw(self, elements: Sequence[RawTypes]) -> PdfWrapper:
        """
        Draws raw elements (text, images, etc.) directly onto the PDF pages.

        This method is the primary mechanism for drawing non-form field content.
        It takes a list of raw element objects, temporarily registers custom fonts
        for ReportLab drawing, renders the elements onto page watermarks, and merges
        those watermarks into the page content. Annotations, including widgets, keep
        their objects, so references to them, such as the AcroForm field tree, are
        unchanged. Registered fonts stay in the AcroForm resources and are not
        embedded again.

        Args:
            elements (Sequence[RawTypes]): A list of raw elements to draw (e.g., [RawText(...), RawImage(...)]).

        Returns:
            PdfWrapper: The `PdfWrapper` object, allowing for method chaining.
        """

        with temporary_font_registration(self._font_register_events) as font_mapping:
            watermarks = create_watermarks_and_draw(
                self._read(), [each.to_draw for each in elements], font_mapping
            )

        self._stream = merge_watermarks_with_pdf(self._read(), watermarks)

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
        is kept so the font can be used for drawing and registered again on wrappers
        created from this one, such as pages and merged PDFs. A font registered while
        `need_appearances` is disabled gets the font metrics that appearance generation
        uses in `read()` output once it is enabled. Invalid font streams are ignored,
        but a missing font path raises.

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
            if not getattr(self, "need_appearances"):
                self._fonts_without_metrics[new_font_name] = ttf_file

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
