# Other utilities

PyPDFForm offers additional utilities similar to other PDF libraries.

This section of the documentation uses [this PDF](pdfs/sample_template.pdf) as an example.

## Blank PDFs

Use the `BlankPage` class with `PdfWrapper` to create new blank PDFs.

=== "Single Page"
    The following example generates a PDF with a single blank page:

    ```python
    from PyPDFForm import BlankPage, PdfWrapper

    blank_pdf = PdfWrapper(BlankPage())

    blank_pdf.write("output.pdf")
    ```
=== "Custom Resolution"
    By default, `BlankPage` generates a letter-size (612 x 792 points or 8.5 x 11 inches) blank PDF page. To change the dimensions, specify `width` and `height` (in points) when you instantiate the object:

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

## Extract pages

The `PdfWrapper` object has a `.pages` attribute, which is a list of `PdfWrapper` objects representing individual pages:

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

## Merge multiple PDFs

You can merge multiple PDF files by adding their `PdfWrapper` objects. For example, to merge [this PDF](https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf) and [this PDF](pdfs/sample_template.pdf):

=== "Default Page Order"
    ```python
    from PyPDFForm import PdfWrapper

    pdf_one = PdfWrapper("dummy.pdf")
    pdf_two = PdfWrapper("sample_template.pdf")
    merged = pdf_one + pdf_two

    merged.write("output.pdf")
    ```
=== "Rearrange Page Order"
    ```python
    from PyPDFForm import PdfWrapper

    pdf_one = PdfWrapper("dummy.pdf")
    pdf_two = PdfWrapper("sample_template.pdf")
    merged = pdf_two.pages[0] + pdf_one + pdf_two.pages[1:]

    merged.write("output.pdf")
    ```

## Change PDF version

PyPDFForm allows you to modify the PDF version up to 2.0:

```python
from PyPDFForm import PdfWrapper

new_version = PdfWrapper("sample_template.pdf").change_version("2.0")
new_version.write("output.pdf")
```
