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

The library's main user interface is the class `PdfWrapper`. It implements most PyPDFForm APIs and accepts various optional parameters, with the PDF form template being the most critical.

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

## Create an Adobe Acrobat compatible PDF wrapper

Adobe Acrobat has known issues displaying PDF forms filled with text. Specifically, text content may only be visible when the text field is selected. This issue is not present in browsers like Chrome or PDF viewers such as Document Viewer (Ubuntu's default PDF application).

By setting the optional parameter `adobe_mode` (default value is `False`) to `True` when instantiating the object, `PdfWrapper` will ensure that the PDF can be processed and displayed correctly by Adobe Acrobat:

```python
from PyPDFForm import PdfWrapper

pdf = PdfWrapper("sample_template.pdf", adobe_mode=True)
```

**NOTE:** PDF objects with `adobe_mode` enabled are optimized for viewing in Adobe Acrobat. Other PDF viewers may experience rendering issues with certain field styles, such as text font or field borders.
So only enable `adobe_mode` when the generated PDFs are meant to be viewed by Adobe Acrobat.

## Use full name for PDF form fields

According to section 12.7.3.2 of the [PDF standard](https://opensource.adobe.com/dc-acrobat-sdk-docs/pdfstandards/PDF32000_2008.pdf) (page 434), PDF form fields can have fully qualified names constructed using the pattern `<parent_field_name>.<field_name>`.

PyPDFForm allows you to access fields by their full names by setting `use_full_widget_name` to `True` when instantiating `PdfWrapper`. For example, using [this PDF](https://github.com/chinapandaman/PyPDFForm/raw/master/pdf_samples/sample_template_with_full_key.pdf):

```python
from PyPDFForm import PdfWrapper

pdf = PdfWrapper("sample_template_with_full_key.pdf", use_full_widget_name=True)
```

This enables accessing fields by their full names. For instance, you can access the checkbox labeled `Gain de 2 classes` using its full name `Gain de 2 classes.0` instead of the partial name `0`.

**NOTE:** When using full names, the `update_widget_key` and `commit_widget_key_updates` methods of `PdfWrapper` are disabled and raise a `NotImplementedError` because full names involve both the field and its parent.

## Write to a file

`PdfWrapper` also behaves like an open file object, allowing you to write the PDF to another file object. For example, to write to a disk file:

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

On top of being similar to a file object, `PdfWrapper` also implements a `write` method which lets you write the PDF to a disk file by specifying the path:

```python
from PyPDFForm import PdfWrapper

pdf = PdfWrapper("sample_template.pdf")
pdf.write("output.pdf")
```
