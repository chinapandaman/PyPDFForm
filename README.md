<p align="center"><img src="https://github.com/chinapandaman/PyPDFForm/raw/master/docs/img/logo.png"></p>
<p align="center">
    <em>PDF Form Automation Simplified - Create, Inspect, Style, and Fill Forms in Python or from the Command Line.</em>
</p>
<p align="center">
    <a href="https://pypi.org/project/PyPDFForm/"><img src="https://img.shields.io/pypi/v/pypdfform?label=version&color=magenta"></a>
    <a href="https://chinapandaman.github.io/PyPDFForm/"><img src="https://img.shields.io/github/v/release/chinapandaman/pypdfform?label=docs&color=cyan"></a>
    <a href="https://github.com/chinapandaman/PyPDFForm/actions/workflows/python-package.yml"><img src="https://img.shields.io/badge/coverage-100%25-green"></a>
    <a href="https://github.com/chinapandaman/PyPDFForm/blob/master/LICENSE"><img src="https://img.shields.io/github/license/chinapandaman/pypdfform?label=license&color=orange"></a>
    <a href="https://www.python.org/downloads/"><img src="https://img.shields.io/pypi/pyversions/pypdfform?label=python&color=gold"></a>
    <a href="https://pepy.tech/projects/pypdfform"><img src="https://static.pepy.tech/badge/pypdfform/month"></a>
</p>

## Introduction

PyPDFForm is a Python library and command line tool for working with PDF forms. It provides Python APIs and CLI commands for creating, inspecting, updating, and filling forms, plus common PDF utilities.

With PyPDFForm, you can:

* Create PDF forms, form fields, and raw elements.
* Inspect form fields, metadata, and values.
* Update field styling, behavior, and scripts.
* Fill PDF forms.
* Extract pages and merge PDFs.

The goal is to make PDF form work straightforward, whether you are handling one document or building a larger workflow.

## Installing

To use PyPDFForm as a Python library, install the base package with [pip](https://pypi.org/project/PyPDFForm/):

```shell
pip install PyPDFForm
```

To use the CLI, install PyPDFForm with the `cli` extra using [pipx](https://pipx.pypa.io/stable/):

```shell
pipx install "PyPDFForm[cli]"
```

## Quick Example
![Check out the GitHub repository for a live demo if you can't see it here.](https://github.com/chinapandaman/PyPDFForm/raw/master/docs/img/demo.gif)

The GIF above shows the CLI filling a PDF form. To try the same workflow with the Python library, download the [sample PDF form](https://chinapandaman.github.io/PyPDFForm/latest/pdfs/sample_template.pdf) and run:

```python
from PyPDFForm import PdfWrapper

filled = PdfWrapper("sample_template.pdf", need_appearances=True).fill(
    {
        "test": "test_1",
        "check": True,
        "test_2": "test_2",
        "check_2": False,
        "test_3": "test_3",
        "check_3": True,
    },
)

filled.write("output.pdf")
```

After running this snippet, `output.pdf` will be written to the location you specified and should look like [this](https://chinapandaman.github.io/PyPDFForm/latest/pdfs/sample_filled.pdf).

## Documentation

The official documentation can be found on [the GitHub page](https://chinapandaman.github.io/PyPDFForm/) of this repository.

## Other Resources

<!-- TODO: remove WIP when finish recording -->
* [(WIP) Video Tutorials](https://youtube.com/playlist?list=PLNz_PBu1QA-gzYg5BvyOO98q15u5Xve1L&si=8MWasKEckBzY-NRQ)
* [Chicago Python User Group - Dec 14, 2023](https://youtu.be/8t1RdAKwr9w?si=TLgumBNXv9H8szSn)
