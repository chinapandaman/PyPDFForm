# Installation and setup

PyPDFForm is available on [PyPI](https://pypi.org/project/PyPDFForm/) and can be installed using any preferred package manager, such as pip, Poetry, or uv.

## Prerequisites

PyPDFForm officially supports Python 3.10 and newer versions that are currently in their active life cycles. This typically includes the minimum supported version and the four major versions above it. For details on Python version life cycles, refer to [this page](https://devguide.python.org/versions/).

???+ info
    While official support is limited to active Python versions, PyPDFForm generally avoids features specific to particular major Python versions. It is expected to be functional with Python 3.7+ (due to its use of [Postponed Evaluation of Annotations](https://peps.python.org/pep-0563/) for type hints, introduced in Python 3.7), though these versions are not actively tested.

## Install using pip

It is highly recommended to create a virtual environment before installation. Then, run the following command to install PyPDFForm:

=== "Install"
    ```shell
    pip install PyPDFForm
    ```
=== "Install & Upgrade Dependencies"
    ```shell
    pip install -U PyPDFForm
    ```

## Create a PDF wrapper

The main user interface of the library is the `PdfWrapper` class. It implements most PyPDFForm APIs and accepts various optional parameters, the most important of which is the PDF form template.

For example, to use [this PDF](pdfs/sample_template.pdf) as a template, instantiate the `PdfWrapper` object as follows:

=== "File Path"
    ```python
    from PyPDFForm import PdfWrapper

    pdf = PdfWrapper("sample_template.pdf")
    ```
=== "Open File Object"
    ```python
    from PyPDFForm import PdfWrapper

    with open("sample_template.pdf", "rb+") as template:
        pdf = PdfWrapper(template)
    ```
=== "Bytes File Stream"
    ```python
    from PyPDFForm import PdfWrapper

    with open("sample_template.pdf", "rb+") as template:
        pdf = PdfWrapper(template.read())
    ```

???+ tip
    PyPDFForm provides an adapter for different file interaction methods in Python, which allows you to pass your PDF form to `PdfWrapper` as a file path, an open file object, or a `bytes` file stream. This file adaptation applies to all PyPDFForm APIs. You can replace file path parameters with file objects or streams throughout the documentation.

## Change PDF title

The PDF title can be set during `PdfWrapper` instantiation or via the `.title` property. Accessing it retrieves the current title.

=== "Instantiate with Title"
    ```python
    from PyPDFForm import PdfWrapper

    pdf = PdfWrapper("sample_template.pdf", title="My PDF")
    ```
=== "Set Title via Attribute"
    ```python
    from PyPDFForm import PdfWrapper

    pdf = PdfWrapper("sample_template.pdf")
    pdf.title = "My PDF"
    ```
=== "Get Title via Attribute"
    ```python
    from PyPDFForm import PdfWrapper

    pdf = PdfWrapper("sample_template.pdf", title="My PDF")
    print(pdf.title)
    ```

## Handling appearance streams

For a PDF viewer to display content in a form field (especially text fields), it needs an "appearance stream." This stream defines how the field's content is rendered. PyPDFForm offers two ways to handle this, set via flags during `PdfWrapper` instantiation.

=== "Let the Viewer Generate Appearances"
    Set `need_appearances=True` to instruct the PDF viewer to generate appearance streams. This is often the best choice when you expect the PDF to be opened in powerful, proprietary software like Adobe Acrobat, which has sophisticated rendering capabilities.

    ```python
    from PyPDFForm import PdfWrapper

    pdf = PdfWrapper("sample_template.pdf", need_appearances=True)
    ```

=== "Let PyPDFForm Generate Appearances"
    Set `generate_appearance_streams=True` to use PyPDFForm's built-in generator. This is a good fallback if the PDF viewer lacks the ability to generate its own appearance streams.

    ```python
    from PyPDFForm import PdfWrapper

    pdf = PdfWrapper("sample_template.pdf", generate_appearance_streams=True)
    ```

    ???+ warning
        PyPDFForm's internal appearance stream generation relies on [qpdf](https://github.com/qpdf/qpdf) and shares its limitations. Some known limitations include:

        * **Limited to ASCII text:** Only ASCII characters are supported.
        * **Single-line text fields only:** It does not support multi-line text fields.
        * **No text alignment handling:** Text alignment (left, center, right) is not preserved or applied.

## Handling metadata

???+ note
    Due to some regressions in the test suites, PDF metadata needs to be handled explicitly.

To ensure a PDF's metadata is preserved after performing operations through `PdfWrapper`, instantiate the object with `preserve_metadata` set to `True`:

```python
from PyPDFForm import PdfWrapper

pdf = PdfWrapper("sample_template.pdf", preserve_metadata=True)
```

## Use full name for PDF form fields

According to section 12.7.3.2 of the [PDF standard](https://opensource.adobe.com/dc-acrobat-sdk-docs/pdfstandards/PDF32000_2008.pdf#page=442), PDF form fields can have fully qualified names constructed using the pattern `<parent_field_name>.<field_name>`.

PyPDFForm allows you to access fields by their full names by setting `use_full_widget_name` to `True` when instantiating `PdfWrapper`. For example, to use [this PDF](pdfs/sample_template_with_full_key.pdf):

```python
from PyPDFForm import PdfWrapper

pdf = PdfWrapper("sample_template_with_full_key.pdf", use_full_widget_name=True)
```

This enables accessing fields by their full names. For instance, you can access the checkbox labeled `Gain de 2 classes` using its full name `Gain de 2 classes.0` instead of its partial name `0`.

???+ warning
    When using full names, the `update_widget_key` and `commit_widget_key_updates` methods of `PdfWrapper` are disabled and raise a `NotImplementedError` because full names involve both the field and its parent.

## Write to a file

The `PdfWrapper` acts as a file-like object, enabling you to write the processed PDF to another file-like object:

=== "Write to Disk File"
    ```python
    from PyPDFForm import PdfWrapper

    pdf = PdfWrapper("sample_template.pdf")

    with open("output.pdf", "wb+") as output:
        output.write(pdf.read())
    ```
=== "Write to Memory Buffer"
    ```python
    from io import BytesIO
    from PyPDFForm import PdfWrapper

    pdf = PdfWrapper("sample_template.pdf")

    with BytesIO() as output:
        output.write(pdf.read())
    ```

Additionally, `PdfWrapper` offers a convenient `write` method to save the PDF directly.

=== "Write to Disk File"
    ```python
    from PyPDFForm import PdfWrapper

    pdf = PdfWrapper("sample_template.pdf")
    pdf.write("output.pdf")
    ```
=== "Write to Memory Buffer"
    ```python
    from io import BytesIO
    from PyPDFForm import PdfWrapper

    buff = BytesIO()

    pdf = PdfWrapper("sample_template.pdf")
    pdf.write(buff)

    buff.seek(0)
    ```
