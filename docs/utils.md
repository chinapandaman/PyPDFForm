# Other utilities

PyPDFForm offers additional utilities similar to other PDF libraries.

This section of the documentation uses [this PDF](pdfs/sample_template.pdf) as an example.

## Blank PDFs

=== "Library"
    Use the `BlankPage` class with `PdfWrapper` to create blank PDFs.

    === "Single Page"
        The following example generates a PDF with a single blank page:

        ```python
        from PyPDFForm import BlankPage, PdfWrapper

        blank_pdf = PdfWrapper(BlankPage())

        blank_pdf.write("output.pdf")
        ```
    === "Custom Page Size"
        By default, `BlankPage` creates a letter-size blank page (612 x 792 points, or 8.5 x 11 inches). To change the dimensions, specify `width` and `height` in points:

        ```python
        from PyPDFForm import BlankPage, PdfWrapper

        blank_pdf = PdfWrapper(BlankPage(width=595.35, height=841.995)) # A4 size

        blank_pdf.write("output.pdf")
        ```
    === "Multiple Pages"
        To create a blank PDF with multiple pages, multiply the `BlankPage` object by the number of pages you need:

        ```python
        from PyPDFForm import BlankPage, PdfWrapper

        blank_pdf = PdfWrapper(BlankPage() * 3) # 3 pages of letter size

        blank_pdf.write("output.pdf")
        ```
=== "CLI"
    From the CLI, create blank PDFs with `create blank`:

    === "Single Page"
        ```shell
        pypdfform create blank -o output.pdf
        ```
    === "Custom Page Size"
        ```shell
        pypdfform create blank -o output.pdf \
            --width 595.35 \
            --height 841.995
        ```
    === "Multiple Pages"
        ```shell
        pypdfform create blank -o output.pdf -c 3
        ```

## Extract pages

=== "Library"
    The `PdfWrapper` object has a `.pages` attribute, which is a `PdfArray` containing one `PdfWrapper` object per page:

    ```python
    from PyPDFForm import PdfWrapper

    first_page = PdfWrapper("sample_template.pdf").pages[0]
    first_page.fill(
        {
            "test": "test_1",
            "check": True,
        },
    )

    first_page.write("output.pdf")
    ```
=== "CLI"
    The CLI equivalent is `create extract`:

    ```shell
    pypdfform create extract sample_template.pdf \
        --start 1 \
        --end 1 \
        -o output.pdf
    ```

## Merge multiple PDFs

=== "Library"
    You can merge multiple PDF files by adding their `PdfWrapper` objects together. For example, to merge [this PDF](https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf) and [this PDF](pdfs/sample_template.pdf):

    === "Default Page Order"
        ```python
        from PyPDFForm import PdfWrapper

        pdf_one = PdfWrapper("dummy.pdf")
        pdf_two = PdfWrapper("sample_template.pdf")
        merged = pdf_one + pdf_two

        merged.write("output.pdf")
        ```
    === "Custom Page Order"
        ```python
        from PyPDFForm import PdfWrapper

        pdf_one = PdfWrapper("dummy.pdf")
        pdf_two = PdfWrapper("sample_template.pdf")
        merged = pdf_two.pages[0] + pdf_one + pdf_two.pages[1:]

        merged.write("output.pdf")
        ```
    === "Bulk Merge"
        When merging a large number of PDF files, use the `PdfArray.merge` method for better performance:

        ```python
        from PyPDFForm import PdfArray, PdfWrapper

        pdfs = PdfArray(
            [
                PdfWrapper("dummy.pdf"),
                PdfWrapper("sample_template.pdf"),
                # can get very large
            ]
        )
        merged = pdfs.merge()

        merged.write("output.pdf")
        ```
=== "CLI"
    For CLI merges, pass the input PDFs to `create merge`:

    === "Default Page Order"
        ```shell
        pypdfform create merge dummy.pdf sample_template.pdf -o output.pdf
        ```
    === "Custom Page Order"
        ```shell
        pypdfform create extract sample_template.pdf --start 1 --end 1 -o first_page.pdf
        pypdfform create extract sample_template.pdf --start 2 -o remaining_pages.pdf
        pypdfform create merge first_page.pdf dummy.pdf remaining_pages.pdf -o output.pdf
        ```

## Change PDF version

PyPDFForm allows you to set the PDF version to any supported value up to 2.0:

=== "Library"
    ```python
    from PyPDFForm import PdfWrapper

    new_version = PdfWrapper("sample_template.pdf").change_version("2.0")
    new_version.write("output.pdf")
    ```
=== "CLI"
    From the CLI, set the version with `update version`:

    ```shell
    pypdfform update version sample_template.pdf -v 2.0 -o output.pdf
    ```
