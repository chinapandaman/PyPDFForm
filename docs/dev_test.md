# Testing

PyPDFForm uses [pytest](https://pytest.org/) for testing and [coverage.py](https://coverage.readthedocs.io/) 
for test coverages. Tests can be run by simply executing:

```shell
coverage run -m pytest && coverage report --fail-under=100
```

## Generate coverage report

To generate a coverage report, run:

```shell
coverage run -m pytest && coverage html
```

And the coverage report can be viewed by openning `htmlcov/index.html` in a browser.

## Test breakdown

Each PyPDFForm test is different case by case. However, there is a general paradigm that almost all tests follow.

In most cases, a test executes a sequence of instructions related to PyPDFForm, whether being filling a PDF form or 
drawing a text. After the sequence is done, the test should compare the resulted PDF stream with an "expected" PDF stream. 
The expected PDF is a file found under the `pdf_samples` directory.

Consider this example test:

```python
def test_fill(pdf_samples, request):
    expected_path = os.path.join(pdf_samples, "sample_filled.pdf")
    with open(expected_path, "rb+") as f:
        obj = PdfWrapper(
            os.path.join(pdf_samples, "sample_template.pdf")
        ).fill(
            {
                "test": "test_1",
                "check": True,
                "test_2": "test_2",
                "check_2": False,
                "test_3": "test_3",
                "check_3": True,
            },
        )

        request.config.results["expected_path"] = expected_path
        request.config.results["stream"] = obj.read()

        expected = f.read()

        assert len(obj.read()) == len(expected)
        assert obj.read() == expected
```

The test starts by setting an expected PDF `sample_filled.pdf`:

```python
expected_path = os.path.join(pdf_samples, "sample_filled.pdf")
```

The test then fills `sample_template.pdf` with a data dictionary using `PdfWrapper`:

```python
obj = PdfWrapper(
    os.path.join(pdf_samples, "sample_template.pdf")
).fill(
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

These two lines should almost always be added in every test to make updating old tests easier:

```python
request.config.results["expected_path"] = expected_path
request.config.results["stream"] = obj.read()
```

Finally, the test compares the resulted stream from the test with the expected file stream:

```python
expected = f.read()

assert len(obj.read()) == len(expected)
assert obj.read() == expected
```

This concludes the test, which is equivalent to saying after filling `sample_template.pdf` using the 
data dictionary, it should look like `sample_filled.pdf`.
