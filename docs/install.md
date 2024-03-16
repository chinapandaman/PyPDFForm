# Installation and setup

PyPDFForm is hosted on PyPI and any tool that supports downloading from it can be used. 
The most common option is to use pip.

## Install using pip

PyPDFForm requires Python 3.7+.

It is advised that a virtual environment is always created beforehand. Then you can run the following command to install:

```shell
pip install PyPDFForm
```

To upgrade PyPDFForm as well as all its dependencies, run:

```shell
pip install -U PyPDFForm
```

## Create a PDF wrapper

There are two classes provided by the library that abstract a PDF form. The `FormWrapper` class allows you to fill a 
PDF form if you don't need any other API. More info about `FormWrapper` can be found 
[here](simple_fill.md).

The class that implements most of PyPDFForm's APIs is `PdfWrapper`. It takes various optional parameters to instantiate, 
with the most important one being the PDF form "template".

For example, if you download [this PDF](https://github.com/chinapandaman/PyPDFForm/raw/master/pdf_samples/sample_template.pdf), 
you will want to instantiate your object like this:

```python
from PyPDFForm import PdfWrapper

pdf = PdfWrapper("sample_template.pdf")
```

PyPDFForm does implement an adapter for different ways Python interacts with files. So you can pass your PDF form to 
`PdfWrapper` in three different ways: a file path, an open file object, and a file stream that's in `bytes`.

This means the following two snippets are equivalent to the above:

```python
from PyPDFForm import PdfWrapper

with open("sample_template.pdf", "rb+") as template:
    pdf = PdfWrapper(template)
```

```python
from PyPDFForm import PdfWrapper

with open("sample_template.pdf", "rb+") as template:
    pdf = PdfWrapper(template.read())
```

This adaptation is universal across all APIs of PyPDFForm. So in later sections of the documentation whenever you see 
a function parameter that's a file path you can safely switch them for a file object or file stream.

## Write to a file

Lastly, `PdfWrapper` also implements itself similar to an open file object. So you can write the PDF it holds to another 
file:

```python
from PyPDFForm import PdfWrapper

pdf = PdfWrapper("sample_template.pdf")

with open("output.pdf", "wb+") as output:
    output.write(pdf.read())
```

And it doesn't have to be a disk file, it can be a memory buffer as well:

```python
from io import BytesIO

from PyPDFForm import PdfWrapper

pdf = PdfWrapper("sample_template.pdf")

with BytesIO() as output:
    output.write(pdf.read())
```
