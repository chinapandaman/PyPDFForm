<p align="center"><img src="https://github.com/chinapandaman/PyPDFForm/raw/master/docs/img/logo.png"></p>
<p align="center">
    <a href="https://pypi.org/project/PyPDFForm/"><img src="https://img.shields.io/pypi/v/pypdfform?logo=pypi&logoColor=white&label=Version&labelColor=black&color=magenta"></a>
    <a href="https://chinapandaman.github.io/PyPDFForm/"><img src="https://img.shields.io/github/v/release/chinapandaman/pypdfform?logo=read%20the%20docs&logoColor=white&label=Docs&labelColor=black&color=cyan"></a>
    <a href="https://github.com/chinapandaman/PyPDFForm/actions/workflows/python-package.yml"><img src="https://img.shields.io/badge/Coverage-100%25-green?logo=codecov&logoColor=white&labelColor=black"></a>
    <a href="https://github.com/chinapandaman/PyPDFForm/raw/master/LICENSE"><img src="https://img.shields.io/github/license/chinapandaman/pypdfform?logo=github&logoColor=white&label=License&labelColor=black&color=orange"></a><br />
    <a href="https://www.python.org/downloads/"><img src="https://img.shields.io/pypi/pyversions/pypdfform?logo=python&logoColor=white&label=Python&labelColor=black&color=gold"></a>
    <a href="https://pypistats.org/packages/pypdfform"><img src="https://img.shields.io/pypi/dm/pypdfform?logo=pypi&logoColor=white&label=Downloads&labelColor=black&color=blue"></a>
</p>

## Introduction

PyPDFForm is a free and open source pure-Python 3 library for PDF form processing. It contains the essential 
functionalities needed to interact with PDF forms:

* Inspect what data a PDF form needs to be filled with.
* Fill a PDF form by simply creating a Python dictionary.
* Create form fields on a PDF.

It also supports other common utilities such as extracting pages and merging multiple PDFs together.

## Installing

Install using [pip](https://pip.pypa.io/en/stable/):

```shell script
pip install PyPDFForm
```

## Quick Example
![Check out the GitHub repository for a live demo if you can't see it here.](https://github.com/chinapandaman/PyPDFForm/raw/master/docs/img/demo.gif)

A sample PDF form can be found [here](https://github.com/chinapandaman/PyPDFForm/raw/master/pdf_samples/sample_template.pdf). Download it and try:

```python
from PyPDFForm import PdfWrapper

filled = PdfWrapper("sample_template.pdf", adobe_mode=True).fill(
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
and it should look like [this](https://github.com/chinapandaman/PyPDFForm/raw/master/pdf_samples/adobe_mode/sample_filled.pdf).

## Documentation

The official documentation can be found on [the GitHub page](https://chinapandaman.github.io/PyPDFForm/) of this repository.

## Other Resources

[Chicago Python User Group - Dec 14, 2023](https://youtu.be/8t1RdAKwr9w?si=TLgumBNXv9H8szSn)
