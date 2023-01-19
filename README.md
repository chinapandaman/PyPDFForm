# PyPDFForm ![code formatting](https://github.com/chinapandaman/PyPDFForm/actions/workflows/python-black-isort.yml/badge.svg) ![tests](https://github.com/chinapandaman/PyPDFForm/actions/workflows/python-package.yml/badge.svg) [![codecov](https://codecov.io/gh/chinapandaman/PyPDFForm/branch/master/graph/badge.svg?token=CSRLN14IFE)](https://codecov.io/gh/chinapandaman/PyPDFForm) ![deploy](https://github.com/chinapandaman/PyPDFForm/actions/workflows/python-publish.yml/badge.svg)

PyPDFForm is a pure Python library for PDF form processing. 
It allows filling a PDF form programmatically by creating 
a Python dictionary with keys matching its annotated names 
for elements like text fields and checkboxes. It also supports other functionalities such as 
drawing image and merging multiple PDFs together.

## Installing

Install using [pip](https://pip.pypa.io/en/stable/):

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

with open(PATH_TO_FILLED_PDF_FORM, "wb+") as output:
    output.write(
        PyPDFForm(PATH_TO_DOWNLOADED_SAMPLE_PDF_FORM)
        .fill(
            {
                "test": "test_1",
                "check": True,
                "test_2": "test_2",
                "check_2": False,
                "test_3": "test_3",
                "check_3": True,
            },
        )
        .read()
    )
```

After running the above code snippet you can find `output.pdf` at the location you specified, 
and it should look like [this](https://github.com/chinapandaman/PyPDFForm/blob/master/pdf_samples/sample_filled.pdf).

## Documentation

[Examples](https://github.com/chinapandaman/PyPDFForm/blob/master/docs/examples.md)

## How to Contribute

If you wish to improve this library, there is one specific way you can contribute 
on top of the usual open source project norms such as issues and pull requests.

It is difficult to make sure that the library supports all the PDF form creating tools out 
there. So if you run into a case where the library does not work for certain PDF forms created by 
certain tools, feel free to open an issue with the problematic PDF form attached. I will seek 
to make the library support the attached PDF form as well as the tool used to create it.
