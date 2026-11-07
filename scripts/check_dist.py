# -*- coding: utf-8 -*-
"""
Checks a built PyPDFForm sdist and wheel before they are published.

The distribution directory must hold exactly one sdist and one wheel. Hidden
files, such as the .gitignore written by `uv build`, are ignored. The script
checks that:

- The file names, the sdist and wheel metadata, the installed package, and
  the release tag, if given, all report the same version.
- The wheel contains exactly the PyPDFForm files tracked at HEAD of this
  checkout, byte for byte, plus its .dist-info metadata. The sdist contains
  the same package files and README.md, LICENSE, and pyproject.toml, byte for
  byte, plus its generated metadata. The only other files it may contain are
  tracked top-level tests/test*.py files, which setuptools adds by default.
- For each requested Python, the wheel installs into new virtual environments
  in a temporary directory outside this checkout, once without extras and
  once with the cli extra. In each, PyPDFForm must import from the
  environment's site-packages with the same files as the wheel, and every
  module must import, except CLI modules when the cli extra is not installed.
  A form must be created, filled, written, and reopened with the filled
  values. The pypdfform command must print installation guidance without the
  cli extra, and create, fill, and inspect a form with it.

The installed package is checked by a copy of this script run with
`python -I` from the temporary directory, so neither this checkout nor
PYTHONPATH can supply the imported PyPDFForm. Any failed check exits with
status 1.

Requires git and uv.

Usage:
    python scripts/check_dist.py <dist_dir> [--tag vX.Y.Z] [--python VERSION]...
"""

import argparse
import hashlib
import importlib
import importlib.metadata
import importlib.util
import json
import os
import platform
import re
import shutil
import subprocess
import sys
import sysconfig
import tarfile
import tempfile
import zipfile
import zlib
from email.parser import HeaderParser
from pathlib import Path
from typing import NoReturn

SOURCE_ROOT = Path(__file__).resolve().parent.parent
PACKAGE = "PyPDFForm"
DIST_NAME = "pypdfform"
PROBE = "probe"
SDIST_PATTERN = re.compile(r"pypdfform-([^-/]+)\.tar\.gz")
WHEEL_PATTERN = re.compile(r"pypdfform-([^-/]+)-py3-none-any\.whl")
SDIST_TRACKED = {"LICENSE", "README.md", "pyproject.toml"}
SDIST_GENERATED = {"PKG-INFO", "setup.cfg"}
SDIST_EGG_INFO = f"{PACKAGE}.egg-info/"
SDIST_TESTS = re.compile(r"tests/test[^/]*\.py")
WHEEL_METADATA = {"METADATA", "RECORD", "WHEEL", "entry_points.txt"}
CLI_EXTRA = "cli"
CLI_DEPENDENCIES = ("jsonschema", "typer", "yaml")
CLI_HINT = "PyPDFForm CLI dependencies are not installed."
FIELDS = {
    "text": [{"name": "smoke_text", "page_number": 1, "x": 100, "y": 600}],
    "check": [{"name": "smoke_check", "page_number": 1, "x": 100, "y": 500}],
    "dropdown": [
        {
            "name": "smoke_choice",
            "page_number": 1,
            "x": 100,
            "y": 400,
            "options": ["a", "b", "c"],
        }
    ],
}
VALUES = {"smoke_text": "hello", "smoke_check": True, "smoke_choice": 2}


class CheckError(Exception):
    """A failed check, reported without a traceback."""


def fail(message) -> NoReturn:
    """Stops the check with message."""
    raise CheckError(message)


def clean_env():
    """Returns the environment without variables that change Python's imports."""
    return {
        key: value
        for key, value in os.environ.items()
        if not key.startswith("PYTHON") and key != "VIRTUAL_ENV"
    }


def run(args, cwd=None, check=True):
    """Runs a command in a clean environment, failing on a nonzero exit if check."""
    args = [str(each) for each in args]
    try:
        result = subprocess.run(
            args,
            cwd=cwd,
            env=clean_env(),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )
    except OSError as exc:
        fail(f"Unable to run {args[0]}: {exc}")
    if check and result.returncode != 0:
        fail(
            f"`{' '.join(args)}` exited with status {result.returncode}.\n"
            f"{result.stdout}{result.stderr}".rstrip()
        )
    return result


def sha256(path):
    """Returns the SHA-256 hex digest of a file."""
    with open(path, "rb") as f:
        return hashlib.file_digest(f, "sha256").hexdigest()


def blob_id(data):
    """Returns the git blob ID of data."""
    return hashlib.sha1(b"blob %d\0" % len(data) + data).hexdigest()


def tracked_files():
    """Returns the commit at HEAD and its tracked files mapped to blob IDs."""
    head = run(["git", "-C", SOURCE_ROOT, "rev-parse", "--verify", "HEAD^{commit}"])
    commit = head.stdout.strip()
    listing = run(["git", "-C", SOURCE_ROOT, "ls-tree", "-r", "-z", commit]).stdout

    files = {}
    for entry in filter(None, listing.split("\0")):
        info, path = entry.split("\t", 1)
        _, kind, blob = info.split()
        if kind == "blob":
            files[path] = blob
    return commit, files


def find_dists(dist_dir):
    """Returns the sdist and wheel in dist_dir and the version they share."""
    if not dist_dir.is_dir():
        fail(f"{dist_dir} is not a directory.")

    files = sorted(each for each in dist_dir.iterdir() if not each.name.startswith("."))
    sdists = [each for each in files if SDIST_PATTERN.fullmatch(each.name)]
    wheels = [each for each in files if WHEEL_PATTERN.fullmatch(each.name)]
    if len(files) != 2 or len(sdists) != 1 or len(wheels) != 1:
        found = ", ".join(each.name for each in files) or "nothing"
        fail(f"{dist_dir} must hold exactly one sdist and one wheel, found: {found}.")

    sdist, wheel = sdists[0], wheels[0]
    sdist_match = SDIST_PATTERN.fullmatch(sdist.name)
    wheel_match = WHEEL_PATTERN.fullmatch(wheel.name)
    if sdist_match is None or wheel_match is None:
        fail("Unable to read the version from the distribution file names.")
    if sdist_match.group(1) != wheel_match.group(1):
        fail(f"{sdist.name} and {wheel.name} have different versions.")
    return sdist, wheel, wheel_match.group(1)


def check_metadata(label, data, version):
    """Checks the name and version in core metadata."""
    headers = HeaderParser().parsestr(data.decode("utf-8"))
    if headers["Name"] != PACKAGE or headers["Version"] != version:
        fail(
            f"{label} names {headers['Name']} {headers['Version']}, "
            f"not {PACKAGE} {version}."
        )


def compare_files(label, files, required, tracked, unexpected):
    """Checks that files match their tracked blobs and include every required file."""
    problems = [f"unexpected file {each}" for each in sorted(unexpected)]
    for path, data in sorted(files.items()):
        if path not in tracked:
            problems.append(f"{path} is not tracked at HEAD")
        elif blob_id(data) != tracked[path]:
            problems.append(f"{path} differs from HEAD")
    problems.extend(f"missing {each}" for each in sorted(required - files.keys()))
    if problems:
        fail(f"The {label} does not match HEAD:\n  " + "\n  ".join(problems))


def package_files(tracked):
    """Returns the tracked files of the PyPDFForm package."""
    return {each for each in tracked if each.startswith(f"{PACKAGE}/")}


def check_sdist(sdist, version, tracked):
    """Checks the files and metadata in the sdist, returning its file count."""
    root = f"{DIST_NAME}-{version}/"
    files = {}
    generated = {}
    unexpected = []
    with tarfile.open(sdist, "r:gz") as archive:
        for member in archive.getmembers():
            if member.isdir():
                continue
            name = member.name.removeprefix(root)
            content = archive.extractfile(member) if member.isfile() else None
            if name == member.name or content is None:
                unexpected.append(member.name)
                continue

            if name in SDIST_GENERATED or (
                name.startswith(SDIST_EGG_INFO)
                and "/" not in name.removeprefix(SDIST_EGG_INFO)
            ):
                target = generated
            elif (
                name.startswith(f"{PACKAGE}/")
                or name in SDIST_TRACKED
                or SDIST_TESTS.fullmatch(name)
            ):
                target = files
            else:
                unexpected.append(name)
                continue
            if name in target:
                fail(f"The sdist contains {name} more than once.")
            target[name] = content.read()

    compare_files(
        "sdist", files, package_files(tracked) | SDIST_TRACKED, tracked, unexpected
    )
    if "PKG-INFO" not in generated:
        fail("The sdist has no PKG-INFO.")
    check_metadata("The sdist's PKG-INFO", generated["PKG-INFO"], version)
    return len(files) + len(generated)


def check_wheel(wheel, version, tracked):
    """Checks the files and metadata in the wheel, returning its package files."""
    dist_info = f"{DIST_NAME}-{version}.dist-info/"
    files = {}
    metadata = {}
    unexpected = []
    with zipfile.ZipFile(wheel) as archive:
        for member in archive.infolist():
            if member.is_dir():
                continue
            name = member.filename
            if name.startswith(f"{PACKAGE}/"):
                target = files
            elif name.startswith(dist_info):
                target = metadata
                name = name.removeprefix(dist_info)
            else:
                unexpected.append(name)
                continue
            if name in target:
                fail(f"The wheel contains {member.filename} more than once.")
            target[name] = archive.read(member)

    compare_files("wheel", files, package_files(tracked), tracked, unexpected)
    missing = WHEEL_METADATA - metadata.keys()
    if missing:
        fail(f"The wheel is missing {', '.join(sorted(missing))} in {dist_info}.")
    check_metadata("The wheel's METADATA", metadata["METADATA"], version)
    return files


def check_installed(package_dir, wheel_files):
    """Checks that the installed package files are exactly the wheel's."""
    installed = {}
    for path in package_dir.rglob("*"):
        relative = path.relative_to(package_dir)
        if path.is_file() and "__pycache__" not in relative.parts:
            installed[f"{PACKAGE}/{relative.as_posix()}"] = path.read_bytes()

    if installed != wheel_files:
        extra = sorted(installed.keys() - wheel_files.keys())
        missing = sorted(wheel_files.keys() - installed.keys())
        changed = sorted(
            each
            for each in installed.keys() & wheel_files.keys()
            if installed[each] != wheel_files[each]
        )
        fail(
            f"The installed package at {package_dir} differs from the wheel: "
            f"extra {extra}, missing {missing}, changed {changed}."
        )


def executable(env_dir, name):
    """Returns the path of an executable in a virtual environment."""
    if os.name == "nt":
        return env_dir / "Scripts" / f"{name}.exe"
    return env_dir / "bin" / name


def check_cli(command, version, out, with_cli):
    """Checks the pypdfform command installed with or without the cli extra."""
    if not command.is_file():
        fail(f"The pypdfform command was not installed at {command}.")

    result = run([command, "--version"], cwd=out, check=False)
    if not with_cli:
        if result.returncode != 1 or CLI_HINT not in result.stderr:
            fail(
                "Without the cli extra, `pypdfform --version` should exit 1 with "
                f"installation guidance, but exited {result.returncode}: "
                f"{result.stdout}{result.stderr}".rstrip()
            )
        return

    if result.returncode != 0 or result.stdout.strip() != f"v{version}":
        fail(
            f"`pypdfform --version` should print v{version}, but exited "
            f"{result.returncode}: {result.stdout}{result.stderr}".rstrip()
        )

    (out / "fields.json").write_text(json.dumps(FIELDS), encoding="utf-8")
    (out / "values.json").write_text(json.dumps(VALUES), encoding="utf-8")
    run([command, "create", "blank", "-o", "blank.pdf"], cwd=out)
    run(
        [command, "create", "field", "blank.pdf", "-f", "fields.json"]
        + ["-o", "form.pdf"],
        cwd=out,
    )
    run([command, "fill", "form.pdf", "-f", "values.json", "-o", "filled.pdf"], cwd=out)
    output = run([command, "inspect", "data", "filled.pdf"], cwd=out).stdout
    try:
        data = json.loads(output)
    except ValueError:
        data = output
    if data != VALUES:
        fail(f"`pypdfform inspect data` printed {data!r}, not {VALUES!r}.")


def check_variant(python, extra, wheel, version, work, wheel_files):
    """Installs the wheel with extra into a new environment and checks it."""
    env_dir = Path(tempfile.mkdtemp(prefix="venv-", dir=work))
    out = Path(tempfile.mkdtemp(prefix="out-", dir=work))
    run(["uv", "venv", "--quiet", "--python", python, env_dir], cwd=work)
    env_python = executable(env_dir, "python")
    requirement = f"{wheel}[{extra}]" if extra else wheel
    run(
        ["uv", "pip", "install", "--quiet", "--python", env_python, requirement],
        cwd=work,
    )

    probe_args = [env_python, "-I", work / "check_dist_probe.py", PROBE]
    probe_args += ["--version", version, "--source", SOURCE_ROOT, "--out", out]
    if extra:
        probe_args.append("--cli")
    lines = run(probe_args, cwd=out).stdout.strip().splitlines()
    try:
        report = json.loads(lines[-1])
    except (IndexError, ValueError):
        fail(f"The probe printed no report: {lines}")

    package_dir = Path(report["package_dir"])
    if not package_dir.is_relative_to(env_dir.resolve()):
        fail(f"PyPDFForm was imported from {package_dir}, outside {env_dir}.")
    check_installed(package_dir, wheel_files)
    check_cli(executable(env_dir, "pypdfform"), version, out, bool(extra))
    return (
        f"passed on Python {report['python']}; imported {report['imported']} "
        f"modules from {package_dir}"
    )


def check_install(python, wheel, version, work, wheel_files):
    """Checks the wheel installed for python without extras and with the cli extra."""
    for extra in (None, CLI_EXTRA):
        label = f"--python {python}, {f'{extra} extra' if extra else 'no extras'}"
        try:
            result = check_variant(python, extra, wheel, version, work, wheel_files)
        except CheckError as exc:
            fail(f"{label}: {exc}")
        print(f"{label}: {result}")


def probe(argv):
    """Checks the PyPDFForm installed for the running Python and prints a report."""
    parser = argparse.ArgumentParser(prog=f"check_dist.py {PROBE}")
    parser.add_argument("--version", required=True)
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--cli", action="store_true")
    args = parser.parse_args(argv)

    import PyPDFForm

    module_file = getattr(PyPDFForm, "__file__", None)
    if not module_file:
        fail("PyPDFForm was not imported from a file.")
    package_dir = Path(module_file).resolve().parent
    site_packages = Path(sysconfig.get_paths()["purelib"]).resolve()
    if package_dir != site_packages / PACKAGE or package_dir.is_relative_to(
        args.source.resolve()
    ):
        fail(f"PyPDFForm was imported from {package_dir}, not {site_packages}.")

    installed = importlib.metadata.version(PACKAGE)
    if PyPDFForm.__version__ != args.version or installed != args.version:
        fail(
            f"Expected version {args.version}, but __version__ is "
            f"{PyPDFForm.__version__} and the installed metadata says {installed}."
        )

    missing = [each for each in CLI_DEPENDENCIES if not importlib.util.find_spec(each)]
    if args.cli and missing:
        fail(f"The cli extra did not install {', '.join(missing)}.")
    if not args.cli and not missing:
        fail("Without extras, every CLI dependency is already installed.")

    modules = sorted(
        ".".join(
            (PACKAGE, *path.relative_to(package_dir).with_suffix("").parts)
        ).removesuffix(".__init__")
        for path in package_dir.rglob("*.py")
    )
    imported = 0
    for module in modules:
        try:
            importlib.import_module(module)
        except ModuleNotFoundError as exc:
            if (
                args.cli
                or exc.name not in CLI_DEPENDENCIES
                or not module.startswith(f"{PACKAGE}.cli.")
            ):
                raise
        else:
            imported += 1
    for name in PyPDFForm.__all__:
        if not hasattr(PyPDFForm, name):
            fail(f"PyPDFForm.{name} is listed in __all__ but missing.")

    from PyPDFForm import BlankPage, Fields, PdfWrapper, Widgets

    field_types = {
        "text": (Fields.TextField, Widgets.Text),
        "check": (Fields.CheckBoxField, Widgets.Checkbox),
        "dropdown": (Fields.DropdownField, Widgets.Dropdown),
    }
    fields = [
        field_types[kind][0](**spec) for kind, specs in FIELDS.items() for spec in specs
    ]
    form = PdfWrapper(BlankPage()).bulk_create_fields(fields)
    if set(form.data) != set(VALUES):
        fail(f"The created form has fields {sorted(form.data)}, not {sorted(VALUES)}.")

    path = args.out / "library.pdf"
    form.fill(VALUES).write(str(path))
    reopened = PdfWrapper(str(path))
    if reopened.data != VALUES:
        fail(f"The reopened form has data {reopened.data!r}, not {VALUES!r}.")
    for kind, specs in FIELDS.items():
        for spec in specs:
            widget = reopened.widgets.get(spec["name"])
            if not isinstance(widget, field_types[kind][1]):
                fail(f"The reopened {spec['name']} field is {type(widget).__name__}.")

    print(
        json.dumps(
            {
                "package_dir": str(package_dir),
                "python": platform.python_version(),
                "imported": imported,
            }
        )
    )


def check(argv):
    """Checks the distribution files in a directory."""
    parser = argparse.ArgumentParser(
        prog="check_dist.py",
        description="Check a built PyPDFForm sdist and wheel before publishing.",
    )
    parser.add_argument(
        "dist_dir", type=Path, help="Directory with the sdist and wheel."
    )
    parser.add_argument("--tag", help="Release tag the version must match, as vX.Y.Z.")
    parser.add_argument(
        "--python",
        action="append",
        dest="pythons",
        help="Python version or interpreter to install the wheel with. Repeat to "
        "check several. Defaults to the Python running this script.",
    )
    args = parser.parse_args(argv)

    commit, tracked = tracked_files()
    sdist, wheel, version = find_dists(args.dist_dir.resolve())
    print(f"Commit: {commit}")
    print(f"Version: {version}")
    for path in (sdist, wheel):
        print(f"{path.name}: sha256 {sha256(path)}")
    if args.tag is not None:
        if args.tag != f"v{version}":
            fail(f"Release tag {args.tag} does not match version {version}.")
        print(f"Release tag: {args.tag}")

    try:
        count = check_sdist(sdist, version, tracked)
        print(f"{sdist.name}: {count} files match HEAD and the allowed generated files")
        wheel_files = check_wheel(wheel, version, tracked)
        print(f"{wheel.name}: {len(wheel_files)} package files match HEAD")
    except (
        EOFError,
        OSError,
        UnicodeDecodeError,
        tarfile.TarError,
        zipfile.BadZipFile,
        zlib.error,
    ) as exc:
        fail(f"Unable to read the distribution files: {exc!r}")

    with tempfile.TemporaryDirectory(prefix="pypdfform-dist-") as tmp:
        work = Path(tmp).resolve()
        if work.is_relative_to(SOURCE_ROOT):
            fail(f"The temporary directory {work} is inside {SOURCE_ROOT}.")
        shutil.copyfile(__file__, work / "check_dist_probe.py")
        for python in args.pythons or [sys.executable]:
            check_install(python, wheel, version, work, wheel_files)

    print(f"All distribution checks passed for {version} at {commit}.")


def main():
    """Runs the check or the probe, exiting with status 1 on a failed check."""
    try:
        if sys.argv[1:2] == [PROBE]:
            probe(sys.argv[2:])
        else:
            check(sys.argv[1:])
    except CheckError as exc:
        print(f"Distribution check failed: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
