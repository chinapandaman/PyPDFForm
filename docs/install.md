# Installation and setup

PyPDFForm is available on [PyPI](https://pypi.org/project/PyPDFForm/) and can be installed using any preferred package manager, such as pip, Poetry, or uv.

## Prerequisites

PyPDFForm officially supports Python 3.10 and newer versions that are currently in their active life cycles. This typically includes the minimum supported version and the four major versions above it. For details on Python version life cycles, refer to [this page](https://devguide.python.org/versions/).

**NOTE:** While official support is limited to active Python versions, PyPDFForm generally avoids features specific to particular major Python versions. It is expected to be functional with Python 3.7+ (due to its use of [Postponed Evaluation of Annotations](https://peps.python.org/pep-0563/) for type hints, introduced in Python 3.7), though these versions are not actively tested.

## Install using pip

It is highly recommended to create a virtual environment before installation. Then, run the following command to install PyPDFForm:

```shell
pip install PyPDFForm
```

To upgrade PyPDFForm and all its dependencies, run:

```shell
pip install -U PyPDFForm
```

## Create a PDF wrapper

The main user interface of the library is the `PdfWrapper` class. It implements most PyPDFForm APIs and accepts various optional parameters, the most important of which is the PDF form template.

For example, to use [this PDF](pdfs/sample_template.pdf) as a template, instantiate the `PdfWrapper` object as follows:

```python
from PyPDFForm import PdfWrapper

pdf = PdfWrapper("sample_template.pdf")
```

PyPDFForm provides an adapter for different file interaction methods in Python, which allows you to pass your PDF form to `PdfWrapper` as a file path, an open file object, or a `bytes` file stream.

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

**NOTE:** The `PdfWrapper` class does not handle appearance streams by default. For details, see [Handling Appearance Streams](#handling-appearance-streams).

## Handling Appearance Streams

To display PDF form fields filled programmatically, especially text fields, each field requires an appearance stream. This stream dictates how a PDF viewer renders the field's content.

PyPDFForm supports two flags for handling appearance streams, which you set when instantiating the `PdfWrapper` object.

The first flag is `need_appearances`. Setting this flag to `True` tells the PDF viewer/editor opening the generated PDF form to generate appearance streams for each field, if the viewer is capable:

```python
from PyPDFForm import PdfWrapper

pdf = PdfWrapper("sample_template.pdf", need_appearances=True)
```

Alternatively, use PyPDFForm's internal appearance stream generation functionality by setting the `generate_appearance_streams` flag to `True`:

```python
from PyPDFForm import PdfWrapper

pdf = PdfWrapper("sample_template.pdf", generate_appearance_streams=True)
```

The choice between these two flags is situational. Use `need_appearances=True` when the output PDF is viewed in proprietary software like Adobe Acrobat, as these viewers typically have sophisticated appearance stream generation logic. If the PDF viewer does not support generating appearance streams, set `generate_appearance_streams=True` to allow PyPDFForm to handle the generation. Note that PyPDFForm's internal generation functionality is still undergoing testing and refinement.

## Use full name for PDF form fields

According to section 12.7.3.2 of the [PDF standard](https://opensource.adobe.com/dc-acrobat-sdk-docs/pdfstandards/PDF32000_2008.pdf) (page 434), PDF form fields can have fully qualified names constructed using the pattern `<parent_field_name>.<field_name>`.

PyPDFForm allows you to access fields by their full names by setting `use_full_widget_name` to `True` when instantiating `PdfWrapper`. For example, to use [this PDF](pdfs/sample_template_with_full_key.pdf):

```python
from PyPDFForm import PdfWrapper

pdf = PdfWrapper("sample_template_with_full_key.pdf", use_full_widget_name=True)
```

This enables accessing fields by their full names. For instance, you can access the checkbox labeled `Gain de 2 classes` using its full name `Gain de 2 classes.0` instead of its partial name `0`.

**NOTE:** When using full names, the `update_widget_key` and `commit_widget_key_updates` methods of `PdfWrapper` are disabled and raise a `NotImplementedError` because full names involve both the field and its parent.

## Write to a file

The `PdfWrapper` acts as a file-like object, enabling you to write the processed PDF to another file-like object. For instance, to save to a disk file:

```python
from PyPDFForm import PdfWrapper

pdf = PdfWrapper("sample_template.pdf")

with open("output.pdf", "wb+") as output:
    output.write(pdf.read())
```

It doesn't have to be a disk file; it can be a memory buffer as well:

```python
from io import BytesIO
from PyPDFForm import PdfWrapper

pdf = PdfWrapper("sample_template.pdf")

with BytesIO() as output:
    output.write(pdf.read())
```

Additionally, `PdfWrapper` offers a convenient `write` method to save the PDF directly. You can specify a disk file path:

```python
from PyPDFForm import PdfWrapper

pdf = PdfWrapper("sample_template.pdf")
pdf.write("output.pdf")
```

Alternatively, you can provide a memory buffer:

```python
from io import BytesIO
from PyPDFForm import PdfWrapper

buff = BytesIO()

pdf = PdfWrapper("sample_template.pdf")
pdf.write(buff)

buff.seek(0)
```
