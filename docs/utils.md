# Other utilities

PyPDFForm offers additional utilities similar to other PDF libraries.

This section of the documentation will use 
[this PDF](https://github.com/chinapandaman/PyPDFForm/raw/master/pdf_samples/sample_template.pdf) as an example.

## Extract pages

The `PdfWrapper` object has a `.pages` attribute, which is a list of `PdfWrapper` objects representing individual pages.

```python
from PyPDFForm import PdfWrapper

first_page = PdfWrapper("sample_template.pdf").pages[0]
first_page.fill(
    {
        "test": "test_1",
        "check": True,
    },
)

with open("output.pdf", "wb+") as output:
    output.write(first_page.read())
```

## Merge multiple PDFs

Merge multiple PDF files by adding their `PdfWrapper` objects. For an example, see
[this PDF](https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf).

```python
from PyPDFForm import PdfWrapper

pdf_one = PdfWrapper("dummy.pdf")
pdf_two = PdfWrapper("sample_template.pdf")
merged = pdf_one + pdf_two

with open("output.pdf", "wb+") as output:
    output.write(merged.read())
```

To reorganize pages:

```python
from PyPDFForm import PdfWrapper

pdf_one = PdfWrapper("dummy.pdf")
pdf_two = PdfWrapper("sample_template.pdf")
merged = pdf_two.pages[0] + pdf_one + pdf_two.pages[1] + pdf_two.pages[2]

with open("output.pdf", "wb+") as output:
    output.write(merged.read())
```

## Change PDF version

PyPDFForm allows modifying the PDF version up to 2.0:

```python
from PyPDFForm import PdfWrapper

new_version = PdfWrapper("sample_template.pdf").change_version("2.0")

with open("output.pdf", "wb+") as output:
    output.write(new_version.read())
```
