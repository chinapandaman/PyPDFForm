# Installation and setup

PyPDFForm is available on PyPI and can be installed using any compatible tool, with pip being the most common choice.

## Install using pip

PyPDFForm requires Python 3.9+.

Create a virtual environment before installation. Then, run the following command to install PyPDFForm:

```shell
pip install PyPDFForm
```

To upgrade PyPDFForm as well as all its dependencies, run:

```shell
pip install -U PyPDFForm
```

## Create a PDF wrapper

The library provides two classes for abstracting PDF forms. Use `FormWrapper` to fill a PDF form without needing other APIs; more information is available [here](simple_fill.md).

`PdfWrapper` implements most PyPDFForm APIs and accepts various optional parameters, with the PDF form template being the most critical.

For example, if you download [this PDF](https://github.com/chinapandaman/PyPDFForm/raw/master/pdf_samples/sample_template.pdf), 
you will want to instantiate your object like this:

```python
from PyPDFForm import PdfWrapper

pdf = PdfWrapper("sample_template.pdf")
```

PyPDFForm provides an adapter for different file interaction methods in Python, allowing you to pass your PDF form to `PdfWrapper` as a file path, open file object, or `bytes` file stream.

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

This file adaptation applies to all PyPDFForm APIs. You can replace file path parameters with file objects or streams throughout the documentation.

## Use full widget name in PDF wrapper

According to section 12.7.3.2 found on page 434 of [the PDF standard](https://opensource.adobe.com/dc-acrobat-sdk-docs/pdfstandards/PDF32000_2008.pdf), each PDF form widget can have a fully qualified name that is not explicitly defined but can be constructed following the pattern `<parent_widget_name>.<widget_name>`.

PyPDFForm supports accessing widgets through their full names by simply setting the optional parameter `use_full_widget_name` to `True` when a `PdfWrapper` object is instantiated. Consider [this PDF](https://github.com/chinapandaman/PyPDFForm/raw/master/pdf_samples/sample_template_with_full_key.pdf):

```python
from PyPDFForm import PdfWrapper

pdf = PdfWrapper("sample_template_with_full_key.pdf", use_full_widget_name=True)
```

The checkbox widget on the second page with texts `Gain de 2 classes` has a partial name of `0` and a full name of `Gain de 2 classes.0`. By constructing the object like above, you can access the same checkbox through both the partial name and the full name.

**NOTE:** When using full widget names, the `update_widget_key` and `commit_widget_key_updates` methods are disabled and raise a `NotImplementedError` because full names involve both the widget and its parent.

## Write to a file

`PdfWrapper` also behaves like an open file object, allowing you to write the PDF to another file or buffer.

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
