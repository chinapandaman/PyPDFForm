# Testing

PyPDFForm uses [pytest](https://pytest.org/) for testing and [coverage.py](https://coverage.readthedocs.io/)
for measuring test coverage. To run the tests, execute:

=== "Virtual Environment"
    ```shell
    coverage erase && coverage run -m pytest -n auto && coverage combine && coverage report --fail-under=100
    ```
=== "Development Container"
    ```shell
    test
    ```

The tests run in parallel with [pytest-xdist](https://pytest-xdist.readthedocs.io/): `-n auto` starts one worker per CPU. Coverage measures each worker in its own data file, and `coverage combine` merges them before the report. `coverage erase` first removes data left by an earlier run, which would otherwise be merged in. Without `-n`, pytest runs the tests one at a time, which suits running a single test or using a debugger such as `pudb` or `--pdb`.

Runs start the tests marked `@pytest.mark.slow` first, so that a parallel run doesn't wait for a slow test that started last. Mark a test that takes several seconds, such as `test_bulk_create_fields_stress_max`. Regenerating expected PDFs in place keeps the order the tests are collected in.

## Adding tests

Add only the tests needed to cover the changed behavior and maintain 100% coverage. Follow the [placement rule](#where-tests-go): extend the module it names, or create that module if it doesn't exist yet. Consult the maintainer before creating a new directory.

Leave expected PDF sample regeneration and visual regression comparison to the maintainer unless they explicitly delegate these tasks.

### Where tests go

The tests are in these directories under `tests/`:

| Directory | Tests |
| --- | --- |
| `doc_examples/lib/`, `doc_examples/cli/` | The snippets of the User Guide |
| `scenario/` | Reproductions of issues, and tests of PDFs made by third-party tools or found online |
| `snapshots/` | Library tests that only compare with an expected PDF |
| `behavior/` | Other library tests |
| `behavior/field_tree/` | Library tests of field hierarchies, such as inherited, malformed, and cyclic ones, that aren't tied to one operation |
| `cli/` | Tests of CLI-only behavior, such as errors and the entry point |

To place a test:

1. A test of a User Guide snippet goes in `doc_examples/lib/` or `doc_examples/cli/`, in the module named after the page.
2. A test that reproduces an issue, or uses a PDF made by a third-party tool or found online, goes in `scenario/`.
3. Any other test that compares with an expected PDF goes in `snapshots/`. Other library tests go in `behavior/`, and tests of CLI-only behavior go in `cli/`.
4. Modules are named after User Guide pages, such as `test_fill.py` and `test_style.py`. A module longer than about 800 lines is split by operation, the way `behavior/` splits the Utils page into `test_pages.py`, `test_merge.py`, and `test_version.py`. Tests of PDF field structure that isn't tied to one operation go in `behavior/field_tree/`.

A doc example or scenario test can compare with an expected PDF and also make other assertions, since it mirrors one snippet or one issue. A library test that needs both is two tests with the same name, one in `snapshots/` that only compares and one in `behavior/` that only asserts:

```python
# tests/snapshots/test_prepare.py
def test_create_text_multiline(template_stream, expect_pdf):
    obj = PdfWrapper(template_stream).bulk_create_fields(
        [Fields.TextField(name="foo", page_number=1, x=100, y=100, multiline=True)]
    )

    expect_pdf(obj.read())


# tests/behavior/test_prepare.py
def test_create_text_multiline(template_stream):
    obj = PdfWrapper(template_stream).bulk_create_fields(
        [Fields.TextField(name="foo", page_number=1, x=100, y=100, multiline=True)]
    )

    assert obj.schema["properties"]["foo"]["type"] == "string"
```

Test modules contain only tests and their parametrize tables, and don't import each other. Helpers and fixtures are in `tests/support/`:

* `builders.py` builds PDFs for tests, such as nested, inherited, and cyclic field trees, fields with null entries, and forms with actions.
* `checks.py` reads and checks PDFs. It implements the [shared assertions](#shared-assertions).
* `samples.py` has the fixtures for [sample directories](#sample-pdfs), template streams, and fill data. `tests/conftest.py` loads it for every test.
* `snapshots.py` implements [`expect_pdf`](#comparing-with-expected-pdfs).

### Shared assertions

An expected PDF only shows that the output hasn't changed, not that it is correct. `tests/conftest.py` has fixtures that check what a PDF contains instead. They are implemented in `tests/support/checks.py`, don't depend on an expected PDF, and behave the same on every platform:

| Fixture | Checks |
| --- | --- |
| `assert_page_ownership(stream)` | Every page is in the page tree, every annotation belongs to the page that lists it, and every widget of a listed field is on a page. |
| `assert_catalog_fields(stream, names)` | The AcroForm lists exactly the fields with these fully qualified names, and their widgets are exactly the widgets on the pages, each listed once. Fields without a widget, such as hidden fields, are listed by name only. |
| `assert_round_trip(pdf, data)` | The wrapper and its reopened output both read these values. |
| `assert_widgets_match_output(pdf)` | The wrapper has the same fields as its reopened output, with the same values and the same properties read from the PDF, such as geometry, flags, and tooltips. An unchecked checkbox matches whether it reads `False` or `None`. |
| `assert_valid_appearances(stream)` | Every `/AP` is a dictionary of appearance streams, and a widget with appearance states selects one of them or `/Off`. |
| `assert_annotations_preserved(before, after, changed)` | Every annotation has the same content on the same page in the same order, except the widgets of the `changed` fields. |

Use them when a change affects one of these properties. Not every PDF passes all of them. For example, `sample_template_sejda.pdf` lists fields whose widgets are on no page, so it fails `assert_page_ownership`.

### Sample PDFs

`pdf_samples` has two directories:

* `input/` has the PDFs that tests read, such as templates. The `pdf_samples` fixture is this directory, for example `os.path.join(pdf_samples, "sample_template.pdf")`.
* `expected/` has the expected PDFs, each named after the test that owns it: `expected/<directory under tests>/<module>/<test>.pdf`. For example, `tests/snapshots/test_fill.py::test_fill_sejda` owns `expected/snapshots/test_fill/test_fill_sejda.pdf`. A parametrized test adds its parameter ID, as in `<test>-<ID>.pdf`. The ID keeps lowercase letters, digits, `_`, `.`, and `-`, and writes any other character as `~` and its UTF-8 bytes in hexadecimal, so `ids=["A", "a b"]` gives `<test>-~41.pdf` and `<test>-a~20b.pdf`. That way, different IDs get different files, also on filesystems that ignore case. The `expected_pdfs` fixture is this directory.

A test that reads another test's expected PDF, for example to inspect a filled form, joins its path to `expected_pdfs`. Add new inputs to `input/`. Expected PDFs are added by [regenerating](#expected-pdf-environment) them.

## Expected PDF environment

Most tests compare the PDF they generate with an expected PDF in `pdf_samples/expected/`, using the [`expect_pdf`](#comparing-with-expected-pdfs) fixture. The bytes of a PDF can depend on:

* The zlib library Python uses. Expected PDFs are generated with standard zlib. Python builds that use zlib-ng, such as Python 3.14 and later on Windows, compress some streams to different bytes. `expect_pdf` compares the bytes only with standard zlib.
* The installed versions of PyPDFForm's dependencies, and of the qpdf library pikepdf uses.

PyPDFForm doesn't pin its dependencies. Any version in its dependency ranges is supported, and with standard zlib the expected PDFs are the same on Linux, macOS, and Windows, for every supported Python version, and for both the newest and lowest dependency versions.

`pdf_samples/fixture_environment.json` records the environment the expected PDFs were last regenerated in. Regenerating them in place, for example with `make generate-new-pdf-samples` or `update` in the development container, rewrites this file, so commit it with the regenerated PDFs. Regenerating in place stops with an error when Python uses zlib-ng.

Regenerating expected PDFs in place runs one test at a time, because some tests read expected PDFs that other tests write. It stops with an error when pytest runs with `-n`. Regenerating them into another directory, as `make compare-pdf-diffs` does, runs in parallel. `make compare-pdf-diffs` fails when tests fail but no regenerated PDF differs from its expected PDF.

Each test run prints the current environment and any differences from the record at the top of its output, for example:

```
differs from pdf_samples/fixture_environment.json: pypdf 6.22.0 (recorded 6.21.4)
```

If byte comparisons fail without a code change, check these differences first. A newer dependency version that changes the bytes needs regenerated expected PDFs. To reproduce the recorded bytes, install the recorded versions into a separate virtual environment, for example `uv pip install pypdf==6.21.4`.

### Comparing with expected PDFs

A test compares its PDF with an expected PDF using the `expect_pdf` fixture, implemented in `tests/support/snapshots.py`:

```python
def test_fill_font_color(sample_template_with_font_colors, expect_pdf):
    obj = PdfWrapper(sample_template_with_font_colors).fill(...)

    expect_pdf(obj.read())
```

On every platform, the fixture checks that both PDFs have the same version, trailer, and objects, comparing each stream after decompressing it. It ignores each stream's `/Length` and the trailer's `/ID`. Python's zlib compresses some of the streams PyPDFForm writes, such as embedded fonts, drawn text and images, and created fields, so the fixture compares the bytes only with standard zlib.

The test owns the expected PDF [named after it](#sample-pdfs), here `pdf_samples/expected/snapshots/test_fill/test_fill_font_color.pdf`. Regenerating expected PDFs writes the test's PDF to that path, even when the comparison fails or the expected PDF doesn't exist yet. Each test owns at most one expected PDF, and each expected PDF has one owner. Other tests, and the owner's other outputs, compare with it using `same_as`, which never regenerates it:

```python
expected_path = os.path.join(
    expected_pdfs, "doc_examples", "lib", "test_fill", "test_fill_text_check.pdf"
)
expect_pdf(actual, same_as=expected_path)
```

When the comparison fails, regenerating expected PDFs into another directory writes the other test's PDF as `same_as/<test>/<expected PDF>`, so `make compare-pdf-diffs` shows it next to the expected PDF.

The README's example compares with `docs/pdfs/sample_filled.pdf`, which the documentation links to, so it passes that path: `expect_pdf(filled.read(), expected_path)`. Only an expected PDF in `docs/` takes a path.

If two tests own the same expected PDF, the run ends with exit status 4 and lists them, because the PDF written last would hide the other. Regenerating in place then leaves that expected PDF as it was, and also leaves `pdf_samples/fixture_environment.json` as it was if it wrote no other expected PDF. Paths that differ only in case count as the same, since some filesystems ignore case.

A run of the whole suite also checks that every file in `pdf_samples/expected/` has an owner whose path it matches exactly, including case. If one doesn't, for example because its test was renamed or removed, the run ends with exit status 4 and lists the file.

* The check runs only when no test failed and none was left out. So it doesn't run with paths other than `tests/`, or with `-k`, `-m`, `--deselect`, `--ignore`, `--lf`, or `--sw`.
* A skipped test, or a module skipped as a whole, still owns the expected PDFs named after it.
* A `test_Fill_sejda.pdf` left next to `test_fill_sejda.pdf` is reported. On a filesystem that ignores case, regenerating an expected PDF after renaming its test keeps the file's old case, so rename the file with `git mv`.
* A test whose expected PDF is missing fails, unless expected PDFs are being regenerated.

A PDF created from a blank page holds the time it was created. Pass `timestamped=True` for such a PDF. Its `/CreationDate` and `/ModDate` are then ignored, with standard zlib only the length of the bytes is compared, and it is regenerated only when the comparison fails.

The CLI reopens a PDF between commands, so a PDF made by several commands can have its objects numbered differently from the library test's expected PDF. Pass `length_only=True` with `same_as` to compare only the length of the bytes, with standard zlib.

Every test that uses `expect_pdf` gets the `snapshot` marker, so `pytest -m snapshot` runs only the tests that compare with an expected PDF. `make generate-new-pdf-samples` and `make compare-pdf-diffs` run the tests marked `snapshot and not cli_test`.

### Lowest dependency versions

The nightly build also runs every test, including byte comparisons, with the lowest version of each direct dependency on the oldest and newest supported Python versions. Expected PDFs must stay the same on these versions. If a newer version of a dependency changes the bytes, raise that dependency's minimum version to one that produces the regenerated expected PDFs.

To run the tests with the lowest versions locally, install them into a separate virtual environment:

```shell
uv pip install --resolution=lowest-direct -r pyproject.toml --all-extras
```

## Generate coverage report

To generate a test coverage report, run:

=== "Virtual Environment"
    ```shell
    coverage erase && coverage run -m pytest -n auto && coverage combine && coverage html
    ```

    View the coverage report by opening `htmlcov/index.html` in a browser.
=== "Development Container"
    ```shell
    coverage
    ```

    View the coverage report at [http://localhost:8000/htmlcov/index.html](http://localhost:8000/htmlcov/index.html).

## Test breakdown

Although each PyPDFForm test is unique, most follow a general paradigm.

=== "Library"
    Most library tests in `tests/snapshots/` can be summarized in two steps:

    * Use PyPDFForm to generate a PDF from the test inputs.
    * Compare the PDF generated by the test with the expected PDF file named after the test.

    Consider this example test in `tests/snapshots/test_fill.py`:

    ```python
    def test_fill(pdf_samples, expect_pdf):
        obj = PdfWrapper(os.path.join(pdf_samples, "sample_template.pdf")).fill(
            {
                "test": "test_1",
                "check": True,
                "test_2": "test_2",
                "check_2": False,
                "test_3": "test_3",
                "check_3": True,
            },
        )

        expect_pdf(obj.read())
    ```

    The test starts by filling `sample_template.pdf` from `pdf_samples/input/` with a data dictionary using `PdfWrapper`:

    ```python
    obj = PdfWrapper(os.path.join(pdf_samples, "sample_template.pdf")).fill(
        {
            "test": "test_1",
            "check": True,
            "test_2": "test_2",
            "check_2": False,
            "test_3": "test_3",
            "check_3": True,
        },
    )
    ```

    Finally, the test compares the generated PDF with its expected PDF, `pdf_samples/expected/snapshots/test_fill/test_fill.pdf`. `expect_pdf` also records the PDF, so that regenerating expected PDFs can write it:

    ```python
    expect_pdf(obj.read())
    ```

=== "CLI"
    Most CLI tests can be summarized in four steps:

    * Define the expected PDF file.
    * Write any input data required by the command to `tmp_path`.
    * Invoke the CLI command to generate a PDF from the test inputs.
    * Compare the PDF generated by the test with the expected PDF file.

    Consider this example test:

    ```python
    @pytest.mark.cli_test
    def test_fill(pdf_samples, expected_pdfs, tmp_path, expect_pdf):
        expected_path = os.path.join(
            expected_pdfs, "doc_examples", "lib", "test_fill", "test_fill_text_check.pdf"
        )
        input_path = os.path.join(tmp_path, "input.yaml")
        output_path = os.path.join(tmp_path, "output.pdf")
        fill_data = {
            "test": "test_1",
            "check": True,
            "test_2": "test_2",
            "check_2": False,
            "test_3": "test_3",
            "check_3": True,
        }

        with open(input_path, "w") as f:
            yaml.safe_dump(fill_data, f)

        result = runner.invoke(
            cli_app,
            [
                "fill",
                os.path.join(pdf_samples, "sample_template.pdf"),
                "-f",
                input_path,
                "-o",
                output_path,
            ],
        )
        assert result.exit_code == 0

        with open(output_path, "rb") as f:
            expect_pdf(f.read(), same_as=expected_path)
    ```

    Mark CLI tests with `@pytest.mark.cli_test`. The `runner` is a `CliRunner` from
    `typer.testing`, and the command under test is the PyPDFForm CLI app:

    ```python
    import pytest
    import yaml
    from typer.testing import CliRunner

    from PyPDFForm.cli.root import cli_app

    runner = CliRunner()
    ```

    The test starts by defining the expected PDF path, the temporary YAML input path, and the output path. The expected PDF belongs to the library test `tests/doc_examples/lib/test_fill.py::test_fill_text_check`:

    ```python
    expected_path = os.path.join(
        expected_pdfs, "doc_examples", "lib", "test_fill", "test_fill_text_check.pdf"
    )
    input_path = os.path.join(tmp_path, "input.yaml")
    output_path = os.path.join(tmp_path, "output.pdf")
    ```

    The test then writes the fill dictionary to a YAML file in `tmp_path`:

    ```python
    fill_data = {
        "test": "test_1",
        "check": True,
        "test_2": "test_2",
        "check_2": False,
        "test_3": "test_3",
        "check_3": True,
    }

    with open(input_path, "w") as f:
        yaml.safe_dump(fill_data, f)
    ```

    Next, the test invokes the `fill` command against `sample_template.pdf` from `pdf_samples/input/`:

    ```python
    result = runner.invoke(
        cli_app,
        [
            "fill",
            os.path.join(pdf_samples, "sample_template.pdf"),
            "-f",
            input_path,
            "-o",
            output_path,
        ],
    )
    assert result.exit_code == 0
    ```

    Finally, the test compares the PDF written by the command with the expected PDF. A library test owns this expected PDF, so the CLI test uses `same_as` and never regenerates it:

    ```python
    with open(output_path, "rb") as f:
        expect_pdf(f.read(), same_as=expected_path)
    ```
