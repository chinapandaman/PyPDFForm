# -*- coding: utf-8 -*-

import json
import os
import platform
import re
import runpy
import shutil
import tempfile
import tomllib
from importlib import metadata

import pikepdf
import pytest
from packaging.requirements import Requirement
from packaging.utils import canonicalize_name
from PIL import features

from tests.support import checks
from tests.support.snapshots import OWNED, ExpectPdf

# sample paths, template streams, and data, shared by every suite
pytest_plugins = ["tests.support.samples"]

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIXTURE_ENVIRONMENT_PATH = os.path.join(ROOT, "pdf_samples", "fixture_environment.json")
in_place_writes = pytest.StashKey[object]()
shared_expected_pdfs = pytest.StashKey[dict]()


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


class ExpectedPdfOwners:
    # the tests that own each expected PDF, collected from the reports, which
    # the controller of a parallel run receives from every worker

    def __init__(self):
        super().__init__()
        self.owners = {}

    def pytest_runtest_logreport(self, report):
        for name, value in report.user_properties:
            if name == OWNED:
                self.owners.setdefault(value, set()).add(report.nodeid)


class InPlaceWrites:
    # regenerating in place runs one test at a time, so the first test that
    # writes an expected PDF owns it; a second writer's PDF isn't written, and
    # the expected PDF goes back to what it was before the run. A second owner
    # that doesn't write, such as a timestamped one whose comparison passes, is
    # only found when the session ends, which restores the PDF then.

    def __init__(self):
        super().__init__()
        self.backup_dir = tempfile.mkdtemp(prefix="expected_pdf_backups_")
        self.owners = {}
        # the backup of each written expected PDF, or None if it didn't exist
        self.backups = {}
        self.restored = set()

    @property
    def kept(self):
        # whether any expected PDF this run wrote is still its version
        return any(path not in self.restored for path in self.backups)

    def write(self, path, stream, nodeid):
        if self.owners.setdefault(path, nodeid) != nodeid:
            self.restore(path)
            return
        if path not in self.backups:
            backup = None
            if os.path.exists(path):
                backup = os.path.join(self.backup_dir, f"{len(self.backups)}.pdf")
                shutil.copyfile(path, backup)
            self.backups[path] = backup

        with open(path, "wb") as f:
            f.write(stream)
        self.restored.discard(path)

    def restore(self, path):
        if path not in self.backups:
            # not written in this run
            return
        backup = self.backups[path]
        if backup is not None:
            shutil.copyfile(backup, path)
        elif os.path.exists(path):
            os.remove(path)
        self.restored.add(path)

    def close(self):
        shutil.rmtree(self.backup_dir, ignore_errors=True)


def pytest_configure(config):
    config.pluginmanager.register(ExpectedPdfOwners(), "expected_pdf_owners")
    if _regenerating_in_place(config) and _zlib_info()["zlib_backend"] != "zlib":
        msg = (
            "Expected PDFs must be regenerated with standard zlib, but this "
            "Python uses zlib-ng. Regenerate them in the development container."
        )
        raise pytest.UsageError(msg)
    # pytest-xdist sets --dist when it runs the tests in workers
    if _regenerating_in_place(config) and getattr(config.option, "dist", "no") != "no":
        msg = (
            "Expected PDFs must be regenerated in place one test at a time, "
            "because some tests read expected PDFs that other tests write. "
            "Run without -n."
        )
        raise pytest.UsageError(msg)
    if _regenerating_in_place(config):
        config.stash[in_place_writes] = InPlaceWrites()


def pytest_unconfigure(config):
    writes = config.stash.get(in_place_writes, None)
    if isinstance(writes, InPlaceWrites):
        writes.close()


def pytest_addoption(parser):
    parser.addoption("--regenerate", action="store", default="0")
    parser.addoption("--regenerate-dir", action="store", default="")


@pytest.hookimpl(tryfirst=True)
def pytest_collection_modifyitems(items):
    # before -m selects tests, mark every test that compares with an expected PDF
    for item in items:
        if "expect_pdf" in getattr(item, "fixturenames", ()):
            item.add_marker(pytest.mark.snapshot)


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
    config = session.config
    # a pytest-xdist worker only sees its own tests, and the controller all of them
    if not hasattr(config, "workerinput"):
        owners = config.pluginmanager.get_plugin("expected_pdf_owners").owners
        shared = {
            path: sorted(nodeids)
            for path, nodeids in sorted(owners.items())
            if len(nodeids) > 1
        }
        if shared:
            # the last writer would win, so regenerated PDFs couldn't be trusted
            config.stash[shared_expected_pdfs] = shared
            session.exitstatus = pytest.ExitCode.USAGE_ERROR

    writes = config.stash.get(in_place_writes, None)
    if isinstance(writes, InPlaceWrites):
        # also the PDFs whose second owner didn't write them
        for path in config.stash.get(shared_expected_pdfs, {}):
            writes.restore(os.path.abspath(os.path.join(ROOT, path)))

    # record the environment of the latest in-place regeneration, unless every
    # expected PDF it wrote was restored
    if isinstance(writes, InPlaceWrites) and writes.kept:
        with open(FIXTURE_ENVIRONMENT_PATH, "w", encoding="utf-8", newline="\n") as f:
            json.dump(fixture_environment(), f, indent=2)
            f.write("\n")


def pytest_terminal_summary(terminalreporter, config):
    shared = config.stash.get(shared_expected_pdfs, {})
    if shared:
        terminalreporter.section("expected PDFs owned by more than one test", red=True)
        for path, nodeids in shared.items():
            terminalreporter.line(f"{path}: {', '.join(nodeids)}")
        if isinstance(config.stash.get(in_place_writes, None), InPlaceWrites):
            terminalreporter.line(
                "Regenerating in place left these expected PDFs as they were."
            )
        terminalreporter.line(
            "Each expected PDF has one owner. The other tests compare with it "
            "using expect_pdf(stream, same_as=path)."
        )


def _write_artifact(path, stream):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as f:
        f.write(stream)


@pytest.fixture(scope="session")
def standard_zlib():
    # expected PDFs hold the bytes that standard zlib produces
    return _zlib_info()["zlib_backend"] == "zlib"


@pytest.fixture
def expect_pdf(request, standard_zlib):
    # expect_pdf(stream, path) compares with the expected PDF this test owns,
    # and expect_pdf(stream, same_as=path) with one that another test owns
    expect = ExpectPdf(request.node, ROOT, standard_zlib)
    yield expect

    if request.config.getoption("--regenerate") != "1":
        return
    regenerate_dir = request.config.getoption("--regenerate-dir")
    if not regenerate_dir:
        writes = request.config.stash[in_place_writes]
        assert isinstance(writes, InPlaceWrites)
        for path, stream in expect.outputs.items():
            writes.write(path, stream, request.node.nodeid)
        return

    for path, stream in expect.outputs.items():
        # the same relative path under regenerate_dir, instead of overwriting
        # the expected PDF
        _write_artifact(
            os.path.join(regenerate_dir, os.path.relpath(path, ROOT)), stream
        )
    test_name = re.sub(r"[^\w.-]+", "_", request.node.nodeid)
    for path, stream in expect.mismatches.items():
        # named <expected PDF>.<test>.pdf, so that a comparison run shows it
        # without overwriting the version of the test that owns the PDF
        _write_artifact(
            os.path.join(
                regenerate_dir, f"{os.path.relpath(path, ROOT)}.{test_name}.pdf"
            ),
            stream,
        )


@pytest.fixture
def assert_page_ownership():
    return checks.assert_page_ownership


@pytest.fixture
def assert_catalog_fields():
    return checks.assert_catalog_fields


@pytest.fixture
def assert_round_trip():
    return checks.assert_round_trip


@pytest.fixture
def assert_widgets_match_output():
    return checks.assert_widgets_match_output


@pytest.fixture
def assert_valid_appearances():
    return checks.assert_valid_appearances


@pytest.fixture
def assert_annotations_preserved():
    return checks.assert_annotations_preserved
