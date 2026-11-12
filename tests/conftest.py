# -*- coding: utf-8 -*-

import json
import os
import platform
import runpy
import tomllib
from importlib import metadata
from io import BytesIO

import pikepdf
import pytest
from packaging.requirements import Requirement
from packaging.utils import canonicalize_name
from PIL import features

from PyPDFForm import PdfWrapper
from PyPDFForm.lib.middleware.checkbox import Checkbox

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIXTURE_ENVIRONMENT_PATH = os.path.join(ROOT, "pdf_samples", "fixture_environment.json")
regenerated_in_place = pytest.StashKey[bool]()


def _zlib_info():
    # the same zlib detection that `make check-zlib` and CI use
    return runpy.run_path(os.path.join(ROOT, "scripts", "check_zlib.py"))["zlib_info"]()


def _runtime_dependencies():
    # the runtime dependencies, whose versions can change the bytes of expected PDFs
    with open(os.path.join(ROOT, "pyproject.toml"), "rb") as f:
        dependencies = tomllib.load(f)["project"]["dependencies"]

    return [canonicalize_name(Requirement(each).name) for each in dependencies]


def fixture_environment():
    zlib_info = _zlib_info()
    environment = {
        "python": platform.python_version(),
        "python_implementation": platform.python_implementation(),
        "platform": f"{platform.system()}-{platform.machine()}",
        "zlib_backend": zlib_info["zlib_backend"],
        "zlib_compile_time_version": zlib_info["zlib_compile_time_version"],
        "zlib_runtime_version": zlib_info["zlib_runtime_version"],
        "pillow_zlib_version": features.version("zlib"),
        "qpdf": pikepdf.__libqpdf_version__,
    }
    for package in _runtime_dependencies():
        environment[package] = metadata.version(package)

    return environment


def _regenerating_in_place(config):
    return config.getoption("--regenerate") == "1" and not config.getoption(
        "--regenerate-dir"
    )


def pytest_configure(config):
    config.results = {}
    if _regenerating_in_place(config) and _zlib_info()["zlib_backend"] != "zlib":
        msg = (
            "Expected PDFs must be regenerated with standard zlib, but this "
            "Python uses zlib-ng. Regenerate them in the development container."
        )
        raise pytest.UsageError(msg)


def pytest_addoption(parser):
    parser.addoption("--regenerate", action="store", default="0")
    parser.addoption("--regenerate-dir", action="store", default="")


def pytest_report_header(config):
    current = fixture_environment()
    lines = [
        "expected PDF environment: "
        + ", ".join(f"{key} {value}" for key, value in current.items())
    ]
    record = os.path.relpath(FIXTURE_ENVIRONMENT_PATH, ROOT)
    try:
        with open(FIXTURE_ENVIRONMENT_PATH, encoding="utf-8") as f:
            recorded = json.load(f)
    except (OSError, ValueError) as e:
        lines.append(f"{record} could not be read: {e}")
        return lines
    if not isinstance(recorded, dict):
        lines.append(
            f"{record} could not be read: expected a JSON object, "
            f"got {type(recorded).__name__}"
        )
        return lines

    differences = [
        f"{key} {current.get(key)} (recorded {recorded.get(key)})"
        for key in {**current, **recorded}
        if current.get(key) != recorded.get(key)
    ]
    if differences:
        lines.append(f"differs from {record}: " + ", ".join(differences))
    else:
        lines.append(f"matches {record}")

    return lines


def pytest_sessionfinish(session):
    # record the environment of the latest in-place regeneration
    if session.config.stash.get(regenerated_in_place, False):
        with open(FIXTURE_ENVIRONMENT_PATH, "w", encoding="utf-8", newline="\n") as f:
            json.dump(fixture_environment(), f, indent=2)
            f.write("\n")


@pytest.fixture(autouse=True)
def _generate_new_pdf_samples(request):
    request.config.results = {}
    yield
    if (
        request.config.getoption("--regenerate") == "1"
        and request.config.results
        and not request.config.results.get("skip_regenerate")
    ):
        output_path = request.config.results["expected_path"]
        regenerate_dir = request.config.getoption("--regenerate-dir")
        if regenerate_dir:
            # write to the same relative path under regenerate_dir instead of
            # overwriting the expected PDF
            output_path = os.path.join(
                regenerate_dir,
                os.path.relpath(
                    output_path, os.path.join(os.path.dirname(__file__), "..")
                ),
            )
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
        else:
            request.config.stash[regenerated_in_place] = True

        with open(output_path, "wb+") as f:
            f.write(request.config.results["stream"])


def _read_stream(obj):
    try:
        return obj.read_bytes()
    except pikepdf.PdfError:
        # stored with a filter qpdf doesn't decode, such as an image codec
        return obj.read_raw_bytes()


def describe_pdf(stream, timestamped=False):
    # the version, trailer, and objects of a PDF, described so that they don't
    # depend on how its streams are compressed
    with pikepdf.Pdf.open(BytesIO(stream)) as pdf:
        trailer = pikepdf.Dictionary(pdf.trailer)
        if "/ID" in trailer:
            # derived from the creation time or from the written bytes
            del trailer["/ID"]
        info = pdf.trailer.get("/Info")
        description = {"version": pdf.pdf_version, "trailer": trailer.unparse()}
        for index, obj in enumerate(pdf.objects):
            if not isinstance(obj, pikepdf.Object):
                # an indirect number or boolean, which has no object number here
                description[f"object at index {index}"] = repr(obj)
            elif isinstance(obj, pikepdf.Stream):
                properties = pikepdf.Dictionary(obj.stream_dict)
                # the length of the stored, usually compressed, data
                del properties["/Length"]
                description[obj.objgen] = properties.unparse(), _read_stream(obj)
            elif timestamped and info is not None and obj.objgen == info.objgen:
                dated = pikepdf.Dictionary(obj)
                for key in ("/CreationDate", "/ModDate"):
                    if key in dated:
                        del dated[key]
                description[obj.objgen] = dated.unparse()
            else:
                description[obj.objgen] = obj.unparse(resolved=True)

        return description


@pytest.fixture(scope="session")
def standard_zlib():
    # expected PDFs hold the bytes that standard zlib produces
    return _zlib_info()["zlib_backend"] == "zlib"


@pytest.fixture
def assert_same_pdf(standard_zlib):
    # for tests whose expected bytes depend on Python's zlib: the PDF must have
    # the same objects as the expected PDF on every platform, and the same bytes
    # with standard zlib
    def check(actual, expected, timestamped=False):
        actual_description = describe_pdf(actual, timestamped)
        expected_description = describe_pdf(expected, timestamped)
        differences = sorted(
            str(key)
            for key in actual_description.keys() | expected_description.keys()
            if actual_description.get(key) != expected_description.get(key)
        )
        assert not differences

        if standard_zlib:
            assert len(actual) == len(expected)
            if not timestamped:
                # a timestamped PDF only keeps its length between runs
                assert actual == expected

    return check


@pytest.fixture
def assert_page_ownership():
    # every page is in the page tree, every annotation belongs to the page that
    # lists it, and every widget of a listed field is on a page
    def check(stream):
        with pikepdf.Pdf.open(BytesIO(stream)) as pdf:
            pages = {page.obj.objgen for page in pdf.pages}
            assert not [
                obj.objgen
                for obj in pdf.objects
                if isinstance(obj, pikepdf.Dictionary)
                and obj.get("/Type") == pikepdf.Name.Page
                and obj.objgen not in pages
            ]
            annots = {}
            for page in pdf.pages:
                for annot in page.get("/Annots", []):
                    annots[annot.objgen] = annot
                    if "/P" in annot:
                        assert annot.P.objgen == page.obj.objgen
            for annot in annots.values():
                parent = (
                    annot.get("/Parent")
                    if annot.Subtype == pikepdf.Name.Widget
                    else None
                )
                while parent is not None:
                    assert all(
                        kid.objgen in annots or "/Kids" in kid for kid in parent.Kids
                    )
                    parent = parent.get("/Parent")

    return check


@pytest.fixture
def assert_catalog_fields():
    # the catalog lists exactly the fields with these fully qualified names, and
    # their widgets are exactly the widgets on the pages, each of them once
    def check(stream, names):
        with pikepdf.Pdf.open(BytesIO(stream)) as pdf:
            on_pages = [
                annot.objgen
                for page in pdf.pages
                for annot in page.get("/Annots", [])
                if annot.get("/Subtype") == pikepdf.Name.Widget
            ]
            acroform = pdf.Root.get("/AcroForm", pikepdf.Dictionary())
            pending = [(field, "") for field in acroform.get("/Fields", [])]
            found = []
            listed = []
            while pending:
                field, prefix = pending.pop()
                name = prefix + str(field.get("/T", ""))
                kids = list(field.get("/Kids", []))
                # kids with a name are fields, the others are the field's widgets
                pending.extend((kid, f"{name}.") for kid in kids if "/T" in kid)
                widgets = [kid for kid in kids if "/T" not in kid]
                if widgets or not kids:
                    found.append(name)
                    listed.extend(each.objgen for each in widgets or [field])

            assert sorted(found) == sorted(names)
            assert len(set(listed)) == len(listed)
            assert sorted(listed) == sorted(on_pages)

    return check


@pytest.fixture
def assert_round_trip():
    # the wrapper and its reopened output both read these values
    def check(pdf, data):
        reopened = PdfWrapper(pdf.read(), use_full_widget_name=pdf.use_full_widget_name)
        for name, value in data.items():
            for actual in (pdf.data[name], reopened.data[name]):
                # True == 1 and False == 0, but a checkbox value isn't an index
                assert isinstance(actual, bool) == isinstance(value, bool)
                assert actual == value

    return check


def _same_property(actual, expected):
    # numbers are compared approximately, since the PDF stores them as reals,
    # and a list or tuple of choices or per-option geometry element by element
    if isinstance(actual, (list, tuple)) and isinstance(expected, (list, tuple)):
        return len(actual) == len(expected) and all(
            _same_property(a, b) for a, b in zip(actual, expected, strict=True)
        )
    if isinstance(actual, bool) or isinstance(expected, bool):
        return actual is expected
    if isinstance(actual, (int, float)) and isinstance(expected, (int, float)):
        return actual == pytest.approx(expected)

    return actual == expected


# the widget properties that opening a PDF reads from it
READ_PROPERTIES = (
    "value",
    "page_number",
    "x",
    "y",
    "width",
    "height",
    "readonly",
    "required",
    "hidden",
    "tooltip",
    "comb",
    "alignment",
    "multiline",
    "max_length",
    "choices",
    "number_of_options",
)


@pytest.fixture
def assert_widgets_match_output():
    # the wrapper's fields, values, and properties read from the PDF are the
    # same as those of its reopened output
    def check(pdf):
        stream = pdf.read()
        reopened = PdfWrapper(stream, use_full_widget_name=pdf.use_full_widget_name)
        assert list(pdf.widgets) == list(reopened.widgets)
        for name, widget in pdf.widgets.items():
            other = reopened.widgets[name]
            assert type(widget) is type(other)
            for prop in READ_PROPERTIES:
                actual, expected = (
                    getattr(widget, prop, None),
                    getattr(other, prop, None),
                )
                if prop == "value" and type(widget) is Checkbox:
                    # an unchecked checkbox reads None, filled with False or not
                    actual, expected = actual or None, expected or None
                assert _same_property(actual, expected), (name, prop, actual, expected)

    return check


@pytest.fixture
def assert_valid_appearances():
    # every appearance is a dictionary of appearance streams, and a widget with
    # appearance states selects one of them or none
    def check(stream):
        with pikepdf.Pdf.open(BytesIO(stream)) as pdf:
            for page in pdf.pages:
                for annot in page.get("/Annots", []):
                    if "/AP" not in annot:
                        continue
                    assert isinstance(annot.AP, pikepdf.Dictionary)
                    assert "/N" in annot.AP
                    for key in ("/N", "/R", "/D"):
                        appearance = annot.AP.get(key)
                        if appearance is None or isinstance(appearance, pikepdf.Stream):
                            continue
                        assert isinstance(appearance, pikepdf.Dictionary)
                        assert all(
                            isinstance(each, pikepdf.Stream)
                            for each in appearance.values()
                        )
                    if not isinstance(annot.AP.N, pikepdf.Stream):
                        state = annot.get("/AS")
                        # a string with the same characters selects no state
                        assert isinstance(state, pikepdf.Name)
                        assert str(state) in ("/Off", *annot.AP.N.keys())

    return check


def describe_annotations(stream, changed):
    # each page's annotations, without the widgets of the changed fields,
    # described so that they don't depend on object numbers or compression
    with pikepdf.Pdf.open(BytesIO(stream)) as pdf:
        pages = {page.obj.objgen: index for index, page in enumerate(pdf.pages)}

        def get_name(field):
            names = []
            while field is not None:
                if "/T" in field:
                    names.append(str(field.T))
                field = field.get("/Parent")

            return ".".join(reversed(names))

        def describe(obj, seen):
            if not isinstance(obj, pikepdf.Object):
                return repr(obj)
            if obj.is_indirect:
                if obj.objgen in pages:
                    return f"page {pages[obj.objgen] + 1}"
                if obj.objgen in seen:
                    # a reference back to an object that is being described
                    return "seen"
                seen = {*seen, obj.objgen}
            if isinstance(obj, pikepdf.Stream):
                return (
                    {
                        key: describe(value, seen)
                        for key, value in obj.stream_dict.items()
                        if key != "/Length"
                    },
                    _read_stream(obj),
                )
            if isinstance(obj, pikepdf.Dictionary):
                # a field's other widgets are described where their pages list them
                return {
                    key: describe(value, seen)
                    for key, value in obj.items()
                    if key != "/Kids"
                }
            if isinstance(obj, pikepdf.Array):
                return [describe(each, seen) for each in obj]

            return obj.unparse()

        return [
            [
                describe(annot, set())
                for annot in page.get("/Annots", [])
                if annot.get("/Subtype") != pikepdf.Name.Widget
                or get_name(annot) not in changed
            ]
            for page in pdf.pages
        ]


@pytest.fixture
def assert_annotations_preserved():
    # every annotation, other than the widgets of the fields with these fully
    # qualified names, has the same content on the same page in the same order
    def check(before, after, changed=()):
        assert describe_annotations(after, changed) == describe_annotations(
            before, changed
        )

    return check


@pytest.fixture
def pdf_samples():
    return os.path.join(os.path.dirname(__file__), "..", "pdf_samples")


@pytest.fixture
def js_samples():
    return os.path.join(os.path.dirname(__file__), "..", "js_samples")


@pytest.fixture
def json_samples():
    return os.path.join(os.path.dirname(__file__), "..", "json_samples")


@pytest.fixture
def yaml_samples():
    return os.path.join(os.path.dirname(__file__), "..", "yaml_samples")


@pytest.fixture
def static_pdfs():
    return os.path.join(os.path.dirname(__file__), "..", "docs", "pdfs")


@pytest.fixture
def template_stream(pdf_samples):
    with open(os.path.join(pdf_samples, "sample_template.pdf"), "rb+") as f:
        return f.read()


@pytest.fixture
def template_with_radiobutton_stream(pdf_samples):
    with open(
        os.path.join(pdf_samples, "sample_template_with_radio_button.pdf"), "rb+"
    ) as f:
        return f.read()


@pytest.fixture
def image_samples():
    return os.path.join(os.path.dirname(__file__), "..", "image_samples")


@pytest.fixture
def font_samples():
    return os.path.join(os.path.dirname(__file__), "..", "font_samples")


@pytest.fixture
def sample_font_stream(font_samples):
    with open(os.path.join(font_samples, "LiberationSerif-BoldItalic.ttf"), "rb+") as f:
        return f.read()


@pytest.fixture
def data_dict():
    return {
        "test": "test_1",
        "check": True,
        "test_2": "test_2",
        "check_2": False,
        "test_3": "test_3",
        "check_3": True,
    }


@pytest.fixture
def sejda_template(pdf_samples):
    with open(os.path.join(pdf_samples, "sample_template_sejda.pdf"), "rb+") as f:
        return f.read()


@pytest.fixture
def sejda_template_complex(pdf_samples):
    with open(
        os.path.join(pdf_samples, "paragraph", "sample_template_sejda_complex.pdf"),
        "rb+",
    ) as f:
        return f.read()


@pytest.fixture
def sample_template_with_font_colors(pdf_samples):
    with open(
        os.path.join(pdf_samples, "sample_template_with_font_colors.pdf"), "rb+"
    ) as f:
        return f.read()


@pytest.fixture
def sample_template_with_complex_fonts(pdf_samples):
    with open(
        os.path.join(pdf_samples, "sample_template_with_complex_fonts.pdf"), "rb+"
    ) as f:
        return f.read()


@pytest.fixture
def sample_template_paragraph_complex(pdf_samples):
    with open(
        os.path.join(pdf_samples, "paragraph", "sample_template_paragraph_complex.pdf"),
        "rb+",
    ) as f:
        return f.read()


@pytest.fixture
def sample_template_with_paragraph_max_length(pdf_samples):
    with open(
        os.path.join(
            pdf_samples, "paragraph", "sample_template_with_paragraph_max_length.pdf"
        ),
        "rb+",
    ) as f:
        return f.read()


@pytest.fixture
def sample_template_with_max_length_text_field(pdf_samples):
    with open(
        os.path.join(pdf_samples, "sample_template_with_max_length_text_field.pdf"),
        "rb+",
    ) as f:
        return f.read()


@pytest.fixture
def sample_template_with_comb_text_field(pdf_samples):
    with open(
        os.path.join(pdf_samples, "sample_template_with_comb_text_field.pdf"), "rb+"
    ) as f:
        return f.read()


@pytest.fixture
def sample_template_with_comb_text_field_right_aligned(pdf_samples):
    with open(
        os.path.join(
            pdf_samples, "sample_template_with_comb_text_field_right_aligned.pdf"
        ),
        "rb+",
    ) as f:
        return f.read()


@pytest.fixture
def sample_template_with_right_aligned_text_field(pdf_samples):
    with open(
        os.path.join(pdf_samples, "sample_template_with_right_aligned_text_field.pdf"),
        "rb+",
    ) as f:
        return f.read()


@pytest.fixture
def sample_template_with_dropdown(pdf_samples):
    with open(
        os.path.join(pdf_samples, "dropdown", "sample_template_with_dropdown.pdf"),
        "rb+",
    ) as f:
        return f.read()


@pytest.fixture
def sample_template_with_image_field(pdf_samples):
    with open(
        os.path.join(pdf_samples, "sample_template_with_image_field.pdf"), "rb+"
    ) as f:
        return f.read()


@pytest.fixture
def sample_template_with_full_key(pdf_samples):
    with open(
        os.path.join(pdf_samples, "sample_template_with_full_key.pdf"), "rb+"
    ) as f:
        return f.read()


@pytest.fixture
def dropdown_alignment(pdf_samples):
    with open(
        os.path.join(pdf_samples, "dropdown", "dropdown_alignment.pdf"),
        "rb+",
    ) as f:
        return f.read()


@pytest.fixture
def dropdown_alignment_sejda(pdf_samples):
    with open(
        os.path.join(pdf_samples, "dropdown", "dropdown_alignment_sejda.pdf"),
        "rb+",
    ) as f:
        return f.read()


@pytest.fixture
def sejda_data():
    return {
        "date": "01-01",
        "year": "21",
        "buyer_name": "John Doe",
        "buyer_address": "1 N Main St, Chicago, IL 60000",
        "seller_name": "Jack Smith",
        "seller_address": "2 S Main St, Chicago, IL 60000",
        "make": "AK",
        "model": "47",
        "caliber": "7.62-x39mm",
        "serial_number": "111111",
        "purchase_option": 0,
        "date_of_this_bill": True,
        "at_future_date": True,
        "other": True,
        "other_reason": "NO REASONS",
        "payment_amount": "400",
        "future_date": "01-01",
        "future_year": "22",
        "exchange_for": "Food",
        "buyer_name_printed": "John Doe",
        "seller_name_printed": "Jack Smith",
        "buyer_signed_date": "2021-01-01",
        "seller_signed_date": "2021-01-01",
        "buyer_dl_number": "D000-4609-0001",
        "seller_dl_number": "S530-4209-0001",
        "buyer_dl_state": "IL",
        "seller_dl_state": "IL",
    }


@pytest.fixture
def sejda_complex_data():
    return {
        "checkbox": True,
        "radio": 0,
        "dropdown_font_auto_left": 0,
        "dropdown_font_auto_center": 1,
        "dropdown_font_auto_right": 2,
        "dropdown_font_ten_left": 0,
        "dropdown_font_ten_center": 1,
        "dropdown_font_ten_right": 2,
        "paragraph_font_auto_left": "paragraph_font_auto_left",
        "paragraph_font_auto_center": "paragraph_font_auto_center",
        "paragraph_font_auto_right": "paragraph_font_auto_right",
        "paragraph_font_ten_left": "paragraph_font_ten_left",
        "paragraph_font_ten_center": "paragraph_font_ten_center",
        "paragraph_font_ten_right": "paragraph_font_ten_right",
        "text__font_auto_left": "test text left",
        "text_font_auto_center": "test text center",
        "text_font_auto_right": "test text right",
        "text_font_ten_left": "text_font_ten_left",
        "text_font_ten_center": "text_font_ten_center",
        "text_font_ten_right": "text_font_ten_right",
    }


@pytest.fixture
def max_length_expected_directory():
    return os.path.join(
        os.path.dirname(__file__),
        "..",
        "pdf_samples",
        "max_length_text_field_related",
    )
