<p align="center"><img src="https://github.com/chinapandaman/PyPDFForm/raw/master/docs/img/logo.png"></p>
<p align="center">
    <em>PDF Form Automation Simplified – Create, Merge, Style, and Fill Forms Programmatically.</em>
</p>
<p align="center">
    <a href="https://pypi.org/project/PyPDFForm/"><img src="https://img.shields.io/pypi/v/pypdfform?label=version&color=magenta"></a>
    <a href="https://chinapandaman.github.io/PyPDFForm/"><img src="https://img.shields.io/github/v/release/chinapandaman/pypdfform?label=docs&color=cyan"></a>
    <a href="https://codecov.io/gh/chinapandaman/PyPDFForm"><img src="https://img.shields.io/codecov/c/github/chinapandaman/pypdfform"/></a>
    <a href="https://github.com/chinapandaman/PyPDFForm/raw/master/LICENSE"><img src="https://img.shields.io/github/license/chinapandaman/pypdfform?label=license&color=orange"></a>
    <a href="https://www.python.org/downloads/"><img src="https://img.shields.io/pypi/pyversions/pypdfform?label=python&color=gold"></a>
    <a href="https://pepy.tech/projects/pypdfform"><img src="https://static.pepy.tech/badge/pypdfform/month"></a>
</p>

## Introduction

PyPDFForm is a Python library for PDF form processing. It contains the essential functionalities needed to interact with PDF forms:

* Inspect what data a PDF form needs to be filled with.
* Fill a PDF form by simply creating a Python dictionary.
* Create form fields on a PDF.

It also supports other common utilities such as extracting pages and merging multiple PDFs together.

## Installing

Install using [pip](https://pypi.org/project/PyPDFForm/):

```shell script
pip install PyPDFForm
```

## Quick Example
![Check out the GitHub repository for a live demo if you can't see it here.](https://github.com/chinapandaman/PyPDFForm/raw/master/docs/img/demo.gif)

A sample PDF form can be found [here](https://chinapandaman.github.io/PyPDFForm/pdfs/sample_template.pdf). Download it and try:

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

After running the above code snippet you can find `output.pdf` at the location you specified, 
and it should look like [this](https://chinapandaman.github.io/PyPDFForm/pdfs/sample_filled.pdf).

## Documentation

The official documentation can be found on [the GitHub page](https://chinapandaman.github.io/PyPDFForm/) of this repository.

## Other Resources

[Chicago Python User Group - Dec 14, 2023](https://youtu.be/8t1RdAKwr9w?si=TLgumBNXv9H8szSn)

## Star History

This project is maintained entirely in my spare time. If you like the project please consider starring the GitHub repository. It is the best way to keep me motivated and continue making the project better.

[![Stargazers over time](https://starchart.cc/chinapandaman/PyPDFForm.svg?variant=adaptive)](https://starchart.cc/chinapandaman/PyPDFForm)
