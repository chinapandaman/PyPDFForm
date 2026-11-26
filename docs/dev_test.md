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

## Adding tests

Add only the tests needed to cover the changed behavior and maintain 100% coverage. Extend existing test files. If a new test file is absolutely necessary, consult the maintainer before creating it.

Leave expected PDF sample regeneration and visual regression comparison to the maintainer unless they explicitly delegate these tasks.

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

Use them when a change affects one of these properties. Not every PDF passes all of them. For example, filling a text field by default writes an `/AP` that isn't a dictionary.

## Expected PDF environment

Most tests compare the PDF they generate with an expected PDF in `pdf_samples`, using the [`expect_pdf`](#comparing-with-expected-pdfs) fixture. The bytes of a PDF can depend on:

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
def test_fill_font_color(sample_template_with_font_colors, pdf_samples, expect_pdf):
    expected_path = os.path.join(pdf_samples, "test_fill_font_color.pdf")
    obj = PdfWrapper(sample_template_with_font_colors).fill(...)

    expect_pdf(obj.read(), expected_path)
```

On every platform, the fixture checks that both PDFs have the same version, trailer, and objects, comparing each stream after decompressing it. It ignores each stream's `/Length` and the trailer's `/ID`. Python's zlib compresses some of the streams PyPDFForm writes, such as embedded fonts, drawn text and images, and created fields, so the fixture compares the bytes only with standard zlib.

The test owns this expected PDF. Regenerating expected PDFs writes the test's PDF to that path, even when the comparison fails or the expected PDF doesn't exist yet. Each expected PDF has one owner. Other tests compare with it using `same_as`, which never regenerates it:

```python
expect_pdf(actual, same_as=expected_path)
```

When the comparison fails, regenerating expected PDFs into another directory writes the other test's PDF as `<expected PDF>.<test>.pdf`, so `make compare-pdf-diffs` shows it next to the expected PDF.

If two tests own the same expected PDF, the run ends with exit status 4 and lists them, because the PDF written last would hide the other. Regenerating in place then leaves that expected PDF as it was.

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
    Most library tests can be summarized in three steps:

    * Define the expected PDF file.
    * Use PyPDFForm to generate a PDF from the test inputs.
    * Compare the PDF generated by the test with the expected PDF file.

    Consider this example test:

    ```python
    def test_fill(pdf_samples, expect_pdf):
        expected_path = os.path.join(pdf_samples, "sample_filled.pdf")
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

        expect_pdf(obj.read(), expected_path)
    ```

    The test starts by defining an expected PDF `sample_filled.pdf`:

    ```python
    expected_path = os.path.join(pdf_samples, "sample_filled.pdf")
    ```

    The test then fills `sample_template.pdf` with a data dictionary using `PdfWrapper`:

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

    Finally, the test compares the generated PDF with the expected PDF. `expect_pdf` also records the PDF, so that regenerating expected PDFs can write it:

    ```python
    expect_pdf(obj.read(), expected_path)
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
    def test_fill(pdf_samples, tmp_path, expect_pdf):
        expected_path = os.path.join(pdf_samples, "docs", "test_fill_text_check.pdf")
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

    The test starts by defining the expected PDF path, the temporary YAML input path, and the output path:

    ```python
    expected_path = os.path.join(pdf_samples, "docs", "test_fill_text_check.pdf")
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

    Next, the test invokes the `fill` command against `sample_template.pdf` from `pdf_samples`:

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
