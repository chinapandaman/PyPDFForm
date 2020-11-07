# PyPDFForm

PyPDFForm is a pure-python library for PDF form processing. 
It allows filling a PDF form programmatically by creating 
a python dictionary with keys matching its annotation names 
for elements like text fields and checkboxes. It also supports other functionalities such as 
drawing image and merging multiple PDFs together.

## Installing

Install using [pip](https://pip.pypa.io/en/stable/quickstart/):

```shell script
pip install PyPDFForm
```

## Quick Example

A sample PDF form can be found [here](https://github.com/chinapandaman/PyPDFForm/blob/master/pdf_samples/sample_template.pdf). Download it and try:

```python
import os

from PyPDFForm import PyPDFForm

PATH_TO_DOWNLOADED_SAMPLE_PDF_FORM = os.path.join(
    os.path.expanduser("~/Downloads"), "sample_template.pdf"
)  # Change this to where you downloaded the sample PDF form

PATH_TO_FILLED_PDF_FORM = os.path.join(
    os.path.expanduser("~"), "output.pdf"
)  # Change this to where you wish to put your filled PDF form

with open(PATH_TO_DOWNLOADED_SAMPLE_PDF_FORM, "rb+") as template:
    filled_pdf = PyPDFForm(template.read(), simple_mode=False).fill(
        {
            "test": "test_1",
            "check": True,
            "test_2": "test_2",
            "check_2": False,
            "test_3": "test_3",
            "check_3": True,
        },
        font_size=20,
    )

    with open(PATH_TO_FILLED_PDF_FORM, "wb+") as output:
        output.write(filled_pdf.stream)
```

After running the above code snippet you can find `output.pdf` at the location you specified 
and it should look like [this](https://github.com/chinapandaman/PyPDFForm/blob/master/pdf_samples/sample_filled_font_20.pdf).

## Documentation

* API Reference: https://github.com/chinapandaman/PyPDFForm/blob/master/docs/api_reference.md

## Tests

PyPDFForm utilizes [pytest](https://docs.pytest.org/en/stable/) for unit and 
functional tests. Tests can be run by first installing dependencies using 
[pip](https://pip.pypa.io/en/stable/quickstart/):

```shell script
pip install -r requirements.txt
```

Alternatively, there is a bash script which will setup a python virtual environment 
and install all needed dependencies if you are running Linux:

```shell script
./scripts/build.sh
```

In order to run tests, source root needs to be added to PYTHONPATH by running 
the following command at project root:

```shell script
export PYTHONPATH=$PYTHONPATH:$(pwd)/PyPDFForm
```

From there run tests using:

```shell script
pytest -v
```

Or you can use this bash script to do the above two steps if you are running Linux:

```shell script
./scripts/test.sh
```
