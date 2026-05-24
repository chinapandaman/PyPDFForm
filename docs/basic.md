# Basic Usage

This section covers the basic entry point and some global options for scaffolding PyPDFForm's APIs.

=== "Library"
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
=== "CLI"
    To use the CLI, simply run:

    ```shell
    pypdfform
    ```

    And it will prompt help messages on commands and their usages. This applies to other subcommands as well when run without any arguments or options.

## Handling appearance streams

For a PDF viewer to display content in a form field (especially text fields), it needs an "appearance stream." This stream defines how the field's content is rendered. PyPDFForm offers two ways to handle this.

=== "Library"
    Appearance stream handling options are set via flags during `PdfWrapper` instantiation.

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
=== "CLI"
    Appearance stream handling options are set via global options when running any commands.

    === "Let the Viewer Generate Appearances"
        ```shell
        pypdfform --need-appearances
        ```
    === "Let PyPDFForm Generate Appearances"
        ```shell
        pypdfform --generate-appearance-streams
        ```

    ???+ warning
        PyPDFForm's internal appearance stream generation relies on [qpdf](https://github.com/qpdf/qpdf) and shares its limitations. Some known limitations include:

        * **Limited to ASCII text:** Only ASCII characters are supported.
        * **Single-line text fields only:** It does not support multi-line text fields.
        * **No text alignment handling:** Text alignment (left, center, right) is not preserved or applied.

## Handling metadata

???+ note
    PDF metadata preservation must be enabled explicitly due to regressions identified in the test suites.

=== "Library"
    To ensure the original metadata of a PDF template is maintained after performing operations with `PdfWrapper`, set the `preserve_metadata` parameter to `True` during instantiation:

    ```python
    from PyPDFForm import PdfWrapper

    pdf = PdfWrapper("sample_template.pdf", preserve_metadata=True)
    ```
=== "CLI"
    For CLI, simply set the global option `--preserve-metadata` when running any commands:

    ```shell
    pypdfform --preserve-metadata
    ```

## Use full name for PDF form fields

According to section 12.7.3.2 of the [PDF standard](https://opensource.adobe.com/dc-acrobat-sdk-docs/pdfstandards/PDF32000_2008.pdf#page=442), PDF form fields can have fully qualified names constructed using the pattern `<parent_field_name>.<field_name>`.

PyPDFForm allows you to access fields by their full names. For example, to use [this PDF](pdfs/sample_template_with_full_key.pdf):

=== "Library"
    Set `use_full_widget_name` to `True` when instantiating `PdfWrapper`:

    ```python
    from PyPDFForm import PdfWrapper

    pdf = PdfWrapper("sample_template_with_full_key.pdf", use_full_widget_name=True)
    ```

    ???+ warning
        When using full names, the `update_widget_key` and `commit_widget_key_updates` methods of `PdfWrapper` are disabled and raise a `NotImplementedError` because full names involve both the field and its parent.
=== "CLI"
    Set the global option `--use-full-widget-name` when running commands:

    ```shell
    pypdfform --use-full-widget-name
    ```

    ???+ warning
        Similar to the library, `pypdfform update rename` will error out when called with `--use-full-widget-name`.

This enables accessing fields by their full names. For instance, you can access the checkbox labeled `Gain de 2 classes` using its full name `Gain de 2 classes.0` instead of its partial name `0`.

## Write to a file

=== "Library"
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
=== "CLI"
    The CLI runs rather stateless. When any command needs to output a file, it either modifies the input file in place or writes the output file to the location specified by the `--output/-o` option.
