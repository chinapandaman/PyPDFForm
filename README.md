<p align="center"><img src="https://github.com/chinapandaman/PyPDFForm/raw/master/logo.png"></p>
<p align="center">
    <a href="https://pypi.org/project/PyPDFForm/"><img src="https://img.shields.io/pypi/v/pypdfform?logo=pypi&logoColor=white&label=version&labelColor=black&color=magenta&style=for-the-badge"></a>
    <a href="https://chinapandaman.github.io/PyPDFForm/"><img src="https://img.shields.io/github/v/release/chinapandaman/pypdfform?logo=read%20the%20docs&logoColor=white&label=docs&labelColor=black&color=cyan&style=for-the-badge"></a>
    <a href="https://github.com/chinapandaman/PyPDFForm/actions/workflows/python-package.yml"><img src="https://img.shields.io/github/actions/workflow/status/chinapandaman/pypdfform/python-package.yml?logo=github&logoColor=white&label=tests&labelColor=black&color=green&style=for-the-badge"></a>
    <a href="https://github.com/chinapandaman/PyPDFForm/raw/master/LICENSE"><img src="https://img.shields.io/github/license/chinapandaman/pypdfform?logo=github&logoColor=white&label=license&labelColor=black&color=orange&style=for-the-badge"></a>
    <a href="https://www.python.org/downloads/"><img src="https://img.shields.io/pypi/pyversions/pypdfform?logo=python&logoColor=white&label=python&labelColor=black&color=gold&style=for-the-badge"></a>
    <a href="https://pypistats.org/packages/pypdfform"><img src="https://img.shields.io/pypi/dm/pypdfform?logo=pypi&logoColor=white&label=downloads&labelColor=black&color=blue&style=for-the-badge"></a>
</p>

## Introduction

PyPDFForm is a free and open source pure-Python 3 library for PDF form processing. It contains the essential 
functionalities needed to interact with PDF forms:

* Inspect what data a PDF form needs to be filled with.
* Fill a PDF form by simply creating a Python dictionary.
* Create a subset of form widgets on a PDF.

It also supports other common utilities such as extracting pages and merging multiple PDFs together.

## Installing

Install using [pip](https://pip.pypa.io/en/stable/):

```shell script
pip install PyPDFForm
```

## Quick Example
![Check out the GitHub repository for a live demo if you can't see it here.](https://github.com/chinapandaman/PyPDFForm/raw/master/demo.gif)

A sample PDF form can be found [here](https://github.com/chinapandaman/PyPDFForm/raw/master/pdf_samples/sample_template.pdf). Download it and try:

```python
from PyPDFForm import PdfWrapper

filled = PdfWrapper("sample_template.pdf").fill(
    {
        "test": "test_1",
        "check": True,
        "test_2": "test_2",
        "check_2": False,
        "test_3": "test_3",
        "check_3": True,
    },
)

with open("output.pdf", "wb+") as output:
    output.write(filled.read())
```

After running the above code snippet you can find `output.pdf` at the location you specified, 
and it should look like [this](https://github.com/chinapandaman/PyPDFForm/raw/master/pdf_samples/sample_filled.pdf).

## Documentation

The official documentation can be found on [the GitHub page](https://chinapandaman.github.io/PyPDFForm/) of this repository.

## Other Resources

[Chicago Python User Group - Dec 14, 2023](https://youtu.be/8t1RdAKwr9w?si=TLgumBNXv9H8szSn)
